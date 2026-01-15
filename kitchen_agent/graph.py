# graph.py
from langgraph.graph import StateGraph, END
from state import AgentState, RecipeList
from parser import extract_and_merge_data, llm  # llm viene da qui
from search import get_best_recipe_url         # get_best_recipe_url viene da qui
from scraper import scrape_recipe_text        # scrape_recipe_text viene da qui

# --- NODO 1: ANALIZZATORE ---
def analyzer_node(state: AgentState):
    """Estrae dati dal messaggio utente e decide se mancano info"""
    user_input = state["messages"][-1]["content"]
    # Aggiorna lo stato (ingredienti, scadenze, gusti)
    new_ks = extract_and_merge_data(user_input, state["state"])
    
    # Logica di controllo per la raccolta progressiva
    vague_items = [i.name for i in new_ks.inventory if i.quantity == "sconosciuta"]
    
    if len(new_ks.inventory) < 1:
        new_ks.missing_info_reason = "Ciao! Dimmi cosa hai in cucina per iniziare."
    elif vague_items:
        new_ks.missing_info_reason = f"Ho segnato {', '.join(vague_items)}. Potresti dirmi le quantità approssimative?"
    elif len(new_ks.inventory) < 2:
        new_ks.missing_info_reason = "Ho bisogno di almeno un altro ingrediente per suggerirti una ricetta completa."
    else:
        new_ks.missing_info_reason = None # Tutto pronto per cucinare!
        
    return {"state": new_ks}

# --- NODO 2: GENERATORE (Quello che hai chiesto) ---
def generator_node(state: AgentState):
    """Cerca sul web, legge i siti e genera 3 ricette complete"""
    current_ks = state["state"]
    
    # 1. Trova il link migliore
    url = get_best_recipe_url(current_ks)
    
    # 2. Legge il contenuto del sito (Scraping)
    context = scrape_recipe_text(url) if url else "Usa la tua conoscenza gastronomica."
    
    # 3. Generazione strutturata delle 3 ricette
    recipe_gen = llm.with_structured_output(RecipeList)
    
    prompt = f"""
    Sei uno Chef stellato. Crea 3 ricette basandoti su: {current_ks.json()}
    Contesto web reale: {context}
    
    Per ogni ricetta specifica:
    - Nome del piatto
    - Tempo di preparazione
    - Ingredienti con QUANTITÀ precise
    - Descrizione passo-passo
    
    Rispondi in ITALIANO.
    """
    
    try:
        output = recipe_gen.invoke(prompt)
        current_ks.found_recipes = output.recipes
        current_ks.missing_info_reason = None # Reset domande perché abbiamo finito
    except Exception as e:
        print(f"Errore generazione: {e}")
        
    return {"state": current_ks}

# --- CONFIGURAZIONE DEL GRAFO (Workflow) ---
workflow = StateGraph(AgentState)

# Aggiungiamo i nodi definiti sopra
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("generator", generator_node)

# Impostiamo l'entrata
workflow.set_entry_point("analyzer")

# Definiamo il Router (chi decide dove andare dopo l'analisi)
def router(state: AgentState):
    # Se analyzer ha impostato un motivo di blocco, ci fermiamo e rispondiamo all'utente
    if state["state"].missing_info_reason:
        return END
    # Altrimenti, se tutto è ok, andiamo a generare le ricette
    return "generator"

# Colleghiamo i nodi
workflow.add_conditional_edges("analyzer", router)
workflow.add_edge("generator", END)

# Esportiamo l'app compilata per app.py
app = workflow.compile()