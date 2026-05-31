import streamlit as st
import random

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

# --- BIBLIOTHEEK MET ECHTE YOUTUBE CODES ---
YOUTUBE_POOL = [
    # NEDERLANDS: Nerdland
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
    
    # ENGELS: Misdaad
    {"podcast": "Rotten Mango", "titel": "The Case of the Missing Heiress", "yt_id": "m9P8vX4lQ7w", "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 85},
    {"podcast": "JCS - Criminal Psychology", "titel": "The Legend of Jeff", "yt_id": "8-X7pJUY-G4", "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 52},
    
    # ENGELS: Wetenschap & Weetjes
    {"podcast": "Veritasium", "titel": "The Scientific Way to Turn Back Time", "yt_id": "K6L8V_p9X8k", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 24},
    {"podcast": "Stuff You Should Know", "titel": "How Phobias Work", "yt_id": "w9v_P7x4Lko", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 45}
]

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit?", 15, 360, 120, 15)

st.sidebar.write("### 🌍 Welke talen?")
wil_nl = st.sidebar.checkbox("Nederlands 🇳🇱/🇧🇪", value=True)
wil_en = st.sidebar.checkbox("Engels 🇬🇧/🇺🇸", value=True)

st.sidebar.write("### 📂 Welke genres?")
genres_beschikbaar = sorted(list(set(p["genre"] for p in YOUTUBE_POOL)))
gekozen_genres = []
for g in genres_beschikbaar:
    if st.sidebar.checkbox(g, value=True):
        gekozen_genres.append(g)

st.sidebar.write("---")
if st.sidebar.button("🔀 Schud de kaarten voor een nieuwe mix"):
    st.rerun()

# --- FILTEREN EN SHUFFLEN ---
mogelijke_mix = []
for v in YOUTUBE_POOL:
    # Check of het genre is aangevinkt
    if v["genre"] not in gekozen_genres:
        continue
    # Check of de video al bekeken is
    if v["titel"] in st.session_state.bekeken_videos:
        continue
    # Check de taalvoorkeuren
    if v["taal"] == "Nederlands" and not wil_nl:
        continue
    if v["taal"] == "Engels" and not wil_en:
        continue
        
    mogelijke_mix.append(v)

random.shuffle(mogelijke_mix)

# --- PLAYLIST OPBOUWEN ---
playlist = []
totale_tijd = 0

for video in mogelijke_mix:
    if totale_tijd + video["minuten"] <= minuten_beschikbaar:
        playlist.append(video)
        totale_tijd += video["minuten"]

# --- PLAYLIST GENEREREN EN INTERFACE ---
col1, col2 = st.columns(2)
with col1: st.metric(label="Aantal fragmenten", value=f"{len(playlist)} stuks")
with col2: st.metric(label="Gevulde tijd", value=f"{totale_tijd} / {minuten_beschikbaar} min")

if not playlist:
    st.info("Geen video's gevonden. Vink meer opties aan of verhoog je tijd!")
else:
    # De magische link bouwen voor YouTube
    video_ids = [track["yt_id"] for track in playlist]
    yt_playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"
    
    # Grote opvallende knop voor de reismix
    st.markdown(f'<a href="{yt_playlist_url}" target="_blank" class="playlist-button">🚀 Start Reismix in de YouTube-App (Speelt automatisch door!)</a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📋 Inhoud van je huidige mix:")
    
    for i, track in enumerate(playlist, 1):
        icoon = "🔬" if "Wetenschap" in track['genre'] else "🕵️" if "Misdaad" in track['genre'] else "🏰"
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['titel']}</h3>
                <span class="badge badge-genre">{icoon} {track['genre']}</span>
                <span class="badge badge-lang">🌍 {track['taal']}</span>
                <span class="badge badge-time">⏱️ {track['minuten']} min</span>
            </div>
        """, unsafe_allow_html=True)

    if st.button("✔️ Markeer deze video's als bekeken"):
        for track in playlist:
            st.session_state.bekeken_videos.add(track["titel"])
        st.success("Gemarkeerd! Deze afleveringen zijn uit je poule verwijderd.")
        st.rerun()

if st.session_state.bekeken_videos:
    st.sidebar.write("---")
    if st.sidebar.button("🔄 Geschiedenis wissen"):
        st.session_state.bekeken_videos.clear()
        st.sidebar.success("Geschiedenis gereset!")
        st.rerun()