import streamlit as st
import random
import urllib.parse

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn YouTube Playlist Mixer", page_icon="📺", layout="centered")

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #fcf8fa; }
    .podcast-card {
        background-color: #fff0f5;
        padding: 22px;
        border-radius: 14px;
        border-left: 6px solid #008b8b;
        border-right: 1px solid #f0dae4; border-top: 1px solid #f0dae4; border-bottom: 1px solid #f0dae4;
        margin-bottom: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    h1, h3 { color: #005f5f !important; }
    .playlist-button {
        display: block; text-align: center; background-color: #e4719e; color: white !important;
        font-weight: bold; font-size: 1.2em; padding: 15px; border-radius: 12px;
        text-decoration: none; margin: 20px 0; box-shadow: 0 4px 15px rgba(228,113,158,0.4);
    }
    .playlist-button:hover { background-color: #008b8b; }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.85em; margin-right: 5px; color: white; }
    .badge-genre { background-color: #00a8a8; }
    .badge-time { background-color: #e4719e; }
    .badge-lang { background-color: #7b68ee; }
    </style>
""", unsafe_allow_html=True)

st.title("📺 Mijn Automatische YouTube Reismix")
st.write("Genereer een playlist op maat. De knop opent YouTube waarin alles automatisch na elkaar afspeelt!")
st.write("---")

if "bekeken_videos" not in st.session_state:
    st.session_state.bekeken_videos = set()

# --- BIBLIOTHEEK MET ECHTE CODES (Een greep uit legendarische afleveringen) ---
YOUTUBE_POOL = [
    # NEDERLANDS: Nerdland (Seizoen/Maandoverzichten)
    {"podcast": "Nerdland Maandoverzicht", "titel": "Maandoverzicht Maart 2026", "yt_id": "89vY3XWclpE", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 105},
    {"podcast": "Nerdland Maandoverzicht", "titel": "Maandoverzicht Februari 2026", "yt_id": "E69A57V_b_8", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 95},
    {"podcast": "Nerdland", "titel": "Special: Kernenergie & Fusion", "yt_id": "u49w9R8wV7Y", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 75},
    
    # NEDERLANDS: De Volksjury & Misdaad
    {"podcast": "De Volksjury", "titel": "Aflevering 100 - Live Special", "yt_id": "h3_9f_fmx_M", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 70},
    {"podcast": "De Volksjury", "titel": "Aflevering 85 - Moord in de Polders", "yt_id": "Pz78V3uJ3l8", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 60},
    {"podcast": "Stemmen van Assisen", "titel": "De Kasteelmoord Reconstructie", "yt_id": "W9vPq4p5Y7M", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 45},
    {"podcast": "Volksjury Dossier", "titel": "De Horror-Huisarts", "yt_id": "b7vC3x8wM4k", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 55},

    # NEDERLANDS: Geschiedenis
    {"podcast": "Geschiedenis van Vlaanderen", "titel": "De Guldensporenslag Mythe", "yt_id": "X4vW8_p9oLk", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "minuten": 30},
    {"podcast": "Universiteit van Vlaanderen", "titel": "Hoe dachten de ridders écht?", "yt_id": "Y3vA4_x9P_k", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "minuten": 18},
    
    # ENGELS: Misdaad & Documentaires
    {"podcast": "Rotten Mango (English)", "titel": "The Case of the Missing Heiress", "yt_id": "m9P8vX4lQ7w", "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 85},
    {"podcast": "JCS