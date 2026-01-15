from langgraph.graph import StateGraph, END
from state import AgentState
from parser import extract_and_merge_data, llm # Importiamo anche llm
from search import get_best_recipe_url
from scraper import scrape_recipe_text

def analyzer_node(state: AgentState):
    new_state = extract_and_merge_data(state["messages"][-1]["content"], state["state"])
    return {"state": new_state}

def search_and_scrape_node(state: AgentState):
    current_ks = state["state"]
    # Cerchiamo solo se non ci sono dubbi e abbiamo almeno 2 ingredienti
    if not current_ks.missing_info_reason and len(current_ks.inventory) >= 2:
        url = get_best_recipe_url(current_ks)
        if url:
            raw_text = scrape_recipe_text(url)
            # Chiediamo all'LLM di pulire il testo grezzo (Refinement)
            prompt = f"Estrai solo la ricetta (ingredienti e passaggi) da questo testo disordinato:\n\n{raw_text}"
            clean_recipe = llm.invoke(prompt).content
            current_ks.found_recipes = [clean_recipe]
    return {"state": current_ks}

workflow = StateGraph(AgentState)
workflow.add_node("analyzer", analyzer_node)
workflow.add_node("search_scrape", search_and_scrape_node)

workflow.set_entry_point("analyzer")

def router(state: AgentState):
    if state["state"].missing_info_reason:
        return END
    return "search_scrape"

workflow.add_conditional_edges("analyzer", router)
workflow.add_edge("search_scrape", END)
app = workflow.compile()