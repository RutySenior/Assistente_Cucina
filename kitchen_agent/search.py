# search.py
from typing import List # <--- Aggiungi questa riga
from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

def find_recipes_online(ingredients: List[str], preferences: List[str]) -> str:
    query = f"ricette facili con {', '.join(ingredients)} {' '.join(preferences)}"
    results = search_tool.run(query)
    return results