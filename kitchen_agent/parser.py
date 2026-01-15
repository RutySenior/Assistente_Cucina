# parser.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

def extract_and_merge_data(user_input: str, current_state: KitchenState) -> KitchenState:
    structured_llm = llm.with_structured_output(KitchenState)
    prompt = f"""
    Sei un assistente di cucina. Aggiorna lo stato in base al messaggio: "{user_input}"
    Stato attuale: {current_state.json()}

    REGOLE:
    1. 'disliked_ingredients': se l'utente dice "non mi piace", "odio", "senza X".
    2. 'health_constraints': allergie, celiachia, "poco sale", "dieta".
    3. 'preferences': gusti positivi (es. "mi piace il piccante").
    4. 'inventory': ingredienti presenti e scadenze (is_expiring se dice "scade oggi/domani").
    """
    return structured_llm.invoke(prompt)