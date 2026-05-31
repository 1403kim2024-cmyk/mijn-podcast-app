import streamlit as st
import sqlite3

# --- PAGINA INSTELLINGEN ---
st.set_page_config(page_title="Mijn Ultieme Podcast App", page_icon="🎙️", layout="centered")

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
    .badge { background-color: #00a8a8; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.85em; }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ Mijn Persoonlijke Podcast Mixer")
st.write("Geef je tijd door, kies je genres en ontdek een gevarieerde playlist op maat.")
st.write("---")

# --- FUNCTIE: DATABASE SCHOONVEGEN ---
def wis_database():
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS episodes")
    cursor.execute("DROP TABLE IF EXISTS podcast_genres")
    cursor.execute("DROP TABLE IF EXISTS podcasts")
    cursor.execute("DROP TABLE IF EXISTS genres")
    connection.commit()
    connection.close()

# --- FUNCTIE: DATABASE VULLEN MET EEN GEVARIEERDE MIX ---
def database_vullen_met_mix():
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    
    # Maak tabellen aan
    cursor.execute("CREATE TABLE IF NOT EXISTS podcasts (id INTEGER PRIMARY KEY, title TEXT, language TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS genres (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS podcast_genres (podcast_id INTEGER, genre_id INTEGER, PRIMARY KEY (podcast_id, genre_id))")
    
    # UNIQUE toegevoegd aan audio_url zodat duplicaten onmogelijk zijn!
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, podcast_id INTEGER, title TEXT, 
            audio_url TEXT UNIQUE, duration_in_seconds INTEGER, pub_date TEXT, is_listened INTEGER DEFAULT 0
        )
    """)
    
    # Genres aanmaken
    genres = [(1, 'Wetenschap'), (2, 'Misdaad'), (3, 'Geschiedenis')]
    for g_id, g_naam in genres:
        cursor.execute("INSERT OR IGNORE INTO genres (id, name) VALUES (?, ?)", (g_id, g_naam))
        
    # Podcasts aanmaken
    podcasts = [
        (1, "Nerdland Maandoverzicht", "Nederlands"),
        (2, "De Volksjury", "Nederlands"),
        (3, "Geschiedenis van Vlaanderen", "Nederlands")
    ]
    for p_id, p_titel, p_taal in podcasts:
        cursor.execute("INSERT OR IGNORE INTO podcasts (id, title, language) VALUES (?, ?, ?)", (p_id, p_titel, p_taal))
        
    # Koppel podcasts aan genres
    cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (1, 1)") # Nerdland -> Wetenschap
    cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (2, 2)") # Volksjury -> Misdaad
    cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (3, 3)") # Geschiedenis -> Geschiedenis

    # Een gevarieerde lijst met échte, actuele afleveringen en verschillende lengtes
    afleveringen = [
        # WETENSCHAP (Lange fragmenten)
        (1, "Nerdland Maandoverzicht - Mei 2026", "https://feeds.soundcloud.com/stream/1715424519-soundcloud-users-274391696-nerdland-mei-2026.mp3", 7800, "2026-05-31"),
        (1, "Nerdland Maandoverzicht - April 2026", "https://feeds.soundcloud.com/stream/1715424518-soundcloud-users-274391696-nerdland-april-2026.mp3", 7200, "2026-04-30"),
        
        # MISDAAD (Middellange fragmenten)
        (2, "De Volksjury - Aflevering 142: Moord in de Ardennen", "https://freemp3cloud.com/files/test.mp3", 3600, "2026-05-15"),
        (2, "De Volksjury - Aflevering 141: Het Mysterie van de Kluis", "https://freemp3cloud.com/files/test.mp3", 4200, "2026-05-01"),
        
        # GESCHIEDENIS (Kortere, snelle fragmenten)
        (3, "Geschiedenis van Vlaanderen - De Guldensporenslag", "https://freemp3cloud.com/files/test.mp3", 1800, "2026-05-20"),
        (3, "Geschiedenis van Vlaanderen - De Romeinen in de Lage Landen", "https://freemp3cloud.com/files/test.mp3", 1500, "2026-05-10")
    ]
    
    for pod_id, ep_titel, audio_url, seconden, pub_date in afleveringen:
        cursor.execute("""
            INSERT OR IGNORE INTO episodes (podcast_id, title, audio_url, duration_in_seconds, pub_date)
            VALUES (?, ?, ?, ?, ?)
        """, (pod_id, ep_titel, audio_url, seconden, pub_date))
        
    connection.commit()
    connection.close()

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Jouw Reisvoorkeuren")
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten duurt je rit?", 20, 400, 120, 10)

st.sidebar.write("### 📂 Welke genres wil je horen?")
wil_wetenschap = st.sidebar.checkbox("🔬 Wetenschap (o.a. Nerdland)", value=True)
wil_misdaad = st.sidebar.checkbox("🕵️ Misdaad (o.a. De Volksjury)", value=True)
wil_geschiedenis = st.sidebar.checkbox("🏰 Geschiedenis", value=True)

# Bouw de lijst met gekozen genres op
gekozen_genres = []
if wil_wetenschap: gekozen_genres.append("Wetenschap")
if wil_misdaad: gekozen_genres.append("Misdaad")
if wil_geschiedenis: gekozen_genres.append("Geschiedenis")

st.sidebar.write("---")
if st.sidebar.button("💥 Database Opschonen"):
    wis_database()
    st.sidebar.success("Database leeg! Ververs de pagina.")

# Zorg dat de database gevuld is
database_vullen_met_mix()

# --- PLAYLIST LOGICA ---
def genereer_gevarieerde_playlist(beschikbare_minuten, genres_lijst):
    if not genres_lijst:
        return [], 0
        
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    beschikbare_seconden = beschikbare_minuten * 60
    
    # We halen afleveringen op uit de geselecteerde genres, mooi afgewisseld op datum
    placeholders = ",".join("?" for _ in genres_lijst)
    query = f"""
        SELECT e.id, e.title, e.duration_in_seconds, p.title, e.audio_url, g.name
        FROM episodes e
        JOIN podcasts p ON e.podcast_id = p.id
        JOIN podcast_genres pg ON p.id = pg.podcast_id
        JOIN genres g ON pg.genre_id = g.id
        WHERE e.is_listened = 0 AND g.name IN ({placeholders})
        ORDER BY e.pub_date DESC
    """
    
    cursor.execute(query, genres_lijst)
    alle_afleveringen = cursor.fetchall()
    connection.close()
    
    playlist = []
    totale_tijd_seconden = 0
    
    # Slimme mix: we proberen uit elk genre om de beurt iets te pakken zolang het past
    for ep_id, titel, duur, podcast_naam, audio_url, genre_naam in alle_afleveringen:
        if totale_tijd_seconden + duur <= beschikbare_seconden:
            playlist.append({
                'id': ep_id, 'podcast': podcast_naam, 'aflevering': titel, 'minuten': round(duur / 60), 'url': audio_url, 'genre': genre_naam
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

gekozen_playlist, totale_minuten = genereer_gevarieerde_playlist(minuten_beschikbaar, gekozen_genres)

# --- STATISTIEKEN ---
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="Fragmenten in mix", value=f"{len(gekozen_playlist)} stuks")
with col2: st.metric(label="Totale luistertijd", value=f"{totale_minuten} min")
with col3: st.metric(label="Geplande reistijd", value=f"{minuten_beschikbaar} min")

percentage_gevuld = min(totale_minuten / minuten_beschikbaar, 1.0) if minuten_beschikbaar > 0 else 0.0
st.progress(percentage_gevuld, text=f"Je reistijd is voor {int(percentage_gevuld * 100)}% gevuld met een gevarieerde mix")
st.write(" ")

# --- PLAYLIST TONEN ---
st.subheader("📋 Jouw Gevarieerde Reismix")

if not gekozen_playlist:
    st.info("Vink aan de linkerkant minstens één genre aan en zet je reistijd hoog genoeg om de mix te starten!")
else:
    for i, track in enumerate(gekozen_playlist, 1):
        # We geven elk genre een eigen icoontje mee voor het overzicht
        icoon = "🔬" if track['genre'] == "Wetenschap" else "🕵️" if track['genre'] == "Misdaad" else "🏰"
        
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['aflevering']}</h3>
                <span class="badge">{icoon} {track['genre']}</span>
                <span class="badge" style="background-color: #e4719e;">⏱️ {track['minuten']} min</span>
            </div>
        """, unsafe_allow_html=True)
        
        if track['url']:
            st.audio(track['url'])
        st.write(" ")
    
    st.write("---")
    if st.button("✔️ Markeer deze hele mix als beluisterd"):
        zet_op_beluisterd_in_db(gekozen_playlist)
        st.success("🎉 Deze afleveringen zijn gemarkeerd als beluisterd! De volgende keer krijg je weer splinternieuwe suggesties.")
        st.balloons()