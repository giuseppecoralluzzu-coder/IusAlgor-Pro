import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time
import base64
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# Funzione per caricare il CSS esterno
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# --- 2. INTRO "SIGLA" (EFFETTO CINEMATOGRAFICO) ---
# Mostriamo il video solo se è la prima volta che l'utente entra nella sessione
if "intro_done" not in st.session_state:
    placeholder = st.empty()
    
    video_path = "Creazione_Animazione_Logo_Legale.mp4"
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode()
        
        # HTML per video pulito: niente barre, niente controlli, riempie lo spazio
        video_html = f'''
            <div style="display: flex; justify-content: center; align-items: center; height: 85vh; background-color: #0e1117;">
                <video width="90%" height="auto" autoplay muted playsinline style="pointer-events: none; border-radius: 15px; box-shadow: 0px 0px 30px rgba(0,0,0,0.5);">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
            </div>
        '''
        
        with placeholder.container():
            st.markdown(video_html, unsafe_allow_html=True)
            # --- TIMER SINCRONIZZATO ---
            # Impostato a 11 secondi per coprire tutta la durata del tuo video
            time.sleep(11) 
            
        placeholder.empty()
        st.session_state.intro_done = True

# --- 3. GESTIONE API KEY (SEGRETI) ---
# Streamlit pesca la chiave dai Secrets impostati online
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

# --- 4. SIDEBAR (STRUMENTI) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        image = Image.open('logo.png')
        st.image(image, width=250)
    
    st.header("Console di Controllo")
    
    # Se la chiave non è nei secrets (test locale), appare il box
    if not api_key:
        api_key = st.text_input("Inserisci Gemini API Key", type="password")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documentazione Tecnica", type=['pdf', 'txt'])
    
    st.markdown("---")
    livello_dettaglio = st.select_slider(
        "Dettaglio Analisi:",
        options=["Riassuntiva", "Completa"],
        value="Completa"
    )
    st.info("Algoritmo di Audit aggiornato all'AI Act.")

# --- 5. INTERFACCIA CHAT ---
st.title("⚖️ IusAlgor Pro")
st.markdown("##### *Audit di Conformità Legale per Sistemi di Intelligenza Artificiale*")

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra i messaggi precedenti
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Gestione nuovo input
    if prompt := st.chat_input("Chiedi un'analisi legale..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if uploaded_file is not None:
                ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                
                with st.spinner('Elaborazione dati tecnici in corso...'):
                    g_file = genai.upload_file(tmp_path)
                    
                    # Istruzioni diverse se è il primo messaggio o un approfondimento
                    if len(st.session_state.messages) <= 1:
                        if livello_dettaglio == "Completa":
                            sys_instr = "Sei IusAlgor Pro. Analizza il file e rispondi con: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE, ❓ Q&A."
                        else:
                            sys_instr = "Sei IusAlgor Pro. Dai un verdetto rapido e sintetico."
                    else:
                        sys_instr = "Sei IusAlgor Pro. Rispondi come un consulente esperto e colloquiale."

                    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                    
                    # Ricostruisce la cronologia della chat
                    history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"]=="user" else "model"
                        history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=history)
                    response = chat.send_message([g_file, prompt])
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                
                os.remove(tmp_path)
            else:
                st.warning("⚠️ Carica prima un documento tecnico dalla barra laterale per avviare l'Audit.")
else:
    st.error("⚠️ Chiave API non rilevata. Controlla i Secrets di Streamlit.")
