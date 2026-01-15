from langgraph.graph import StateGraph, END
from state import AgentState, KitchenState
from parser import extract_kitchen_data
from search import find_recipes_online

def parse_input_node(state: AgentState):
    user_msg = state["messages"][-1]["content"]
    new_kitchen_state = extract_kitchen_data(user_msg, state["state"])
    return {"state": new_kitchen_state}

def recipe_search_node(state: AgentState):
    recipes = find_recipes_online(state["state"].ingredients, state["state"].preferences)
    updated_state = state["state"]
    updated_state.found_recipes = [recipes]
    return {"state": updated_state}

# Costruzione del Grafo
workflow = StateGraph(AgentState)
workflow.add_node("parser", parse_input_node)
workflow.add_node("search", recipe_search_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser", "search") # Semplificato per l'esempio
workflow.add_edge("search", END)

app = workflow.compile()