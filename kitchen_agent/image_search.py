# image_search.py
from typing import Optional  # <--- AGGIUNGI QUESTA RIGA

def search_recipe_image(query: str) -> Optional[str]:
    """Cerca un'immagine del piatto finale"""
    try:
        # In un ambiente di produzione useresti l'API di Google Custom Search o Bing.
        # Qui usiamo un generatore di immagini basato su parole chiave per il test.
        clean_query = query.replace(" ", ",")
        return f"https://source.unsplash.com/800x600/?cooking,{clean_query}"
    except Exception:
        return None