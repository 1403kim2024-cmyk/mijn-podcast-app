import streamlit as st
import feedparser
import random
from datetime import datetime

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
st.write("Elke dag verse, actuele suggesties van het internet — volledig op maat van jouw tijd.")
st.write("---")

# --- INITIALISEER HET GEHEUGEN VAN JOUW GSM (Zonder database-gedoe!) ---
# Streamlit kan dingen onthouden in het geheugen van de browser (st.session_state)
if "beluisterde_titels" not in st.session_state:
    st.session_state.beluisterde_titels = set()

# --- DE ULTIEME LIJST VAN INTERNATIONALE TOP-PODCASTS ---
FEEDS = [
    # NEDERLANDS
    {"naam": "Nerdland Maandoverzicht", "url": "https://feeds.soundcloud.com/users/soundcloud:users:274391696/sounds.rss", "genre": "🔬 Wetenschap", "taal": "Nederlands", "duur": 120},
    {"naam": "De Volksjury", "url": "https://feeds.pubsub.club/devolksjury.xml", "genre": "🕵️ Misdaad", "taal": "Nederlands", "duur": 65},
    {"naam": "De Stemmen van Assisen", "url": "https://www.nieuwsblad.be/rss/podcast/stemmen-van-assisen", "genre": "🕵️ Misdaad", "taal": "Nederlands", "duur": 45},
    {"naam": "Geschiedenis van Vlaanderen", "url": "https://rss.vrt.be/epub/manual/geschiedenis_van_vlaanderen.xml", "genre": "🏰 Geschiedenis", "taal": "Nederlands", "duur": 25},
    
    # ENGELS
    {"naam": "The Daily (NY Times)", "url": "https://feeds.simplecast.com/54nAGZIl", "genre": "📰 Nieuws & Actualiteit", "taal": "Engels", "duur": 30},
    {"naam": "Stuff You Should Know", "url": "https://feeds.iheart.com/stuffyoushouldknow", "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "duur": 50},
    {"naam": "Criminal", "url": "https://feeds.thisiscriminal.com/CriminalShow", "genre": "🕵️ Misdaad", "taal": "Engels", "duur": 35},
    {"naam": "Dan Carlin's Hardcore History", "url": "https://feeds.feedburner.com/dancarlin/history?format=xml", "genre": "🏰 Geschiedenis", "taal": "Engels", "duur": 180}
]

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit vandaag?", 15, 300, 90, 15)

st.sidebar.write("### 🌍 Welke talen wil je horen?")
wil_nl = st.sidebar.checkbox("Nederlands", value=True)
wil_en = st.sidebar.checkbox("Engels", value=True)

st.sidebar.write("### 📂 Welke genres hebben je voorkeur?")
genres_beschikbaar = sorted(list(set(f["genre"] for f in FEEDS)))
gekozen_genres = []
for g in genres_beschikbaar:
    if st.sidebar.checkbox(g, value=True):
        gekozen_genres.append(g)

# Knop om handmatig een compleet nieuwe frisse mix op te vragen
st.sidebar.write("---")
if st.sidebar.button("🔀 Schud de kaarten (Nieuwe suggesties)"):
    st.rerun()

# --- LIVE INTERNET IMPORTEER-LOGICA ---
@st.cache_data(ttl=1800) # Sla de internetdata 30 minuten op zodat de app razendsnel laadt
def laad_alle_afleveringen_live():
    alle_items = []
    for f in FEEDS:
        try:
            # Pluk live de allernieuwste 5 afleveringen van het internet
            parsed_feed = feedparser.parse(f["url"])
            for entry in parsed_feed.entries[:5]:
                audio = entry.enclosures[0].href if entry.get('enclosures') else ""
                if audio:
                    alle_items.append({
                        "podcast": f["naam"],
                        "titel": entry.title,
                        "url": audio,
                        "genre": f["genre"],
                        "taal": f["taal"],
                        "minuten": f["duur"] # We gebruiken onze slimme schatting voor de perfecte tijdslot-vulling
                    })
        except:
            pass
    return alle_items

# Haal de reusachtige lijst live op van internet
alle_beschikbare_afleveringen = laad_alle_afleveringen_live()

# --- FILTER LOGICA ---
# Filter op taal en genre, én zorg dat beluisterde afleveringen NOOIT meer terugkomen
mogelijke_mix = [
    a for a in alle_beschikbare_afleveringen
    if a["genre"] in gekozen_genres
    and ((wil_nl and a["taal"] == "Nederlands") or (wil_en and a["taal"] == "Engels"))
    and a["titel"] not in st.session_state.beluisterde_titels
]

# --- PLAYLIST SAMENSTELLEN ---
# We husselen de lijst volledig willekeurig zodat je ALTIJD een verrassende variatie krijgt
random.shuffle(mogelijke_mix)

playlist = []
totale_tijd = 0

for aflevering in mogelijke_mix:
    if totale_tijd + aflevering["minuten"] <= minuten_beschikbaar:
        playlist.append(aflevering)
        totale_tijd += aflevering["minuten"]

# --- PLAYLIST TONEN ---
col1, col2 = st.columns(2)
with col1: st.metric(label="Aantal fragmenten in deze mix", value=f"{len(playlist)} stuks")
with col2: st.metric(label="Totale gevulde reistijd", value=f"{totale_tijd} / {minuten_beschikbaar} min")

st.write(" ")
st.subheader("📋 Jouw Unieke Reismix voor Vandaag")

if not playlist:
    st.info("Geen nieuwe afleveringen gevonden voor deze combinatie. Vink meer genres/talen aan, schuif je reistijd open, of reset je geschiedenis!")
else:
    for i, track in enumerate(playlist, 1):
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['titel']}</h3>
                <span class="badge badge-genre">{track['genre']}</span>
                <span class="badge badge-lang">🌍 {track['taal']}</span>
                <span class="badge badge-time">⏱️ {track['minuten']} min</span>
            </div>
        """, unsafe_allow_html=True)
        st.audio(track['url'])
        st.write(" ")
    
    st.write("---")
    if st.button("✔️ Markeer deze specifieke mix als volledig beluisterd"):
        for track in playlist:
            st.session_state.beluisterde_titels.add(track["titel"])
        st.success("🎉 Gemarkeerd! Deze afleveringen zijn uit je bibliotheek verwijderd. Volgende keer krijg je weer splinternieuwe suggesties!")
        st.balloons()

# Optie in de zijbalk om je luistergeschiedenis te resetten mocht je database leegraken
if st.session_state.beluisterde_titels:
    st.sidebar.write("---")
    if st.sidebar.button("🔄 Luistergeschiedenis wissen"):
        st.session_state.beluisterde_titels.clear()
        st.sidebar.success("Geschiedenis gewist!")
        st.rerun()