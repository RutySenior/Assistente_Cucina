from langchain_community.tools import DuckDuckGoSearchResults
import re
from typing import Optional
from state import KitchenState

search_tool = DuckDuckGoSearchResults()

def get_best_recipe_url(state: KitchenState) -> Optional[str]:
    # Crea una query basata sugli ingredienti presenti
    ing_names = [i.name for i in state.inventory]
    query = f"ricetta italiana originale con {', '.join(ing_names)}"
    
    # Aggiunge esclusioni se presenti
    if state.disliked_ingredients:
        query += " senza " + " ".join(state.disliked_ingredients)
    
    results = search_tool.run(query)
    # Estrae il primo URL valido
    links = re.findall(r"https?://[^\s,\]]+", results)
    return links[0] if links else None