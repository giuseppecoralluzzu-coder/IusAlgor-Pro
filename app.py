import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA E STILE ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

st.title("⚖️ IusAlgor Pro")
st.markdown("##### *Audit di Conformità Legale per Sistemi di Intelligenza Artificiale*")

# --- 2. GESTIONE API KEY (SEGRETA) ---
# Cerchiamo la chiave nei Secrets di Streamlit o nella sidebar come backup
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    with st.sidebar:
        api_key = st.text_input("Inserisci Gemini API Key", type="password")

# --- 3. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo.png"):
        image = Image.open('logo.png')
        st.image(image, width=250) 
    
    st.header("Console di Controllo")
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documentazione Tecnica", type=['pdf', 'txt'])
    st.markdown("---")
    livello_dettaglio = st.select_slider(
        "Dettaglio Analisi:",
        options=["Riassuntiva", "Completa"],
        value="Completa"
    )

# --- 4. LOGICA DEL CHATBOT ---
if api_key:
    genai.configure(api_key=api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Digita qui la tua richiesta..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if uploaded_file is not None:
                ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                
                with st.spinner('Analisi in corso...'):
                    g_file = genai.upload_file(tmp_path)
                    is_first_msg = len(st.session_state.messages) <= 1
                    
                    if is_first_msg:
                        if livello_dettaglio == "Completa":
                            sys_instr = "Sei IusAlgor Pro. Analizza il file e rispondi con: 🎯 AMBITI INTACCATI, ⚠️ RISCHI PRINCIPALI, 💡 AZIONI CORRETTIVE, ❓ Q&A."
                        else:
                            sys_instr = "Sei IusAlgor Pro. Dai un verdetto sintetico di max 5 righe."
                    else:
                        sys_instr = "Sei IusAlgor Pro. Rispondi in modo colloquiale come un consulente umano."

                    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                    
                    history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history)
                    response = chat.send_message([g_file, prompt])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                os.remove(tmp_path)
            else:
                st.warning("⚠️ Carica un documento per iniziare.")
else:
    st.error("⚠️ Configurazione API Key mancante.")
