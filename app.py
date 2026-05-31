import streamlit as st
import sqlite3

# --- PAGINA INSTELLINGEN ---
st.set_page_config(
    page_title="Mijn Ultieme Podcast App", 
    page_icon="🎙️", 
    layout="centered"
)

# --- CUSTOM CSS STYLING (Appelblauwzeegroen & Roze) ---
st.markdown("""
    <style>
    /* Achtergrond van de hele pagina een heel zachte, frisse tint geven */
    .stApp {
        background-color: #fcf8fa;
    }
    
    /* De podcast-kaart: Zacht roze achtergrond met een dikke appelblauwzeegroene rand */
    .podcast-card {
        background-color: #fff0f5; /* LavenderBlush / zacht roze */
        padding: 22px;
        border-radius: 14px;
        border-left: 6px solid #008b8b; /* Donker appelblauwzeegroen */
        border-right: 1px solid #f0dae4;
        border-top: 1px solid #f0dae4;
        border-bottom: 1px solid #f0dae4;
        margin-bottom: 18px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    
    /* De hoofdtitels een mooie diepe teal/appelblauwzeegroene kleur geven */
    h1, h3 {
        color: #005f5f !important;
    }
    
    /* Grote actieknop: Volledig appelblauwzeegroen, verandert naar roze bij hover! */
    .stButton>button {
        background-color: #008b8b !important;
        color: white !important;
        border-radius: 10px !important;
        width: 100%;
        font-weight: bold;
        padding: 12px;
        border: none !important;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #e4719e !important; /* Levendig roze bij aanwijzen */
        color: white !important;
    }
    
    /* Kleine subtiele badges in de kaarten */
    .badge {
        background-color: #00a8a8;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# --- TITEL VAN DE APP ---
st.title("🎙️ Mijn Persoonlijke Podcast Speler")
st.write("Jouw reistijd perfect gevuld in stijl.")
st.write("---")

# --- SIDEBAR INTERFACE (Instellingen) ---
st.sidebar.header("⚙️ Instellingen")
taal = st.sidebar.radio("Welke taal?", ("Nederlands", "Engels"))
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten heb je?", 10, 600, 60, 10)
genre = st.sidebar.selectbox("Kies een genre:", ("Alles", "Wetenschap", "Misdaad", "Nieuws & Politiek"))

# --- FUNCTIE: PLAYLIST BEREKENEN ---
def genereer_slimme_playlist(beschikbare_minuten, gekozen_taal, gekozen_genre):
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    beschikbare_seconden = beschikbare_minuten * 60
    
    if gekozen_genre == 'Alles':
        cursor.execute("""
            SELECT e.id, e.title, e.duration_in_seconds, p.title, e.audio_url 
            FROM episodes e
            JOIN podcasts p ON e.podcast_id = p.id
            WHERE e.is_listened = 0 AND p.language = ?
            ORDER BY e.pub_date DESC
        """, (gekozen_taal,))
    else:
        cursor.execute("""
            SELECT e.id, e.title, e.duration_in_seconds, p.title, e.audio_url 
            FROM episodes e
            JOIN podcasts p ON e.podcast_id = p.id
            JOIN podcast_genres pg ON p.id = pg.podcast_id
            JOIN genres g ON pg.genre_id = g.id
            WHERE e.is_listened = 0 AND p.language = ? AND g.name = ?
            ORDER BY e.pub_date DESC
        """, (gekozen_taal, gekozen_genre))
        
    alle_afleveringen = cursor.fetchall()
    connection.close()
    
    playlist = []
    totale_tijd_seconden = 0
    
    for ep_id, titel, duur, podcast_naam, audio_url in alle_afleveringen:
        if totale_tijd_seconden + duur <= beschikbare_seconden:
            playlist.append({
                'id': ep_id,
                'podcast': podcast_naam,
                'aflevering': titel,
                'minuten': round(duur / 60),
                'url': audio_url
            })
            totale_tijd_seconden += duur
            
    return playlist, round(totale_tijd_seconden / 60)

def zet_op_beluisterd_in_db(playlist):
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    for track in playlist:
        cursor.execute("UPDATE episodes SET is_listened = 1 WHERE id = ?", (track['id'],))
    connection.commit()
    connection.close()

# --- BEREKENING UITVOEREN ---
gekozen_playlist, totale_minuten = genereer_slimme_playlist(minuten_beschikbaar, taal, genre)

# --- VISUELE DASHBOARD MET METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Aantal fragmenten", value=f"{len(gekozen_playlist)} stuks")
with col2:
    st.metric(label="Totale luistertijd", value=f"{totale_minuten} min")
with col3:
    st.metric(label="Jouw budget", value=f"{minuten_beschikbaar} min")

# --- VISUELE VOORTGANGSBALK (Kleur beweegt mee met thema) ---
percentage_gevuld = min(totale_minuten / minuten_beschikbaar, 1.0) if minuten_beschikbaar > 0 else 0.0
st.progress(percentage_gevuld, text=f"Je tijdslot is voor {int(percentage_gevuld * 100)}% gevuld")
st.write(" ")

# --- JOUW PLAYLIST TONEN ---
st.subheader("📋 Jouw Persoonlijke Playlist")

if not gekozen_playlist:
    st.info("Geen onbeluisterde afleveringen gevonden. Schuif je tijd open of zet je database weer vol via Thonny!")
else:
    for i, track in enumerate(gekozen_playlist, 1):
        # Dynamische HTML-kaart met onze nieuwe frisse kleuren
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['aflevering']}</h3>
                <span class="badge">⏱️ {track['minuten']} minuten</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Audiospeler
        if track['url']:
            st.audio(track['url'])
        st.write(" ")
    
    st.write("---")
    
    # Grote actieknop
    if st.button("✔️ Markeer deze playlist als volledig beluisterd"):
        zet_op_beluisterd_in_db(gekozen_playlist)
        st.success("🎉 Database bijgewerkt! Veel plezier met de ballonnen!")
        st.balloons()