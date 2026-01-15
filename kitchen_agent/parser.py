import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

load_dotenv()
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

def extract_and_merge_data(user_input: str, current_state: KitchenState) -> KitchenState:
    structured_llm = llm.with_structured_output(KitchenState)
    prompt = f"""
    Sei un assistente di cucina esperto. Aggiorna lo stato attuale con le nuove informazioni fornite dall'utente.
    LINGUA: Rispondi sempre ed esclusivamente in ITALIANO.
    
    STATO ATTUALE: {current_state.json()}
    MESSAGGIO UTENTE: "{user_input}"
    
    ISTRUZIONI:
    1. Aggiorna ingredienti, quantità e scadenze.
    2. Registra gusti negativi e vincoli di salute.
    3. Se l'utente è vago o mancano dati cruciali per una ricetta, spiega cosa manca in 'missing_info_reason'.
    4. Non cancellare dati esistenti se non richiesto.
    """
    return structured_llm.invoke(prompt)