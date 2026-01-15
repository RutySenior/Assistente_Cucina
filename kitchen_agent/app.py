import streamlit as st
from graph import app
from state import KitchenState

st.set_page_config(page_title="Chef Agent AI", page_icon="👨‍🍳", layout="wide")

# 1. Inizializzazione Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kitchen_state" not in st.session_state:
    st.session_state.kitchen_state = KitchenState()

# --- SIDEBAR (Sempre fissa a sinistra) ---
with st.sidebar:
    st.header("🔍 Stato Agente")
    ks = st.session_state.kitchen_state

    # 1. DISPENSA
    st.subheader("📦 Dispensa")
    for i in ks.inventory:
        status = "⏰" if i.is_expiring else "🟢"
        st.write(f"{status} **{i.name}** ({i.quantity})")

    # 2. GUSTI (Dislikes)
    if ks.disliked_ingredients:
        st.markdown("---")
        st.subheader("🚫 Gusti No")
        for item in ks.disliked_ingredients:
            st.warning(f"Senza: {item}")

    # 3. SALUTE (Constraints)
    if ks.health_constraints:
        st.markdown("---")
        st.subheader("⚕️ Salute & Allergie")
        for item in ks.health_constraints:
            st.error(f"Vincolo: {item}")

    # 4. PREFERENZE (Likes)
    if ks.preferences:
        st.markdown("---")
        st.subheader("😋 Preferenze")
        for item in ks.preferences:
            st.success(f"Gusto: {item}")

    if st.button("Reset Totale"):
        st.session_state.kitchen_state = KitchenState()
        st.session_state.messages = []
        st.rerun()

st.title("👨‍🍳 Il tuo Chef Personale")

# --- 2. CICLO DI VISUALIZZAZIONE CHAT (Cronologico) ---
# Usiamo un indice per sapere se siamo all'ultimo messaggio
for index, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Mostra le ricette solo se siamo all'ultimo messaggio dell'assistente
        if (msg["role"] == "assistant" and 
            index == len(st.session_state.messages) - 1 and 
            st.session_state.kitchen_state.found_recipes):
            
            st.write("---")
            tabs = st.tabs([f"🍴 {r.name}" for r in st.session_state.kitchen_state.found_recipes])
            
            for i, tab in enumerate(tabs):
                recipe = st.session_state.kitchen_state.found_recipes[i]
                with tab:
                    # Immagine reale recuperata dal tool
                    if recipe.image_url:
                        st.image(recipe.image_url, use_container_width=True)
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.info(f"⏱️ **Tempo:** {recipe.prep_time}")
                        st.markdown("**🛒 Ingredienti (Dosi per 2):**")
                        for item in recipe.ingredients:
                            st.write(f"- {item}")
                    with c2:
                        st.markdown("**👨‍🍳 Preparazione Passo-Passo**")
                        st.write(recipe.description)

# --- 3. INPUT UTENTE (Sempre in fondo) ---
if prompt := st.chat_input("Scrivi qui cosa hai in cucina..."):
    # Aggiungi messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Lo Chef sta pensando..."):
        # Esecuzione Grafo
        result = app.invoke({
            "messages": st.session_state.messages, 
            "state": st.session_state.kitchen_state
        })
        
        # Aggiorna lo stato
        st.session_state.kitchen_state = result["state"]
        new_ks = st.session_state.kitchen_state
        
        # Determina la risposta testuale
        if new_ks.found_recipes:
            ans = "Ho trovato delle ricette basate su quello che mi hai detto. Ecco le opzioni:"
        elif new_ks.missing_info_reason:
            ans = new_ks.missing_info_reason
        else:
            ans = "Ho capito, cos'altro hai a disposizione?"

        # Aggiungi risposta assistente
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()