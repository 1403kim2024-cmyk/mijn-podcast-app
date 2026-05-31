import streamlit as st
import urllib.request
import json
import random

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn Ultieme Podcast Mixer", page_icon="🎙️", layout="centered")

# --- CUSTOM CSS STYLING (Roze & Appelblauwzeegroen) ---
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
    .stButton>button {
        background-color: #008b8b !important; color: white !important;
        border-radius: 10px !important; width: 100%; font-weight: bold; padding: 12px; border: none !important;
    }
    .stButton>button:hover { background-color: #e4719e !important; color: white !important; }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.85em; margin-right: 5px; color: white; }
    .badge-genre { background-color: #00a8a8; }
    .badge-time { background-color: #e4719e; }
    .badge-lang { background-color: #7b68ee; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Mijn Wereldwijde Podcast Mixer")
st.write("Een diepe, gevarieerde lijst met actuele Nederlandse en Engelse podcasts.")
st.write("---")

# --- LUISTERGESCHIEDENIS INSTELLEN ---
if "beluisterde_titels" not in st.session_state:
    st.session_state.beluisterde_titels = set()

# --- DE INTERNATIONALE PODCAST LIJST ---
# We hebben de feeds stabieler gemaakt en extra Engelse/Nederlandse toppers toegevoegd!
PODCASTS = [
    {"naam": "Nerdland Maandoverzicht", "url": "https://feeds.soundcloud.com/users/soundcloud:users:274391696/sounds.rss", "genre": "🔬 Wetenschap", "taal": "Nederlands", "duur": 120},
    {"naam": "De Volksjury", "url": "https://feeds.pubsub.club/devolksjury.xml", "genre": "🕵️ Misdaad", "taal": "Nederlands", "duur": 65},
    {"naam": "De Stemmen van Assisen", "url": "https://www.nieuwsblad.be/rss/podcast/stemmen-van-assisen", "genre": "🕵️ Misdaad", "taal": "Nederlands", "duur": 45},
    {"naam": "Geschiedenis van Vlaanderen", "url": "https://rss.vrt.be/epub/manual/geschiedenis_van_vlaanderen.xml", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "duur": 25},
    {"naam": "The Daily (NY Times)", "url": "https://feeds.simplecast.com/54nAGZIl", "genre": "📰 Nieuws & Actualiteit", "taal": "Engels", "duur": 30},
    {"naam": "Stuff You Should Know", "url": "https://feeds.iheart.com/stuffyoushouldknow", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "duur": 50},
    {"naam": "Criminal", "url": "https://feeds.thisiscriminal.com/CriminalShow", "genre": "🕵️ Misdaad", "taal": "Engels", "duur": 35},
    {"naam": "BBC Global News Podcast", "url": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss", "genre": "📰 Nieuws & Actualiteit", "taal": "Engels", "duur": 30}
]

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit?", 15, 360, 120, 15)

st.sidebar.write("### 🌍 Welke talen?")
wil_nl = st.sidebar.checkbox("Nederlands 🇳🇱/🇧🇪", value=True)
wil_en = st.sidebar.checkbox("Engels 🇬🇧/🇺🇸", value=True)

st.sidebar.write("### 📂 Welke genres?")
genres_beschikbaar = sorted(list(set(p["genre"] for p in PODCASTS)))
gekozen_genres = []
for g in genres_beschikbaar:
    if st.sidebar.checkbox(g, value=True):
        gekozen_genres.append(g)

st.sidebar.write("---")
if st.sidebar.button("🔀 Schud de kaarten voor een nieuwe mix"):
    st.rerun()

# --- BLOKKADE-VRIJE PARSER (Met behulp van een internet-tussendeur) ---
@st.cache_data(ttl=900) #