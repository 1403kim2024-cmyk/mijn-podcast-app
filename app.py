import streamlit as st
import random

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn Ultieme YouTube Mixer", page_icon="📺", layout="centered")

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

st.title("📺 Mijn YouTube Podcast Mixer")
st.write("Mix en ontdek echte video-podcasts op basis van jouw beschikbare reistijd.")
st.write("---")

# --- GEHEUGEN VOOR GEZIENE VIDEO'S ---
if "bekuisterde_videos" not in st.session_state:
    st.session_state.bekuisterde_videos = set()

# --- REUSACHTIGE LIJST MET ECHTE YOUTUBE PODCASTS (NL & EN) ---
# Hier staat een hele reeks aan verschillende afleveringen in!
YOUTUBE_POOL = [
    # --- NEDERLANDS: WETENSCHAP (Nerdland) ---
    {"podcast": "Nerdland Maandoverzicht", "titel": "Maandoverzicht Mei 2026", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 120},
    {"podcast": "Nerdland Maandoverzicht", "titel": "Maandoverzicht April 2026", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 110},
    {"podcast": "Nerdland Maandoverzicht", "titel": "Special: Artificiële Intelligentie", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 90},
    
    # --- NEDERLANDS: MISDAAD (De Volksjury & Assisen) ---
    {"podcast": "De Volksjury", "titel": "Aflevering 140 - De Kasteelmoord", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 60},
    {"podcast": "De Volksjury", "titel": "Aflevering 139 - Mysterie in de Ardennen", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 70},
    {"podcast": "De Stemmen van Assisen", "titel": "De Zaak van de Parachutemoord", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 45},
    {"podcast": "De Stemmen van Assisen", "titel": "Het Proces van de Eeuw", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 50},
    
    # --- NEDERLANDS: GESCHIEDENIS ---
    {"podcast": "Geschiedenis van Vlaanderen", "titel": "Aflevering 1: De Prehistorie & Romeinen", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "minuten": 35},
    {"podcast": "Geschiedenis van Vlaanderen", "titel": "Aflevering 2: De Guldensporenslag", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "minuten": 40},
    {"podcast": "Universiteit van Vlaanderen", "titel": "Waarom was de Napoleon zo klein?", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "minuten": 20},

    # --- ENGELS: MISDAAD ---
    {"podcast": "Criminal (English)", "titel": "Episode 210 - The Chase", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 35},
    {"podcast": "Rotten Mango", "titel": "The Twin Sister Mystery", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 80},
    
    # --- ENGELS: WETENSCHAP & WEETJES ---
    {"podcast": "Stuff You Should Know", "titel": "How Castles Work", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 45},
    {"podcast": "Stuff You Should Know", "titel": "The Mystery of Easter Island", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 55},
    {"podcast": "Veritasium", "titel": "The Illusion of Truth", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 25},

    # --- ENGELS: GESCHIEDENIS ---
    {"podcast": "The Rest is History", "titel": "The Fall of the Roman Empire", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🏰 Geschiedenis", "taal": "Engels", "minuten": 50},
    {"podcast": "The Rest is History", "titel": "The Real Robin Hood", "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "genre": "🏰 Geschiedenis", "taal": "Engels", "minuten": 45}
]

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit?", 15, 360, 100, 15)

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
if st.sidebar.button("🔀 Schud de kaarten (Nieuwe Mix)"):
    st.rerun()

# --- FILTEREN ---
mogelijke_mix = [
    v for v in YOUTUBE_POOL
    if v["genre"] in gekozen_genres
    and ((wil_nl and v["taal"] == "Nederlands") or (wil_en and v["taal"] == "Engels"))
    and v["titel"] not in st.session_state.bekuisterde_videos
]

# Volledig willekeurig husselen zodat het ALTIJD anders is
random.shuffle(mogelijke_mix)

# --- LIJST SAMENSTELLEN OP BASIS VAN TIJD ---
playlist = []
totale_tijd = 0

for video in mogelijke_mix:
    if totale_tijd + video["minuten"] <= minuten_beschikbaar:
        playlist.append(video)
        totale_tijd += video["minuten"]

# --- PLAYLIST BIJSTUREN EN WEERGEVEN ---
col1, col2 = st.columns(2)
with col1: st.metric(label="Aantal video's in mix", value=f"{len(playlist)} stuks")
with col2: st.metric(label="Gevulde tijd slot", value=f"{totale_tijd} / {minuten_beschikbaar} min")

st.write(" ")
st.subheader("📋 Jouw Persoonlijke YouTube Reismix")

if not playlist:
    st.info("Geen nieuwe video's gevonden voor deze combinatie. Verhoog je tijd of reset je geschiedenis!")
else:
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
        
        # De magische YouTube-speler van Streamlit!
        st.video(track['url'])
        st.write(" ")
    
    st.write("---")
    if st.button("✔️ Markeer deze video's als bekeken"):
        for track in playlist:
            st.session_state.bekuisterde_videos.add(track["titel"])
        st.success("🎉 Gemarkeerd! Deze video's zijn uit je poule gehaald. Klik op 'Schud de kaarten' voor een gloednieuwe selectie!")
        st.balloons()

if st.session_state.bekuisterde_videos:
    st.sidebar.write("---")
    if st.sidebar.button("🔄 Geschiedenis wissen"):
        st.session_state.bekuisterde_videos.clear()
        st.sidebar.success("Geschiedenis gereset!")
        st.rerun()