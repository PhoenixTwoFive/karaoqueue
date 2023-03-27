# -*- coding: utf_8 -*-

from email.mime import base
from MySQLdb import Connection
from sqlalchemy import create_engine, engine
import pandas
from io import StringIO
from flask import current_app

song_table = "songs"
entry_table = "entries"
index_label = "Id"
done_table = "done_songs"

sql_engine = None


def get_db_engine() -> engine.base.Engine:
    global sql_engine
    if (not sql_engine):
        print(current_app.config.get("DBCONNSTRING"))
        sql_engine = create_engine(current_app.config.get("DBCONNSTRING"))  # type: ignore
    return sql_engine


def import_songs(song_csv):
    print("Start importing Songs...")
    df = pandas.read_csv(StringIO(song_csv), sep=';')
    with get_db_engine().connect() as conn:
        df.to_sql(song_table, conn, if_exists='replace',
                index=False)
        cur = conn.execute("SELECT Count(Id) FROM songs")
        num_songs = cur.fetchone()[0] # type: ignore
    print("Imported songs ({} in Database)".format(num_songs))
    return("Imported songs ({} in Database)".format(num_songs))


def create_entry_table():
    with get_db_engine().connect() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS '+entry_table +
                 ' (ID INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, Song_Id INTEGER NOT NULL, Name VARCHAR(255), Client_Id VARCHAR(36), Transferred INTEGER DEFAULT 0)')


def create_done_song_table():
    with get_db_engine().connect() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS '+done_table +
                 ' (Song_Id INTEGER PRIMARY KEY NOT NULL,  Plays INTEGER)')


def create_song_table():
    with get_db_engine().connect() as conn:
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


def create_list_view():
    with get_db_engine().connect() as conn:
        conn.execute("""CREATE OR REPLACE VIEW `Liste` AS
                 SELECT Name, Title, Artist, entries.Id AS entry_ID, songs.Id AS song_ID, entries.Transferred
                 FROM entries, songs
                 WHERE entries.Song_Id=songs.Id""")


def create_done_song_view():
    with get_db_engine().connect() as conn:
        conn.execute("""CREATE OR REPLACE VIEW `Abspielliste` AS
                 SELECT CONCAT(Artist," - ", Title) AS Song, Plays AS Wiedergaben
                 FROM songs, done_songs
                 WHERE done_songs.Song_Id=songs.Id""")


def get_list():
    with get_db_engine().connect() as conn:
        cur = conn.execute("SELECT * FROM Liste")
    return cur.fetchall()


def get_played_list():
    with get_db_engine().connect() as conn:
        cur = conn.execute("SELECT * FROM Abspielliste")
    return cur.fetchall()


def get_song_list():
    with get_db_engine().connect() as conn:
        cur = conn.execute(
        "SELECT Artist || \" - \" || Title AS Song, Id FROM songs;")
    return cur.fetchall()


def get_song_completions(input_string):
    with get_db_engine().connect() as conn:
        # Don't look, it burns...
        prepared_string = "%{0}%".format(
            input_string).upper()  # "Test" -> "%TEST%"
        print(prepared_string)
        cur = conn.execute(
            "SELECT CONCAT(Artist,\" - \",Title) AS Song, Id FROM songs WHERE CONCAT(Artist,\" - \",Title) LIKE (%s) LIMIT 20;", [prepared_string])
    return cur.fetchall()


def add_entry(name, song_id, client_id):
    with get_db_engine().connect() as conn:
        conn.execute(
        "INSERT INTO entries (Song_Id,Name,Client_Id) VALUES(%s,%s,%s);", (song_id, name, client_id))
    return


def add_sung_song(entry_id):
    with get_db_engine().connect() as conn:
        cur = conn.execute(
            """SELECT Song_Id FROM entries WHERE Id=%s""", (entry_id,))
        song_id = cur.fetchone()[0] # type: ignore
        conn.execute("""INSERT INTO done_songs (Song_Id, Plays) VALUES("""+str(song_id)+""",1) ON DUPLICATE KEY UPDATE Plays=Plays + 1;""")
        delete_entry(entry_id)
    return True


def toggle_transferred(entry_id):
    with get_db_engine().connect() as conn:
        cur = conn.execute(
            "SELECT Transferred FROM entries WHERE ID =%s", (entry_id,))
        marked = cur.fetchall()[0][0]
        if(marked == 0):
            conn.execute(
                "UPDATE entries SET Transferred = 1 WHERE ID =%s", (entry_id,))
        else:
            conn.execute(
                "UPDATE entries SET Transferred = 0 WHERE ID =%s", (entry_id,))
    return True


def check_entry_quota(client_id):
    with get_db_engine().connect() as conn:
        cur = conn.execute(
            "SELECT Count(*) FROM entries WHERE entries.Client_Id = %s", (client_id,))
    return cur.fetchall()[0][0]


def check_queue_length():
    with get_db_engine().connect() as conn:
        cur = conn.execute("SELECT Count(*) FROM entries")
    return cur.fetchall()[0][0]


def clear_played_songs():
    with get_db_engine().connect() as conn:
        conn.execute("DELETE FROM done_songs")
    return True


def delete_entry(id):
    with get_db_engine().connect() as conn:
        conn.execute("DELETE FROM entries WHERE id=%s", (id,))
    return True


def delete_entries(ids):
    idlist = []
    for x in ids:
        idlist.append((x,))
    try:
        with get_db_engine().connect() as conn:
            cur = conn.execute("DELETE FROM entries WHERE id=%s", idlist)

        return cur.rowcount
    except Exception as error:
        return -1


def delete_all_entries():
    with get_db_engine().connect() as conn:
        conn.execute("DELETE FROM entries")
    return True
