# scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_recipe_text(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=' ')[:4000]
    except:
        return ""