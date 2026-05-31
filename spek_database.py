import sqlite3

connection = sqlite3.connect("podcasts.db")
cursor = connection.cursor()

print("Database rigoureus aan het opfrissen...")

# 1. We zetten alle bestaande afleveringen weer op onbeluisterd
cursor.execute("UPDATE episodes SET is_listened = 0")

# 2. We gebruiken INSERT OR REPLACE. Dit dwingt SQLite om het te overschrijven als de url al bestaat!
cursor.execute("""
    INSERT OR REPLACE INTO podcasts (id, title, rss_url, description, language) 
    VALUES (2, 'Echte Misdaad BE', 'https://test.com/misdaad', 'Belgische misdaadverhalen.', 'Nederlands')
""")
misdaad_id = 2

cursor.execute("""
    INSERT OR REPLACE INTO podcasts (id, title, rss_url, description, language) 
    VALUES (3, 'Het Dagelijks Nieuws', 'https://test.com/nieuws', 'Het nieuws van de dag.', 'Nederlands')
""")
nieuws_id = 3

# 3. We controleren of de genres bestaan en halen de ID's op
cursor.execute("SELECT id FROM genres WHERE name = 'Misdaad'")
row_m = cursor.fetchone()
misdaad_genre_id = row_m[0] if row_m else 2

cursor.execute("SELECT id FROM genres WHERE name = 'Nieuws & Politiek'")
row_n = cursor.fetchone()
nieuws_genre_id = row_n[0] if row_n else 3

# Koppelen aan genres (veilig met OR IGNORE)
cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (?, ?)", (misdaad_id, misdaad_genre_id))
cursor.execute("INSERT OR IGNORE INTO podcast_genres (podcast_id, genre_id) VALUES (?, ?)", (nieuws_id, nieuws_genre_id))

# 4. Extra lange afleveringen toevoegen (in seconden) voor de 10-uurs test
extra_bulk = [
    (misdaad_id, "De Kasteelmoord - Aflevering 1", "https://audio.com/m1", 5400, "2026-05-31 12:00:00"), # 1.5 uur
    (misdaad_id, "De Kasteelmoord - Aflevering 2", "https://audio.com/m2", 7200, "2026-05-31 13:00:00"), # 2 uur
    (nieuws_id, "Formatie-update en Politiek Debat", "https://audio.com/n1", 3600, "2026-05-31 14:00:00"), # 1 uur
    (nieuws_id, "De Weekbrieving", "https://audio.com/n2", 10800, "2026-05-31 15:00:00")                 # 3 uur
]

# We overschrijven eventuele oude testafleveringen om unieke fouten te voorkomen
cursor.execute("DELETE FROM episodes WHERE audio_url IN ('https://audio.com/m1', 'https://audio.com/m2', 'https://audio.com/n1', 'https://audio.com/n2')")

for pod_id, title, url, duration, pub_date in extra_bulk:
    cursor.execute("""
        INSERT INTO episodes (podcast_id, title, audio_url, duration_in_seconds, pub_date)
        VALUES (?, ?, ?, ?, ?)
    """, (pod_id, title, url, duration, pub_date))

connection.commit()
connection.close()
print("🎉 GOUD! De database is nu 100% succesvol overschreven en gevuld!")