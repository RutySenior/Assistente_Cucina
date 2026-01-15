from langgraph.graph import StateGraph, END
from state import AgentState, RecipeList
from parser import extract_and_merge_data, llm
from search import get_best_recipe_url
from scraper import scrape_recipe_text

def analyzer_node(state: AgentState):
    """Estrae dati dal messaggio"""
    new_state = extract_and_merge_data(state["messages"][-1]["content"], state["state"])
    return {"state": new_state}

def generator_node(state: AgentState):
    """Genera 3 ricette basate su fatti reali"""
    current_ks = state["state"]
    url = get_best_recipe_url(current_ks)
    web_text = scrape_recipe_text(url) if url else "Usa la tua conoscenza."
    
    recipe_gen = llm.with_structured_output(RecipeList)
    
    prompt = f"""
    Sei uno Chef. Crea 3 ricette basandoti su: {current_ks.json()}
    Contesto web: {web_text}
    
    Per ogni ricetta DEVI includere:
    - name: Nome piatto
    - prep_time: Tempo (es. 30 min)
    - ingredients: Lista dettagliata con QUANTITÀ (es. 200g pasta)
    - description: Preparazione completa.
    
    RISPONDI IN ITALIANO.
    """
    
    # Invocazione LLM
    output = recipe_gen.invoke(prompt)
    current_ks.found_recipes = output.recipes
    current_ks.missing_info_reason = None # Reset domande
    return {"state": current_ks}

# Configurazione
workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("generator", generator_node)
workflow.set_entry_point("analyzer")

def router(state: AgentState):
    # Se mancano info importanti o ingredienti < 2, chiedi all'utente
    if state["state"].missing_info_reason: return END
    if len(state["state"].inventory) < 2: 
        state["state"].missing_info_reason = "Aggiungi almeno un altro ingrediente per avere una ricetta completa!"
        return END
    return "generator"

workflow.add_conditional_edges("analyzer", router)
workflow.add_edge("generator", END)
app = workflow.compile()