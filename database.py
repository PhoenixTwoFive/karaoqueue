import sqlite3
import pandas
from io import StringIO

song_table  = "songs"
entry_table = "entries"
index_label = "Id"

def open_db():
    conn = sqlite3.connect("test.db")
    return conn

def import_songs(song_csv):
    df = pandas.read_csv(StringIO(song_csv), sep=';')
    conn = open_db()
    df.to_sql(song_table, conn, if_exists='replace',
              index=False)
    conn.close()
    return

def create_entry_table():
    conn = open_db()
    t = (entry_table,)
    conn.execute('CREATE TABLE IF NOT EXISTS '+entry_table +
                 ' (ID INTEGER PRIMARY KEY NOT NULL, Song_Id INTEGER NOT NULL, Name VARCHAR(255))')
    conn.close()

def create_list_view():
    conn = open_db()
    conn.execute("""CREATE VIEW IF NOT EXISTS [Liste] AS
                 SELECT Name, Title, Artist, entries.Id
                 FROM entries, songs
                 WHERE entries.Song_Id=songs.Id""")
    conn.close()

def get_list():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Liste")
    return cur.fetchall()

def get_song_list():
    conn =open_db()
    cur = conn.cursor()
    cur.execute("SELECT Title || \" - \" || Artist AS Song, Id FROM songs")
    return cur.fetchall()

def get_song_completions(input_string):
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT Title || \" - \" || Artist AS Song, Id FROM songs WHERE Song LIKE '%"+input_string+"%'")
    return cur.fetchall()

def add_entry(name,song_id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entries (Song_Id,Name) VALUES(?,?);", (song_id,name))
    conn.commit()
    conn.close()
    return

def delete_entry(id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return True
