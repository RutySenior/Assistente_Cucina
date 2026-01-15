from langgraph.graph import StateGraph, END
from state import AgentState, RecipeList
from parser import extract_and_merge_data, llm
from search import get_best_recipe_url
from scraper import scrape_recipe_text
from duckduckgo_search import DDGS # Nuova libreria per immagini reali

def analyzer_node(state: AgentState):
    user_input = state["messages"][-1]["content"]
    new_ks = extract_and_merge_data(user_input, state["state"])
    
    # Controllo progressivo
    vague = [i.name for i in new_ks.inventory if i.quantity == "sconosciuta"]
    if vague:
        new_ks.missing_info_reason = f"Ho segnato {', '.join(vague)}. Mi diresti le quantità?"
    elif len(new_ks.inventory) < 2:
        new_ks.missing_info_reason = "Aggiungi un altro ingrediente per avere una ricetta!"
    else:
        new_ks.missing_info_reason = None
    return {"state": new_ks}

def get_real_image(query):
    """Cerca una foto reale su DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            # Cerchiamo solo su siti di cucina per evitare gatti o rumore
            results = list(ddgs.images(f"{query} food dish recipe", max_results=1))
            if results:
                return results[0]['image']
    except:
        return None
    return "https://via.placeholder.com/800x600.png?text=Immagine+non+disponibile"

def generator_node(state: AgentState):
    current_ks = state["state"]
    url = get_best_recipe_url(current_ks)
    context = scrape_recipe_text(url) if url else ""
    
    recipe_gen = llm.with_structured_output(RecipeList)
    
    # PROMPT AGGRESSIVO PER LE QUANTITÀ
    prompt = f"""
    Sei uno Chef. Crea 3 ricette basandoti su: {current_ks.json()}
    Contesto web: {context}
    
    REGOLE OBBLIGATORIE:
    1. QUANTITÀ: Per ogni singolo ingrediente DEVI inventare una quantità realistica per 2 persone (es: '200g di spaghetti', '1 spicchio d'aglio', '60g di pecorino'). 
       NON SCRIVERE MAI 'quantità sconosciuta' o 'a piacere'.
    2. NOME INGLESE: In 'search_keywords_en' scrivi solo il nome del piatto in inglese.
    
    Rispondi in ITALIANO.
    """
    
    try:
        output = recipe_gen.invoke(prompt)
        
        for r in output.recipes:
            # Cerchiamo un'immagine reale per ogni ricetta
            real_img = get_real_image(r.search_keywords_en)
            r.image_url = real_img
        
        current_ks.found_recipes = output.recipes
        current_ks.missing_info_reason = None 
    except Exception as e:
        print(f"Errore: {e}")
        
    return {"state": current_ks}

workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("generator", generator_node)
workflow.set_entry_point("analyzer")

def router(state: AgentState):
    if state["state"].missing_info_reason: return END
    return "generator"

workflow.add_conditional_edges("analyzer", router)
workflow.add_edge("generator", END)
app = workflow.compile()