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

# --- 2. INTRO "SIGLA" (SOLO AL PRIMO AVVIO) ---
if "intro_done" not in st.session_state:
    placeholder = st.empty()
    
    video_path = "Creazione_Animazione_Logo_Legale.mp4"
    if os.path.exists(video_path):
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            video_base64 = base64.b64encode(video_bytes).decode()
        
        # HTML per video a tutto schermo, senza controlli e non cliccabile
        video_html = f'''
            <div style="display: flex; justify-content: center; align-items: center; height: 80vh; background-color: #0e1117;">
                <video width="80%" height="auto" autoplay muted playsinline style="pointer-events: none; border-radius: 20px;">
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
            </div>
        '''
        
        with placeholder.container():
            st.markdown(video_html, unsafe_allow_html=True)
            # Regola i secondi qui sotto in base alla durata del tuo video
            time.sleep(6) 
            
        placeholder.empty()
        st.session_state.intro_done = True

# --- 3. GESTIONE API KEY (SEGRETI) ---
# Cerca la chiave nei Secrets di Streamlit (per la versione online)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Se non la trova (test locale), la chiede nella sidebar
    api_key = None

# --- 4. SIDEBAR (CONSOLE DI CONTROLLO) ---
with st.sidebar:
    # Logo Grande e Nitido
    if os.path.exists("logo.png"):
        image = Image.open('logo.png')
        st.image(image, width=250)
    
    st.header("Console di Controllo")
    
    # Se la chiave non è nei secrets, mostra il campo di input
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
    st.info("Configurazione: GDPR / AI Act Compliance")

# --- 5. LOGICA PRINCIPALE ---
st.title("⚖️ IusAlgor Pro")
st.markdown("##### *Audit di Conformità Legale per Sistemi di Intelligenza Artificiale*")

if api_key:
    genai.configure(api_key=api_key)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Visualizzazione Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input Utente
    if prompt := st.chat_input("Digita qui la tua richiesta legale..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            if uploaded_file is not None:
                ext = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name
                
                with st.spinner('Analisi dei protocolli in corso...'):
                    g_file = genai.upload_file(tmp_path)
                    
                    is_first_msg = len(st.session_state.messages) <= 1
                    
                    if is_first_msg:
                        if livello_dettaglio == "Completa":
                            sys_instr = "Sei IusAlgor Pro. Analizza il file e rispondi con icone: 🎯 AMBITI, ⚠️ RISCHI, 💡 AZIONI CORRETTIVE, ❓ Q&A."
                        else:
                            sys_instr = "Sei IusAlgor Pro. Dai un verdetto legale sintetico (max 5 righe)."
                    else:
                        sys_instr = "Sei IusAlgor Pro. Rispondi in modo colloquiale come un avvocato umano."

                    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=sys_instr)
                    
                    # Memoria storica
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
                st.warning("⚠️ Per iniziare, carica un documento tecnico nella barra laterale.")
else:
    st.error("⚠️ API Key non configurata. Inseriscila nei Secrets di Streamlit o nella sidebar.")
