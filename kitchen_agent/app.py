import streamlit as st
from graph import app
from state import KitchenState

st.set_page_config(page_title="AI Kitchen Agent", layout="wide")

st.title("👨‍🍳 Assistente di Cucina Agentico")
st.sidebar.header("🔍 Stato Interno dell'Agente")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.kitchen_state = KitchenState()

# Visualizzazione Stato nella Sidebar
st.sidebar.write("Ingredienti rilevati:", st.session_state.kitchen_state.ingredients)
st.sidebar.write("Preferenze:", st.session_state.kitchen_state.preferences)

# Chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Cosa hai in cucina?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Esecuzione Agente
    inputs = {"messages": st.session_state.messages, "state": st.session_state.kitchen_state}
    config = {"configurable": {"thread_id": "1"}}
    
    # L'agente lavora...
    output = app.invoke(inputs, config)
    
    # Aggiorna UI
    st.session_state.kitchen_state = output["state"]
    ans = f"Ho trovato queste idee per te basandomi su {output['state'].ingredients}: \n\n {output['state'].found_recipes[0]}"
    
    st.chat_message("assistant").write(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.rerun()