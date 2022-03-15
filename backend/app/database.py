# -*- coding: utf_8 -*-

import sqlite3
import pandas
from io import StringIO

song_table = "songs"
entry_table = "entries"
index_label = "Id"
done_table = "done_songs"


def open_db():
    conn = sqlite3.connect("/tmp/karaoqueue.db")
    conn.execute('PRAGMA encoding = "UTF-8";')
    return conn


def import_songs(song_csv):
    print("Start importing Songs...")
    df = pandas.read_csv(StringIO(song_csv), sep=';')
    conn = open_db()
    cur = conn.cursor()
    df.to_sql(song_table, conn, if_exists='replace',
              index=False)
    cur.execute("SELECT Count(Id) FROM songs")
    num_songs = cur.fetchone()[0]
    conn.close()
    print("Imported songs ({} in Database)".format(num_songs))
    return("Imported songs ({} in Database)".format(num_songs))


def create_entry_table():
    conn = open_db()
    conn.execute('CREATE TABLE IF NOT EXISTS '+entry_table +
                 ' (ID INTEGER PRIMARY KEY NOT NULL, Song_Id INTEGER NOT NULL, Name VARCHAR(255), Client_Id VARCHAR(36), Transferred INTEGER DEFAULT 0)')
    conn.close()


def create_done_song_table():
    conn = open_db()
    conn.execute('CREATE TABLE IF NOT EXISTS '+done_table +
                 ' (Song_Id INTEGER PRIMARY KEY NOT NULL,  Plays INTEGER)')
    conn.close()


def create_song_table():
    conn = open_db()
    conn.execute("CREATE TABLE IF NOT EXISTS \""+song_table+"""\" (
        "Id" INTEGER,
        "Title" TEXT,
        "Artist" TEXT,
        "Year" INTEGER,
        "Duo" INTEGER,
        "Explicit" INTEGER,
        "Date Added" TEXT,
        "Styles" TEXT,
        "Languages" TEXT
    )""")
    conn.close()


def create_list_view():
    conn = open_db()
    conn.execute("""CREATE VIEW IF NOT EXISTS [Liste] AS
                 SELECT Name, Title, Artist, entries.Id, songs.Id, entries.Transferred
                 FROM entries, songs
                 WHERE entries.Song_Id=songs.Id""")
    conn.close()


def create_done_song_view():
    conn = open_db()
    conn.execute("""CREATE VIEW IF NOT EXISTS [Abspielliste] AS
                 SELECT Artist || \" - \" || Title AS Song, Plays AS Wiedergaben
                 FROM songs, done_songs
                 WHERE done_songs.Song_Id=songs.Id""")
    conn.close()


def get_list():
    conn = open_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Liste")
    return cur.fetchall()


def get_played_list():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Abspielliste")
    return cur.fetchall()


def get_song_list():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT Artist || \" - \" || Title AS Song, Id FROM songs;")
    return cur.fetchall()


def get_song_completions(input_string):
    conn = open_db()
    cur = conn.cursor()
    # Don't look, it burns...
    prepared_string = "%{0}%".format(
        input_string).upper()  # "Test" -> "%TEST%"
    print(prepared_string)
    cur.execute(
        "SELECT Title || \" - \" || Artist AS Song, Id FROM songs WHERE REPLACE(REPLACE(REPLACE(REPLACE(UPPER( SONG ),'ö','Ö'),'ü','Ü'),'ä','Ä'),'ß','ẞ') LIKE (?) LIMIT 20;", (prepared_string,))
    return cur.fetchall()


def add_entry(name, song_id, client_id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entries (Song_Id,Name,Client_Id) VALUES(?,?,?);", (song_id, name, client_id))
    conn.commit()
    conn.close()
    return


def add_sung_song(entry_id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute("""SELECT Song_Id FROM entries WHERE Id=?""", (entry_id,))
    song_id = cur.fetchone()[0]
    cur.execute("""INSERT OR REPLACE INTO done_songs (Song_Id, Plays)
                VALUES("""+str(song_id)+""",
                       COALESCE(
                           (SELECT Plays FROM done_songs
                            WHERE Song_Id="""+str(song_id)+"), 0) + 1)"
                )
    conn.commit()
    delete_entry(entry_id)
    conn.close()
    return True


def toggle_transferred(entry_id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT Transferred FROM entries WHERE ID =?", (entry_id,))
    marked = cur.fetchall()[0][0]
    if(marked == 0):
        cur.execute(
            "UPDATE entries SET Transferred = 1 WHERE ID =?", (entry_id,))
    else:
        cur.execute(
            "UPDATE entries SET Transferred = 0 WHERE ID =?", (entry_id,))
    conn.commit()
    conn.close()
    return True


def check_entry_quota(client_id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT Count(*) FROM entries WHERE entries.Client_Id = ?", (client_id,))
    return cur.fetchall()[0][0]


def check_queue_length():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM entries")
    return cur.fetchall()[0][0]


def clear_played_songs():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM done_songs")
    conn.commit()
    conn.close()
    return True


def delete_entry(id):
    conn = open_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True


def delete_entries(ids):
    idlist = []
    for x in ids:
        idlist.append((x,))
    try:
        conn = open_db()
        cur = conn.cursor()
        cur.executemany("DELETE FROM entries WHERE id=?", idlist)
        conn.commit()
        conn.close()
        return cur.rowcount
    except sqlite3.Error as error:
        return -1


def delete_all_entries():
    conn = open_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return True
