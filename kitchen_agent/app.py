# app.py
import streamlit as st
from graph import app, MAX_REFLECTION_STEPS
from state import KitchenState

st.set_page_config(page_title="Agentic Chef Pro", layout="wide", page_icon="👨‍🍳")

# Budget token per il piano gratuito Groq
TOKEN_LIMIT = 30000 

if "messages" not in st.session_state: st.session_state.messages = []
if "kitchen_state" not in st.session_state: st.session_state.kitchen_state = KitchenState()
res_state = st.session_state.kitchen_state

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

st.title("👨‍🍳 Il tuo Chef Personale con Critico Integrato")

# Ciclo di visualizzazione cronologica
for index, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Se l'ultimo messaggio è dell'assistente e ci sono ricette, mostrale QUI
        if (msg["role"] == "assistant" and 
            index == len(st.session_state.messages) - 1 and 
            res_state.found_recipes):
            
            st.divider()
            st.subheader("🍴 Le mie proposte approvate:")
            tabs = st.tabs([f"Ricetta {i+1}: {r.name}" for i, r in enumerate(res_state.found_recipes)])
            
            for i, tab in enumerate(tabs):
                recipe = res_state.found_recipes[i]
                with tab:
                    if recipe.image_url:
                        st.image(recipe.image_url, use_container_width=True)
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.metric("⏱️ Tempo", recipe.prep_time)
                        st.markdown("**🛒 Ingredienti**")
                        for item in recipe.ingredients:
                            st.write(f"- {item}")
                    with c2:
                        st.markdown("**👨‍🍳 Procedimento Passo-Passo**")
                        st.write(recipe.description)
            
            # Se l'agente ha dovuto riflettere (Agente Critico)
            if res_state.reflection_steps > 0:
                st.caption(f"✨ Ottimizzata in {res_state.reflection_steps} passi dal Critico Gastronomico.")

# --- 4. INPUT UTENTE ---
if prompt := st.chat_input("Cosa hai in frigo?"):
    if res_state.total_tokens_used > TOKEN_LIMIT:
        st.error("Budget token esaurito. Clicca Reset in sidebar.")
    else:
        # Aggiungi messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Lo Chef e il Critico stanno parlando..."):
            try:
                # Esecuzione del Grafo Agentico
                result = app.invoke({
                    "messages": st.session_state.messages, 
                    "state": st.session_state.kitchen_state
                })
                
                # Aggiornamento dello stato sessione
                st.session_state.kitchen_state = result["state"]
                new_state = st.session_state.kitchen_state
                
                # Definizione risposta testo
                if new_state.missing_info_reason:
                    ans = new_state.missing_info_reason
                elif new_state.found_recipes:
                    ans = "Ho trovato 3 ricette che rispettano i tuoi vincoli e le tue scadenze!"
                else:
                    ans = "Capito, dimmi di più!"

                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()

            except Exception as e:
                st.error(f"Errore tecnico Groq: {e}")