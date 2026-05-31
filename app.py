import streamlit as st
import urllib.request
import urllib.parse
import json
import random

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn Ultieme Podcast Mixer", page_icon="🎙️", layout="centered")

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

st.title("🎙️ Mijn Wereldwijde Podcast Mixer")
st.write("Een diepe, gevarieerde lijst met actuele Nederlandse en Engelse podcasts.")
st.write("---")

# --- LUISTERGESCHIEDENIS INSTELLEN ---
if "beluisterde_titels" not in st.session_state:
    st.session_state.beluisterde_titels = set()

# --- DE INTERNATIONALE PODCAST LIJST ---
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

# --- BLOKKADE-VRIJE PARSER ---
def haal_alle_afleveringen_veilig_op():
    alle_items = []
    
    for p in PODCASTS:
        try:
            veilig_url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.parse.quote(p['url'])}"
            req = urllib.request.Request(veilig_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode())
            
            if data.get("status") == "ok":
                for item in data.get("items", [])[:10]:
                    audio_url = item.get("enclosure", {}).get("link", "")
                    if not audio_url and "media:content" in item:
                        audio_url = item["media:content"].get("url", "")
                    
                    if audio_url:
                        alle_items.append({
                            "podcast": p["naam"],
                            "titel": item.get("title", ""),
                            "url": audio_url,
                            "genre": p["genre"],
                            "taal": p["taal"],
                            "minuten": p["duur"]
                        })
        except:
            pass
            
    return alle_items

# Trek direct de actuele lijst live binnen
alle_afleveringen = haal_alle_afleveringen_veilig_op()

# --- FILTEREN OP JOUW VOORKEUREN ---
mogelijke_mix = [
    a for a in alle_afleveringen
    if a["genre"] in gekozen_genres
    and ((wil_nl and a["taal"] == "Nederlands") or (wil_en and a["taal"] == "Engels"))
    and a["titel"] not in st.session_state.beluisterde_titels
]

# Shuffle de lijst volledig willekeurig voor maximale variatie
random.shuffle(mogelijke_mix)

# --- PLAYLIST OPBOUWEN OP BASIS VAN TIJD ---
playlist = []
totale_tijd = 0

for aflevering in mogelijke_mix:
    if totale_tijd + aflevering["minuten"] <= minuten_beschikbaar:
        playlist.append(aflevering)
        totale_tijd += aflevering["minuten"]

# --- PLAYLIST WEERGEVEN ---
col1, col2 = st.columns(2)
with col1: st.metric(label="Aantal fragmenten in mix", value=f"{len(playlist)} stuks")
with col2: st.metric(label="Gevulde luistertijd", value=f"{totale_tijd} / {minuten_beschikbaar} min")

st.write(" ")
st.subheader("📋 Jouw Gevarieerde Reismix")

if not playlist:
    st.info("Geen nieuwe afleveringen gevonden. Vink meer genres aan, wissel van taal of verhoog je reistijd!")
else:
    for i, track in enumerate(playlist, 1):
        icoon = "🔬" if "Wetenschap" in track['genre'] else "🕵️" if "Misdaad" in track['genre'] else "🏰" if "Geschiedenis" in track['genre'] else "📰"
        
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['titel']}</h3>
                <span class="badge badge-genre">{icoon} {track['genre']}</span>
                <span class="badge badge-lang">🌍 {track['taal']}</span>
                <span class="badge badge-time">⏱️ {track['minuten']} min</span>
            </div>
        """, unsafe_allow_html=True)
        st.audio(track['url'])
        st.write(" ")
    
    st.write("---")
    if st.button("✔️ Markeer deze hele mix als volledig beluisterd"):
        for track in playlist:
            st.session_state.beluisterde_titels.add(track["titel"])
        st.success("🎉 Gemarkeerd! Deze afleveringen zijn uit je bibliotheek verwijderd. Klik hierboven op 'Schud de kaarten' voor een gloednieuwe mix!")
        st.balloons()

if st.session_state.beluisterde_titels:
    st.sidebar.write("---")
    if st.sidebar.button("🔄 Luistergeschiedenis wissen"):
        st.session_state.beluisterde_titels.clear()
        st.sidebar.success("Geschiedenis gereset!")
        st.rerun()