import streamlit as st
from graph import app
from state import KitchenState

st.set_page_config(page_title="Chef Agent Pro", layout="wide")
st.title("👨‍🍳 Chef Agent: Ricette Reali in Tempo Reale")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "kitchen_state" not in st.session_state:
    st.session_state.kitchen_state = KitchenState()

# Sidebar
with st.sidebar:
    st.header("🛒 La tua Dispensa")
    for i in st.session_state.kitchen_state.inventory:
        st.write(f"• **{i.name}** ({i.quantity})")
    if st.session_state.kitchen_state.health_constraints:
        st.error(f"Vincoli: {', '.join(st.session_state.kitchen_state.health_constraints)}")

# Chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ho della pasta e del guanciale..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.spinner("Sto leggendo le ricette dai siti web..."):
        result = app.invoke({"messages": st.session_state.messages, "state": st.session_state.kitchen_state})
        st.session_state.kitchen_state = result["state"]
        
        if result["state"].missing_info_reason:
            ans = result["state"].missing_info_reason
        elif result["state"].found_recipes:
            ans = result["state"].found_recipes[0]
        else:
            ans = "Dimmi di più sugli ingredienti!"

    st.chat_message("assistant").write(ans)
    st.session_state.messages.append({"role": "assistant", "content": ans})
    st.rerun()