# parser.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

# 1. Carica le variabili dal file .env immediatamente
load_dotenv()

# 2. Recupera la chiave dall'ambiente
api_key = os.getenv("GROQ_API_KEY")

# 3. Controllo di sicurezza: se la chiave manca, ferma tutto con un messaggio chiaro
if not api_key:
    raise ValueError("ERRORE: La chiave GROQ_API_KEY non è stata trovata nel file .env")

# 4. Inizializza il modello passandogli esplicitamente la chiave
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=api_key, # Usa il nome corretto del parametro: groq_api_key
    temperature=0
)

def extract_and_merge_data(user_input: str, current_state: KitchenState) -> KitchenState:
    structured_llm = llm.with_structured_output(KitchenState)
    
    # Passiamo lo stato attuale come JSON per farlo "leggere" all'LLM
    prompt = f"""
    Sei un assistente di cucina. Il tuo compito è AGGIORNARE lo stato attuale senza perdere dati.
    
    STATO ATTUALE (Dati già salvati): 
    {current_state.json()}
    
    NUOVO MESSAGGIO UTENTE: 
    "{user_input}"
    
    ISTRUZIONI:
    1. Prendi la lista 'inventory' dallo stato attuale.
    2. Se l'utente aggiunge nuovi ingredienti, AGGIUNGILI alla lista.
    3. Se l'utente specifica la quantità per un ingrediente che era già presente (era 'sconosciuta'), AGGIORNA quel campo.
    4. Se l'utente parla di allergie o gusti, aggiorna 'health_constraints' e 'disliked_ingredients'.
    5. NON cancellare mai gli ingredienti già presenti nello stato attuale.
    
    Rispondi in ITALIANO.
    """
    return structured_llm.invoke(prompt)