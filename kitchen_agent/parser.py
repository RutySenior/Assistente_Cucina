import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state import KitchenState

load_dotenv()
# Definiamo LLM qui in modo che sia accessibile a tutti
llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=os.getenv("GROQ_API_KEY"))

def extract_and_merge_data(user_input: str, current_state: KitchenState) -> KitchenState:
    structured_llm = llm.with_structured_output(KitchenState)
    prompt = f"""
    Aggiorna lo stato della cucina in base al messaggio dell'utente. 
    Linguaggio: ITALIANO.
    Stato attuale: {current_state.json()}
    Messaggio: "{user_input}"
    """
    return structured_llm.invoke(prompt)