from database import Database

db = Database()
conn = db.get_connection()
cursor = conn.cursor()

print("Current tracks:")
cursor.execute("SELECT id, title FROM tracks")
for track_id, title in cursor.fetchall():
    print(f"  {track_id}: {title}")

cursor.execute("DELETE FROM tracks WHERE id < 4")
cursor.execute("DELETE FROM playlist_tracks WHERE track_id < 4")
cursor.execute("DELETE FROM download_queue WHERE status='failed'")

conn.commit()
print("\n✓ Database cleaned!")

cursor.execute("SELECT id, title FROM tracks")
print("\nRemaining tracks:")
for track_id, title in cursor.fetchall():
    print(f"  {track_id}: {title}")

conn.close()