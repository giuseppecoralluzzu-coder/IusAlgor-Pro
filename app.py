import streamlit as st
import google.generativeai as genai
import os
import tempfile
import time # Serve per gestire il tempo della intro
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="IusAlgor Pro", page_icon="⚖️", layout="wide")

# Funzione per caricare il CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css("style.css")

# --- 2. INTRO VIDEO (EFFETTO WOW) ---
# Usiamo la session_state per far vedere il video solo la prima volta che si apre l'app
if "intro_done" not in st.session_state:
    # Creiamo un contenitore vuoto che riempie la pagina
    placeholder = st.empty()
    
    with placeholder.container():
        # Mostriamo il video centrato
        # Nota: 'autoplay' e 'muted' sono necessari perché molti browser bloccano i video automatici con audio
        video_file = open('Creazione_Animazione_Logo_Legale.mp4', 'rb')
        video_bytes = video_file.read()
        st.video(video_bytes, format="video/mp4", autoplay=True, muted=True)
        
        # Aspettiamo la durata del video (es. 5 secondi) prima di passare all'app
        time.sleep(5) 
    
    # Rimuoviamo il video e segnamo che la intro è finita
    placeholder.empty()
    st.session_state.intro_done = True

# --- DA QUI PARTE L'APP VERA E PROPRIA ---
st.title("⚖️ IusAlgor Pro")
st.markdown("##### *Audit di Conformità Legale per Sistemi di Intelligenza Artificiale*")

# ... tutto il resto del codice che avevamo prima (Sidebar, Logica Chat, ecc.) ...
