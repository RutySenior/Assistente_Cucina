# graph.py
import os
from langgraph.graph import StateGraph, END
from duckduckgo_search import DDGS
from state import AgentState, RecipeList, KitchenState
from parser import extract_and_merge_data, llm
from search import get_best_recipe_url
from scraper import scrape_recipe_text

# Limite di sicurezza per evitare loop infiniti tra Chef e Critico
MAX_REFLECTION_STEPS = 2

def analyzer_node(state: AgentState):
    user_input = state["messages"][-1]["content"]
    new_ks = extract_and_merge_data(user_input, state["state"])
    # Se abbiamo almeno 2 ingredienti, sblocchiamo la generazione
    if len(new_ks.inventory) >= 2:
        new_ks.missing_info_reason = None
    else:
        # Se ne abbiamo 0 o 1, chiediamo gentilmente di continuare
        if len(new_ks.inventory) == 0:
            new_ks.missing_info_reason = "Ciao! Iniziamo: cosa hai in frigo o in dispensa?"
        else:
            ing_presente = new_ks.inventory[0].name
            new_ks.missing_info_reason = f"Ho segnato {ing_presente}. Cos'altro potremmo aggiungere per fare una ricetta completa?"
            
    return {"state": new_ks}

def generator_node(state: AgentState):
    current_ks = state["state"]
    url = get_best_recipe_url(current_ks)
    context = scrape_recipe_text(url) if url else ""
    
    recipe_gen = llm.with_structured_output(RecipeList)
    prompt = f"""
    Sei uno Chef Stellato. Crea 3 ricette basandoti su: {current_ks.json()}
    
    REGOLE PER IL PROCEDIMENTO:
    1. Per ogni ricetta, il campo 'description' DEVI scrivere un PROCEDIMENTO PROFESSIONALE.
    2. Dividi la spiegazione in fasi chiare (es: 1. Preparazione, 2. Cottura, 3. Impiattamento).
    3. Sii molto dettagliato: spiega come tagliare, quanto scaldare, come capire se è cotto.
    4. Usa un tono incoraggiante ma tecnico.
    
    LINGUA: ITALIANO.
    """
    
    output = recipe_gen.invoke(prompt)
    # Simulazione conteggio token (Groq Free ha limiti bassi)
    current_ks.total_tokens_used += 1500 
    
    for r in output.recipes:
        try:
            with DDGS() as ddgs:
                res = list(ddgs.images(f"{r.search_keywords_en} food dish", max_results=1))
                r.image_url = res[0]['image'] if res else None
        except: r.image_url = None

    current_ks.found_recipes = output.recipes
    return {"state": current_ks}

def critic_node(state: AgentState):
    """L'Agente Critico: verifica se lo Chef ha rispettato i vincoli"""
    current_ks = state["state"]
    # Prompt per la critica
    prompt = f"""
    Sei un critico gastronomico severo. Verifica se queste ricette rispettano i vincoli:
    - ALLERGIE/SALUTE: {current_ks.health_constraints}
    - GUSTI NO: {current_ks.disliked_ingredients}
    - RICETTE: {[r.name for r in current_ks.found_recipes]}
    
    Se le ricette contengono ingredienti vietati, scrivi gli errori. 
    Se sono perfette, scrivi solo 'APPROVATO'.
    """
    critic_res = llm.invoke(prompt).content
    current_ks.total_tokens_used += 500
    
    if "APPROVATO" in critic_res.upper():
        current_ks.critic_feedback = None
    else:
        current_ks.critic_feedback = critic_res
        current_ks.reflection_steps += 1
    return {"state": current_ks}

# --- COSTRUZIONE DEL GRAFO ---
workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("generator", generator_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("analyzer")

def route_after_analyzer(state: AgentState):
    if state["state"].missing_info_reason: return END
    return "generator"

def route_after_critic(state: AgentState):
    # Se approvato o troppi tentativi, finisci. Altrimenti riprova generator.
    if state["state"].critic_feedback is None or state["state"].reflection_steps >= MAX_REFLECTION_STEPS:
        return END
    return "generator"

workflow.add_conditional_edges("analyzer", route_after_analyzer)
workflow.add_edge("generator", "critic")
workflow.add_conditional_edges("critic", route_after_critic)

app = workflow.compile()