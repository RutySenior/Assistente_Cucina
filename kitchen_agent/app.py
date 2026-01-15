# app.py
import streamlit as st
from graph import app
from state import KitchenState

st.set_page_config(page_title="Chef Agent AI", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "kitchen_state" not in st.session_state:
    st.session_state.kitchen_state = KitchenState()

# Sidebar
with st.sidebar:
    st.header("🔍 Monitor Stato Agente")
    res_state = st.session_state.kitchen_state

    # --- SEZIONE INVENTARIO ---
    st.subheader("📦 Dispensa")
    if res_state.inventory:
        for ing in res_state.inventory:
            icon = "⏰" if ing.is_expiring else "🟢"
            st.write(f"{icon} **{ing.name}** ({ing.quantity})")
    else:
        st.caption("Nessun ingrediente.")

    # --- SEZIONE GUSTI (DISLIKED) ---
    if res_state.disliked_ingredients:
        st.markdown("---")
        st.subheader("🚫 Gusti No")
        for item in res_state.disliked_ingredients:
            st.warning(f"**{item}**") # Giallo per i gusti negativi

    # --- SEZIONE SALUTE & ALLERGIE (HEALTH) ---
    if res_state.health_constraints:
        st.markdown("---")
        st.subheader("⚕️ Salute & Allergie")
        for item in res_state.health_constraints:
            st.error(f"**{item}**") # Rosso per vincoli di salute/allergie

    # --- SEZIONE PREFERENZE (POSITIVE) ---
    if res_state.preferences:
        st.markdown("---")
        st.subheader("😋 Preferenze")
        for item in res_state.preferences:
            st.success(f"**{item}**") # Verde per preferenze positive

    st.markdown("---")
    if st.button("Reset Totale"):
        st.session_state.kitchen_state = KitchenState()
        st.session_state.messages = []
        st.rerun()

st.title("👨‍Chef Agent: Ricette Intelligenti")

# Chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Visualizzazione Ricette
res_state = st.session_state.kitchen_state # Definiamo res_state prima dell'uso
if res_state.found_recipes:
    st.divider()
    tabs = st.tabs([r.name for r in res_state.found_recipes])
    for i, tab in enumerate(tabs):
        r = res_state.found_recipes[i]
        with tab:
            if r.image_url: st.image(r.image_url, width=400)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.info(f"Tempo: {r.prep_time}")
                st.write("**Ingredienti:**")
                for ing in r.ingredients: st.write(f"- {ing}")
            with col2:
                st.write("**Preparazione:**")
                st.write(r.description)

# app.py (Sezione di gestione dell'input)
if prompt := st.chat_input("Cosa hai in cucina?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Esecuzione Grafo
    try:
        result = app.invoke({
            "messages": st.session_state.messages, 
            "state": st.session_state.kitchen_state
        })
        
        # Aggiorna lo stato globale
        st.session_state.kitchen_state = result["state"]
        new_ks = st.session_state.kitchen_state
        
        # DEFINIZIONE DELLA RISPOSTA
        if new_ks.missing_info_reason:
            # Se l'agente ha una domanda, usiamola come risposta
            response = new_ks.missing_info_reason
        elif new_ks.found_recipes:
            response = "Ho trovato delle ottime ricette! Guarda le schede sotto la chat."
        else:
            response = "Ho capito, cos'altro hai?"

        # AGGIUNGIAMO LA RISPOSTA ALLA CRONOLOGIA
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    except Exception as e:
        st.error(f"Errore: {e}")