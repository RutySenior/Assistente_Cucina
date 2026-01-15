# parser.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

# Carica le variabili dal file .env
load_dotenv()

# Prendi la chiave dall'ambiente
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("ERRORE: La GROQ_API_KEY non è stata trovata. Controlla il file .env")

# Inizializza il modello passando esplicitamente la chiave
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=api_key  # <--- Passaggio esplicito
)

def extract_kitchen_data(user_input: str, current_state: KitchenState) -> KitchenState:
    # Utilizziamo il metodo with_structured_output come suggerito da Huyen
    structured_llm = llm.with_structured_output(KitchenState)
    
    prompt = f"""
    Sei un assistente esperto di cucina. 
    Analizza il messaggio: "{user_input}"
    Aggiorna lo stato attuale degli ingredienti e delle preferenze: {current_state.dict()}
    Restituisci l'oggetto KitchenState aggiornato.
    """
    
    return structured_llm.invoke(prompt)