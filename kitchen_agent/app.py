import streamlit as st
from graph import app
from state import KitchenState

# Configurazione della pagina
st.set_page_config(page_title="Chef Agent AI", page_icon="👨‍🍳", layout="wide")

# Inizializzazione Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "kitchen_state" not in st.session_state:
    st.session_state.kitchen_state = KitchenState()

# --- SIDEBAR DI ISPEZIONE ---
with st.sidebar:
    st.header("🔍 Monitor della Dispensa")
    st.info("Dati estratti dall'AI in tempo reale")
    
    if st.session_state.kitchen_state.inventory:
        st.subheader("📦 Ingredienti rilevati")
        for ing in st.session_state.kitchen_state.inventory:
            icon = "⚠️" if ing.is_expiring else "🟢"
            st.write(f"{icon} **{ing.name}**")
            st.caption(f"Quantità: {ing.quantity}")
    
    if st.session_state.kitchen_state.health_constraints:
        st.markdown("---")
        st.subheader("❤️ Vincoli Salute")
        st.error(", ".join(st.session_state.kitchen_state.health_constraints))

    if st.button("Svuota tutto (Reset)"):
        st.session_state.messages = []
        st.session_state.kitchen_state = KitchenState()
        st.rerun()

st.title("👨‍🍳 Il tuo Chef Personale Agentico")

# --- 1. VISUALIZZAZIONE DELLA CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 2. VISUALIZZAZIONE DELLE 3 RICETTE ---
# Mostriamo le ricette in primo piano se sono state generate
res_state = st.session_state.kitchen_state
if res_state.found_recipes:
    st.markdown("---")
    st.subheader("🍴 Le 3 Proposte dello Chef")
    
    # Crea i tab con i nomi delle ricette
    tabs = st.tabs([r.name for r in res_state.found_recipes])
    
    for i, tab in enumerate(tabs):
        recipe = res_state.found_recipes[i]
        with tab:
            # Definizione colonne: colonna 1 per dettagli, colonna 2 per preparazione
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.info(f"⏱️ **Tempo:** {recipe.prep_time}")
                st.write("**🛒 Ingredienti e Quantità:**")
                for item in recipe.ingredients:
                    st.write(f"- {item}")
            
            with col2:
                st.write("**👨‍🍳 Preparazione Passo-Passo:**")
                st.write(recipe.description)
    st.markdown("---")

# --- 3. INPUT UTENTE ---
if prompt := st.chat_input("Esempio: Ho 500g di pasta e del guanciale..."):
    # Salva il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Lo Chef sta analizzando i dati e cercando ricette..."):
        # Eseguiamo il grafo agentico
        try:
            result = app.invoke({
                "messages": st.session_state.messages, 
                "state": st.session_state.kitchen_state
            })
            
            # Aggiorniamo lo stato globale
            st.session_state.kitchen_state = result["state"]
            
            # Determiniamo la risposta testuale dell'assistente
            if result["state"].found_recipes:
                ans = "Ottimo! Ho trovato 3 ricette complete per te. Guarda le schede qui sopra 👆"
            elif result["state"].missing_info_reason:
                ans = result["state"].missing_info_reason
            else:
                ans = "Ho capito. Cos'altro hai a disposizione o quali sono le tue preferenze?"

            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.rerun()
            
        except Exception as e:
            st.error(f"Errore nel sistema: {e}")