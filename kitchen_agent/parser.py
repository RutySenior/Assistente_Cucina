# parser.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

load_dotenv()
# Esportiamo llm per usarlo negli altri file
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

def extract_and_merge_data(user_input: str, current_state: KitchenState) -> KitchenState:
    structured_llm = llm.with_structured_output(KitchenState)
    
    prompt = f"""
    Sei un assistente di cucina meticoloso. Analizza il messaggio: "{user_input}"
    Stato attuale: {current_state.json()}

    ISTRUZIONI CRUCIALI:
    1. INVENTARIO: Se l'utente dice di avere un ingrediente (es. "ho dei gamberi"), inseriscilo SEMPRE in 'inventory'.
    2. ALLERGIE: Se l'utente dice "non usarli perché sono allergico", NON spostare l'ingrediente dall'inventario, ma aggiungi il nome dell'ingrediente o della categoria in 'health_constraints'.
    3. DISGUSTI: Se dice "odio la cipolla", aggiungi cipolla a 'disliked_ingredients'.
    4. RAGIONAMENTO: Se ho un ingrediente in frigo ma sono allergico, l'agente deve sapere che l'ingrediente C'È, ma deve ESCLUDERLO dalla ricetta finale.

    Rispondi in ITALIANO.
    """
    return structured_llm.invoke(prompt)