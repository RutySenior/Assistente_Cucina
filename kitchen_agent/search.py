# search.py
from typing import Optional, List  # <--- AGGIUNGI QUESTO
from langchain_community.tools import DuckDuckGoSearchResults
from state import KitchenState
import re

search_tool = DuckDuckGoSearchResults()

def get_best_recipe_url(state: KitchenState) -> Optional[str]:
    # Cerchiamo ricette specifiche in base all'inventario
    ing_list = [i.name for i in state.inventory]
    query = f"ricetta originale italiana con {', '.join(ing_list)}"
    results = search_tool.run(query)
    
    # Estrae il primo link valido
    links = re.findall(r"https?://[^\s,\]]+", results)
    return links[0] if links else None