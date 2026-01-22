# app.py
import streamlit as st
from graph import app, MAX_REFLECTION_STEPS
from state import KitchenState

st.set_page_config(page_title="Agentic Chef Pro", layout="wide", page_icon="👨‍🍳")

# Budget token per il piano gratuito Groq
TOKEN_LIMIT = 30000 

if "messages" not in st.session_state: st.session_state.messages = []
if "kitchen_state" not in st.session_state: st.session_state.kitchen_state = KitchenState()

# --- SIDEBAR: MONITOR RISORSE ---
with st.sidebar:
    st.header("📊 Sistema & Risorse")
    used_tokens = st.session_state.kitchen_state.total_tokens_used
    
    # Barra dei token
    col1, col2 = st.columns(2)
    col1.metric("Token Usati", used_tokens)
    col2.metric("Limite", TOKEN_LIMIT)
    st.progress(min(used_tokens / TOKEN_LIMIT, 1.0))
    
    if used_tokens > TOKEN_LIMIT:
        st.error("🛑 LIMITE TOKEN RAGGIUNTO. Reset necessario.")
    elif used_tokens > TOKEN_LIMIT * 0.8:
        st.warning("⚠️ Attenzione: Risorse quasi esaurite.")

    st.divider()
    st.subheader("🛒 Stato Dispensa")
    ks = st.session_state.kitchen_state
    for i in ks.inventory:
        st.write(f"• **{i.name}** ({i.quantity})")
    
    if st.button("Reset Sessione"):
        st.session_state.messages = []
        st.session_state.kitchen_state = KitchenState()
        st.rerun()

# --- CHAT DISPLAY ---
st.title("👨‍🍳 Chef Agent con Controllo Qualità")

for index, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Se l'ultimo messaggio è dello chef e ci sono ricette, mostrale
        if msg["role"] == "assistant" and index == len(st.session_state.messages)-1:
            if st.session_state.kitchen_state.found_recipes:
                tabs = st.tabs([f"🍴 {r.name}" for r in st.session_state.kitchen_state.found_recipes])
                for i, tab in enumerate(tabs):
                    r = st.session_state.kitchen_state.found_recipes[i]
                    with tab:
                        if r.image_url: st.image(r.image_url, use_container_width=True)
                        st.info(f"Tempo: {r.prep_time} | {r.search_keywords_en}")
                        st.write(r.description)

# --- CHAT INPUT ---
if prompt := st.chat_input("Scrivi qui..."):
    # Controllo preventivo token
    if st.session_state.kitchen_state.total_tokens_used > TOKEN_LIMIT:
        st.error("Non posso processare la richiesta: limite token superato.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("L'Agente Chef e il Critico stanno lavorando..."):
            try:
                # Invocazione Grafo
                result = app.invoke({
                    "messages": st.session_state.messages,
                    "state": st.session_state.kitchen_state
                })
                
                st.session_state.kitchen_state = result["state"]
                res = st.session_state.kitchen_state
                
                # Messaggio di risposta
                if res.missing_info_reason:
                    ans = res.missing_info_reason
                elif res.critic_feedback:
                    ans = "Ho provato a generare le ricette ma il Critico ha trovato dei problemi. Ecco il meglio che sono riuscito a fare."
                else:
                    ans = "Ecco 3 ricette approvate dal Critico Gastronomico!"

                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except Exception as e:
                st.error(f"Errore tecnico: {e}")