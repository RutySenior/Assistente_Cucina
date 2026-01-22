# app.py
import streamlit as st
from graph import app, MAX_REFLECTION_STEPS
from state import KitchenState

st.set_page_config(page_title="Agentic Chef Pro", layout="wide", page_icon="👨‍🍳")

# Budget token per il piano gratuito Groq
TOKEN_LIMIT = 30000 

if "messages" not in st.session_state: st.session_state.messages = []
if "kitchen_state" not in st.session_state: st.session_state.kitchen_state = KitchenState()

# --- SIDEBAR DI ISPEZIONE COMPLETA ---
with st.sidebar:
    st.header("🔍 Monitor Stato Agente")
    ks = st.session_state.kitchen_state

    # 1. MONITOR TOKEN (Requisito Gestione Risorse)
    st.subheader("📊 Risorse")
    col1, col2 = st.columns(2)
    col1.metric("Token", ks.total_tokens_used)
    col2.metric("Passi", ks.reflection_steps)
    st.progress(min(ks.total_tokens_used / TOKEN_LIMIT, 1.0))
    
    st.divider()

    # 2. DISPENSA (Ingredienti e Scadenze)
    st.subheader("📦 Dispensa")
    if ks.inventory:
        for i in ks.inventory:
            icon = "⏰" if i.is_expiring else "🟢"
            st.write(f"{icon} **{i.name}**")
            st.caption(f"Quantità: {i.quantity}")
    else:
        st.write("Dispensa vuota.")

    # 3. GUSTI E PREFERENZE (Preferences - In Verde)
    if ks.preferences:
        st.divider()
        st.subheader("😋 Preferenze")
        for pref in ks.preferences:
            st.success(f"Gusto: {pref}")

    # 4. GUSTI "NO" (Disliked - In Giallo)
    if ks.disliked_ingredients:
        st.divider()
        st.subheader("🚫 Gusti No")
        for dislike in ks.disliked_ingredients:
            st.warning(f"Senza: {dislike}")

    # 5. VINCOLI SALUTE E ALLERGIE (Health - In Rosso)
    if ks.health_constraints:
        st.divider()
        st.subheader("⚕️ Salute & Allergie")
        for constraint in ks.health_constraints:
            st.error(f"Vincolo: {constraint}")

    # 6. RESET
    st.divider()
    if st.button("Svuota tutto (Reset)"):
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