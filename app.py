import streamlit as st
import google.generativeai as genai
import os
import tempfile
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA E STILE ---
st.set_page_config(page_title="IusAlgor Pro - IA Legale", page_icon="⚖️", layout="wide")

# Funzione per caricare il CSS esterno
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carichiamo lo stile dal file style.css
load_css("style.css")

st.title("⚖️ IusAlgor Pro")
st.markdown("##### *Audit di Conformità Legale per Sistemi di Intelligenza Artificiale*")

# --- 2. SIDEBAR (CONSOLE DI CONTROLLO) ---
with st.sidebar:
    # --- MODIFICA QUI PER IL LOGO GRANDE E NITIDO ---
    if os.path.exists("logo.png"):
        # Apriamo l'immagine
        image = Image.open('logo.png')
        # Aumentiamo la larghezza a 250 pixel per renderlo grande e leggibile.
        # Assicurati che il file logo.png originale sia ad alta risoluzione!
        st.image(image, width=250) 
    else:
        # Riserva se il file non esiste
        st.image("https://cdn-icons-png.flaticon.com/512/1053/1053331.png", width=80)
    # -----------------------------------------------
    
    st.header("Console di Controllo")
    
    api_key = st.text_input("Gemini API Key", type="password", help="Inserisci la tua chiave segreta Google")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documentazione Tecnica", type=['pdf', 'txt'])
    
    st.markdown("---")
    livello_dettaglio = st.select_slider(
        "Dettaglio Analisi:",
        options=["Riassuntiva", "Completa"],
        value="Completa"
    )
    st.info("Configurazione attiva: GDPR / AI Act Compliance")

# --- 3. LOGICA DEL CHATBOT ---
if api_key:
    genai.configure(api_key=api_key)
    
    # Inizializzazione memoria
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizzazione storico chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input utente
    if prompt := st.chat_input("Digita qui la tua richiesta legale..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if uploaded_file is not None:
                # Gestione file temporaneo
                ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                
                with st.spinner('Analisi dei protocolli in corso...'):
                    # Upload file su Gemini
                    g_file = genai.upload_file(tmp_path)
                    
                    # Definizione del comportamento dell'IA (System Prompt)
                    is_first_msg = len(st.session_state.messages) <= 1
                    
                    if is_first_msg:
                        if livello_dettaglio == "Completa":
                            sys_instr = "Sei IusAlgor Pro. Analizza il file e rispondi ESATTAMENTE con queste sezioni formattate: 🎯 AMBITI INTACCATI, ⚠️ RISCHI PRINCIPALI, 💡 AZIONI CORRETTIVE, ❓ Q&A DI APPROFONDIMENTO."
                        else:
                            sys_instr = "Sei IusAlgor Pro. Dai un verdetto legale sintetico (max 5 righe) sui rischi principali del file."
                    else:
                        sys_instr = "Sei IusAlgor Pro. Rispondi in modo colloquiale come un consulente umano. Non ripetere le sezioni e non essere ripetitivo. Aiuta l'utente a risolvere i dubbi."

                    model = genai.GenerativeModel(
                        model_name='gemini-2.5-flash', 
                        system_instruction=sys_instr
                    )
                    
                    # Gestione Memoria (History)
                    history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    # Esecuzione Chat
                    chat = model.start_chat(history=history)
                    response = chat.send_message([g_file, prompt])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                # Pulizia file temporaneo
                os.remove(tmp_path)
            else:
                st.warning("⚠️ Carica un documento nella sidebar per iniziare l'analisi.")
else:
    st.info("👈 Inserisci la API Key nella sidebar per attivare il sistema.")