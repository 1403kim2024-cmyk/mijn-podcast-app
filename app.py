import streamlit as st
import random

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn YouTube Podcast Mixer", page_icon="📺", layout="centered")

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
        font-weight: bold; font-size: 1.1em; padding: 12px; border-radius: 10px;
        text-decoration: none; margin-top: 10px; box-shadow: 0 3px 10px rgba(228,113,158,0.3);
    }
    .playlist-button:hover { background-color: #008b8b; }
    .badge { padding: 4px 10px; border-radius: 6px; font-size: 0.85em; margin-right: 5px; color: white; }
    .badge-genre { background-color: #00a8a8; }
    .badge-time { background-color: #e4719e; }
    .badge-lang { background-color: #7b68ee; }
    </style>
""", unsafe_allow_html=True)

st.title("📺 Mijn YouTube Podcast Mixer")
st.write("Kies je reistijd en vind de perfecte podcast-afspeellijst die automatisch doorloopt!")
st.write("---")

if "bekeken_podcasts" not in st.session_state:
    st.session_state.bekeken_podcasts = set()

# --- BIBLIOTHEEK MET OFFICIËLE PLAYLIST LINKS ---
# Deze links openen direct de échte series op YouTube die automatisch na elkaar afspelen!
YOUTUBE_PLAYLISTS = [
    {
        "podcast": "Nerdland Maandoverzicht", 
        "omschrijving": "Het meest actuele maandoverzicht vol wetenschapsnieuws met Lieven Scheire.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PL_Xv49g9VfKpK7hErc8LwN_6N_y-zIuUX", 
        "genre": "🔬 Wetenschap", "taal": "Nederlands", "minuten": 100
    },
    {
        "podcast": "De Volksjury", 
        "omschrijving": "Vlaanderens populairste true-crime podcast over onopgeloste moordzaken.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PLG0Tf83uX9v0f_Z9X-76u7Wep_D2oF6U7", 
        "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 60
    },
    {
        "podcast": "De Stemmen van Assisen", 
        "omschrijving": "Het Nieuwsblad blikt achter de schermen van de meest spraakmakende rechtszaken.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PLfO0hP_4Wb8vA7z_p7QeO6X5pT5V6_M3r", 
        "genre": "🕵️ Misdaad", "taal": "Nederlands", "minuten": 45
    },
    {
        "podcast": "Universiteit van Vlaanderen", 
        "omschrijving": "Korte, boeiende colleges van topwetenschappers over uiteenlopende mysteries.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PL3v_B_bE_lU8-w_6S7Vf9AkeGbyUdfiPZ", 
        "genre": "🏰 Geschiedenis & Wetenschap", "taal": "Nederlands", "minuten": 20
    },
    {
        "podcast": "Stuff You Should Know (English)", 
        "omschrijving": "De wereldberoemde podcast die werkelijk álles tot op de bodem uitzoekt.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PL_g3zK2g1X6W5qNf1RkCgV_xI-M_N-wIk", 
        "genre": "🔬 Wetenschap & Weetjes", "taal": "Engels", "minuten": 45
    },
    {
        "podcast": "Rotten Mango (English)", 
        "omschrijving": "Diepgaande true-crime verhalen met een focus op psychologie en details.", 
        "playlist_url": "https://www.youtube.com/playlist?list=PLwZ_D3M5_v7e3Z_XvKzW_jVbU_bXf0GvI", 
        "genre": "🕵️ Misdaad", "taal": "Engels", "minuten": 80
    }
]

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit ongeveer?", 15, 180, 60, 15)

st.sidebar.write("### 🌍 Welke talen?")
wil_nl = st.sidebar.checkbox("Nederlands 🇳🇱/🇧🇪", value=True)
wil_en = st.sidebar.checkbox("Engels 🇬🇧/🇺🇸", value=True)

st.sidebar.write("### 📂 Welke genres?")
genres_beschikbaar = sorted(list(set(p["genre"] for p in YOUTUBE_PLAYLISTS)))
gekozen_genres = []
for g in genres_beschikbaar:
    if st.sidebar.checkbox(g, value=True):
        gekozen_genres.append(g)

st.sidebar.write("---")
if st.sidebar.button("🔀 Schud de kaarten voor een nieuwe show"):
    st.rerun()

# --- FILTEREN ---
mogelijke_shows = []
for p in YOUTUBE_PLAYLISTS:
    if p["genre"] not in gekozen_genres:
        continue
    if p["podcast"] in st.session_state.bekeken_podcasts:
        continue
    if p["taal"] == "Nederlands" and not wil_nl:
        continue
    if p["taal"] == "Engels" and not wil_en:
        continue
        
    mogelijke_shows.append(p)

random.shuffle(mogelijke_shows)

# --- SELECTEER EEN COOLE SHOW DIE BIJ JOUW TIJD PAST ---
gekozen_show = None
for show in mogelijke_shows:
    # Zoek een show die mooi binnen je tijdslot past, of de beste match is
    if show["minuten"] <= minuten_beschikbaar + 30:
        gekozen_show = show
        break

# Als er niks specifieks past, pakken we gewoon de eerste beschikbare show
if not gekozen_show and mogelijke_shows:
    gekozen_show = mogelijke_shows[0]

# --- INTERFACE WEERGEVEN ---
if not gekozen_show:
    st.info("Geen nieuwe podcasts gevonden. Vink meer genres aan of reset je geschiedenis!")
else:
    st.subheader("📋 Jouw Match voor deze Rit:")
    
    icoon = "🔬" if "Wetenschap" in gekozen_show['genre'] else "🕵️" if "Misdaad" in gekozen_show['genre'] else "🏰"
    
    st.markdown(f"""
        <div class="podcast-card">
            <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {gekozen_show['podcast']}</span>
            <h3 style='margin: 8px 0 8px 0; font-size: 1.35em;'>{gekozen_show['podcast']} Afspeellijst</h3>
            <p style='color: #555; font-size: 0.95em; margin-bottom: 12px;'>{gekozen_show['omschrijving']}</p>
            <span class="badge badge-genre">{icoon} {gekozen_show['genre']}</span>
            <span class="badge badge-lang">🌍 {gekozen_show['taal']}</span>
            <span class="badge badge-time">⏱️ Gem. {gekozen_show['minuten']} min</span>
            <br><br>
            <a href="{gekozen_show['playlist_url']}" target="_blank" class="playlist-button">🚀 Open deze Playlist in YouTube (Speelt automatisch door!)</a>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✔️ Markeer deze podcast als gehoord voor vandaag"):
        st.session_state.bekeken_podcasts.add(gekozen_show["podcast"])
        st.success(f"Gemarkeerd! {gekozen_show['podcast']} is tijdelijk uit je keuzes gehaald.")
        st.rerun()

if st.session_state.bekeken_podcasts:
    st.sidebar.write("---")
    if st.sidebar.button("🔄 Geschiedenis wissen"):
        st.session_state.bekeken_podcasts.clear()
        st.sidebar.success("Geschiedenis gereset!")
        st.rerun()