# -*- coding: utf_8 -*-

from types import NoneType
from MySQLdb import Connection
from sqlalchemy import create_engine
import sqlite3
import mariadb
import pandas
from io import StringIO

song_table = "songs"
entry_table = "entries"
index_label = "Id"
done_table = "done_songs"

connection = None


def open_db() -> Connection:
    global connection
    if (not connection):
        engine = create_engine(
            "mysql://ek0ur6p6ky9gdmif:jk571ov6g38g5iqv@eporqep6b4b8ql12.chr7pe7iynqr.eu-west-1.rds.amazonaws.com:3306/xdfmpudc3remzgj0")
        connection = engine.connect()
    # cur.execute('PRAGMA encoding = "UTF-8";')
    return connection


def import_songs(song_csv):
    print("Start importing Songs...")
    df = pandas.read_csv(StringIO(song_csv), sep=';')
    conn = open_db()
    df.to_sql(song_table, conn, if_exists='replace',
              index=False)
    cur = conn.execute("SELECT Count(Id) FROM songs")
    num_songs = cur.fetchone()[0]
    # conn.close()
    print("Imported songs ({} in Database)".format(num_songs))
    return("Imported songs ({} in Database)".format(num_songs))


def create_entry_table():
    conn = open_db()
    conn.execute('CREATE TABLE IF NOT EXISTS '+entry_table +
                 ' (ID INTEGER PRIMARY KEY NOT NULL, Song_Id INTEGER NOT NULL, Name VARCHAR(255), Client_Id VARCHAR(36), Transferred INTEGER DEFAULT 0)')
    # conn.close()


def create_done_song_table():
    conn = open_db()
    conn.execute('CREATE TABLE IF NOT EXISTS '+done_table +
                 ' (Song_Id INTEGER PRIMARY KEY NOT NULL,  Plays INTEGER)')
    # conn.close()


def create_song_table():
    conn = open_db()
    conn.execute("CREATE TABLE IF NOT EXISTS `"+song_table+"""` (
        `Id` INTEGER,
        `Title` TEXT,
        `Artist` TEXT,
        `Year` INTEGER,
        `Duo` INTEGER,
        `Explicit` INTEGER,
        `Date Added` TEXT,
        `Styles` TEXT,
        `Languages` TEXT
    )""")
    # conn.close()


def create_list_view():
    conn = open_db()
    conn.execute("""CREATE OR REPLACE VIEW `Liste` AS
                 SELECT Name, Title, Artist, entries.Id AS entry_ID, songs.Id AS song_ID, entries.Transferred
                 FROM entries, songs
                 WHERE entries.Song_Id=Song_ID""")
    # conn.close()


def create_done_song_view():
    conn = open_db()
    conn.execute("""CREATE OR REPLACE VIEW `Abspielliste` AS
                 SELECT Artist || \" - \" || Title AS Song, Plays AS Wiedergaben
                 FROM songs, done_songs
                 WHERE done_songs.Song_Id=songs.Id""")
    # conn.close()


def get_list():
    conn = open_db()
    cur = conn.execute("SELECT * FROM Liste")
    return cur.fetchall()


def get_played_list():
    conn = open_db()
    cur = conn.execute("SELECT * FROM Abspielliste")
    return cur.fetchall()


def get_song_list():
    conn = open_db()
    cur = conn.execute(
        "SELECT Artist || \" - \" || Title AS Song, Id FROM songs;")
    return cur.fetchall()


def get_song_completions(input_string):
    conn = open_db()
    # Don't look, it burns...
    prepared_string = "%{0}%".format(
        input_string).upper()  # "Test" -> "%TEST%"
    print(prepared_string)
    cur = conn.execute(
        "SELECT CONCAT(Artist,\" - \",Title) AS Song, Id FROM songs WHERE CONCAT(Artist,\" - \",Title) LIKE (%s) LIMIT 20;", [prepared_string])
    return cur.fetchall()


def add_entry(name, song_id, client_id):
    conn = open_db()
    conn.execute(
        "INSERT INTO entries (Song_Id,Name,Client_Id) VALUES(%s,%s,%s);", (song_id, name, client_id))
    # conn.close()
    return


def add_sung_song(entry_id):
    conn = open_db()
    cur = conn.execute(
        """SELECT Song_Id FROM entries WHERE Id=?""", (entry_id,))
    song_id = cur.fetchone()[0]
    conn.execute("""INSERT OR REPLACE INTO done_songs (Song_Id, Plays)
                VALUES("""+str(song_id)+""",
                       COALESCE(
                           (SELECT Plays FROM done_songs
                            WHERE Song_Id="""+str(song_id)+"), 0) + 1)"
                 )
    delete_entry(entry_id)
    # conn.close()
    return True


def toggle_transferred(entry_id):
    conn = open_db()
    cur = conn.execute(
        "SELECT Transferred FROM entries WHERE ID =?", (entry_id,))
    marked = cur.fetchall()[0][0]
    if(marked == 0):
        conn.execute(
            "UPDATE entries SET Transferred = 1 WHERE ID =?", (entry_id,))
    else:
        conn.execute(
            "UPDATE entries SET Transferred = 0 WHERE ID =?", (entry_id,))
    # conn.close()
    return True


def check_entry_quota(client_id):
    conn = open_db()
    cur = conn.execute(
        "SELECT Count(*) FROM entries WHERE entries.Client_Id = ?", (client_id,))
    return cur.fetchall()[0][0]


def check_queue_length():
    conn = open_db()
    cur = conn.execute("SELECT Count(*) FROM entries")
    return cur.fetchall()[0][0]


def clear_played_songs():
    conn = open_db()
    conn.execute("DELETE FROM done_songs")
    # conn.close()
    return True


def delete_entry(id):
    conn = open_db()
    conn.execute("DELETE FROM entries WHERE id=?", (id,))
    # conn.close()
    return True


def delete_entries(ids):
    idlist = []
    for x in ids:
        idlist.append((x,))
    try:
        conn = open_db()
        cur = conn.execute("DELETE FROM entries WHERE id=?", idlist)
        # conn.close()
        return cur.rowcount
    except mariadb.Error as error:
        return -1


def delete_all_entries():
    conn = open_db()
    conn.execute("DELETE FROM entries")
    # conn.close()
    return True
