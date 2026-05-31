import streamlit as st
import sqlite3
import feedparser

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

st.title("🎙️ Mijn Live Podcast App")
st.write("Jouw reistijd gevuld met échte, actuele podcasts van het internet.")
st.write("---")

# --- FUNCTIE: DATABASE EN FEEDS LIVE OPZETTEN ---
def database_en_feeds_initialiseren():
    connection = sqlite3.connect("podcasts.db")
    cursor = connection.cursor()
    
    # Zorg dat de basis-tabellen sowieso bestaan
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY, title TEXT, rss_url TEXT, description TEXT, language TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY, name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS podcast_genres (
            podcast_id INTEGER, genre_id INTEGER, PRIMARY KEY (podcast_id, genre_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, podcast_id INTEGER, title TEXT, 
            audio_url TEXT, duration_in_seconds INTEGER, pub_date TEXT, is_listened INTEGER DEFAULT 0
        )
    """)
    
    # Voeg de genres toe als ze er niet zijn
    cursor.execute("INSERT OR IGNORE INTO genres (id, name) VALUES (1, 'Wetenschap')")
    cursor.execute("INSERT OR IGNORE INTO genres (id, name) VALUES (3, 'Nieuws & Politiek')")
    
    # Echte feeds definieren
    echte_feeds = {
        5: ("Nerdland Maandoverzicht", "https://feeds.soundcloud.com/users/soundcloud:users:274391696/sounds.rss", 1), # Genre 1 = Wetenschap
        1: ("VRT Radio 1 Select", "https://rss.vrt.be/epub/manual/radio1_select.xml", 3) # Genre 3 = Nieuws
    }
    
    for pod_id, (titel, url, genre_id) in echte_feeds.items():
        # Voeg de podcast toe aan de tabel
        cursor.execute("""
            INSERT OR IGNORE INTO podcasts (id, title, rss_url, description, language)
            VALUES (?, ?, ?, 'Live podcast', 'Nederlands')
        """, (pod_id, titel, url))
        
        # Koppel aan het genre
        cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (?, ?)", (pod_id, genre_id))
        
        # Pluk de nieuwste 5 afleveringen live van internet
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                ep_titel = entry.title
                audio_url = entry.enclosures[0].href if entry.get('enclosures') else ""
                pub_date = entry.get('published', '')
                
                # Nerdland afleveringen zijn erg lang (~2 uur = 7200 seconden)
                duratie = entry.get('itunes_duration', 7200)
                try:
                    if ":" in str(duratie):
                        delen = list(map(int, duratie.split(':')))
                        if len(delen) == 3: seconden = delen[0]*3600 + delen[1]*60 + delen[2]
                        elif len(delen) == 2: seconden = delen[0]*60 + delen[1]
                    else: seconden = int(duratie)
                except:
                    seconden = 7200
                
                if audio_url:
                    cursor.execute("""
                        INSERT OR IGNORE INTO episodes (podcast_id, title, audio_url, duration_in_seconds, pub_date)
                        VALUES (?, ?, ?, ?, ?)
                    """, (pod_id, ep_titel, audio_url, seconden, pub_date))
        except:
            pass

    connection.commit()
    connection.close()

# Start de grote winterschoonmaak en live-import!
database_en_feeds_initialiseren()

# --- SIDEBAR INTERFACE ---
st.sidebar.header("⚙️ Instellingen")
taal = st.sidebar.radio("Welke taal?", ("Nederlands", "Engels"))

# Tip: We zetten de schuifbalk standaard lekker hoog (300 min) en verhogen het maximum naar 12 uur zodat Nerdland altijd past!
minuten_beschikbaar = st.sidebar.slider("Hoeveel minuten heb je?", 10, 720, 300, 10)
genre = st.sidebar.selectbox("Kies een genre:", ("Alles", "Wetenschap", "Nieuws & Politiek"))

# --- PLAYLIST LOGICA ---
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
        # Als de allereerste aflevering al groter is dan je totale budget, 
        # springen we naar de volgende om te kijken of er een kortere wél past!
        if totale_tijd_seconden + duur <= beschikbare_seconden:
            playlist.append({
                'id': ep_id, 'podcast': podcast_naam, 'aflevering': titel, 'minuten': round(duur / 60), 'url': audio_url
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

gekozen_playlist, totale_minuten = genereer_slimme_playlist(minuten_beschikbaar, taal, genre)

# --- STATISTIEKEN ---
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="Aantal fragmenten", value=f"{len(gekozen_playlist)} stuks")
with col2: st.metric(label="Totale luistertijd", value=f"{totale_minuten} min")
with col3: st.metric(label="Jouw budget", value=f"{minuten_beschikbaar} min")

percentage_gevuld = min(totale_minuten / minuten_beschikbaar, 1.0) if minuten_beschikbaar > 0 else 0.0
st.progress(percentage_gevuld, text=f"Je tijdslot is voor {int(percentage_gevuld * 100)}% gevuld")
st.write(" ")

# --- PLAYLIST TONEN ---
st.subheader("📋 Jouw Persoonlijke Playlist")

if not gekozen_playlist:
    st.info("Geen onbeluisterde afleveringen gevonden. Schuif je tijdslot verder open (Nerdland heeft veel tijd nodig!) of wissel van genre.")
else:
    for i, track in enumerate(gekozen_playlist, 1):
        st.markdown(f"""
            <div class="podcast-card">
                <span style='color: #d1477a; font-weight: bold; text-transform: uppercase; font-size: 0.85em; letter-spacing: 1px;'>🌸 {track['podcast']}</span>
                <h3 style='margin: 8px 0 12px 0; font-size: 1.25em;'>{i}. {track['aflevering']}</h3>
                <span class="badge">⏱️ {track['minuten']} minuten</span>
            </div>
        """, unsafe_allow_html=True)
        
        if track['url']:
            st.audio(track['url'])
        st.write(" ")
    
    st.write("---")
    if st.button("✔️ Markeer deze playlist als volledig beluisterd"):
        zet_op_beluisterd_in_db(gekozen_playlist)
        st.success("🎉 Database bijgewerkt!")
        st.balloons()