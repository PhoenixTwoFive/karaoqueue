# -*- coding: utf_8 -*-

from sqlalchemy import create_engine, engine, text
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
        sql_engine = create_engine(
            current_app.config.get("DBCONNSTRING"))  # type: ignore
    return sql_engine


def import_songs(song_csv):
    print("Start importing Songs...")
    df = pandas.read_csv(StringIO(song_csv), sep=';')
    with get_db_engine().connect() as conn:
        df.to_sql(song_table, conn, if_exists='replace',
                  index=False)
        cur = conn.execute(text("SELECT Count(Id) FROM songs"))
        num_songs = cur.fetchone()[0]  # type: ignore
        conn.commit()
    print("Imported songs ({} in Database)".format(num_songs))
    return ("Imported songs ({} in Database)".format(num_songs))


def create_entry_table():
    with get_db_engine().connect() as conn:
        stmt = text(
            f'CREATE TABLE IF NOT EXISTS `{entry_table}` (ID INTEGER PRIMARY KEY NOT NULL AUTO_INCREMENT, Song_Id INTEGER NOT NULL, Name VARCHAR(255), Client_Id VARCHAR(36), Transferred INTEGER DEFAULT 0)')
        conn.execute(stmt)
        conn.commit()


def create_done_song_table():
    with get_db_engine().connect() as conn:
        stmt = text(
            f'CREATE TABLE IF NOT EXISTS `{done_table}` (Song_Id INTEGER PRIMARY KEY NOT NULL,  Plays INTEGER)')
        conn.execute(stmt)
        conn.commit()


def create_song_table():
    with get_db_engine().connect() as conn:
        stmt = text(f"""CREATE TABLE IF NOT EXISTS `{song_table}` (
        `Id` INTEGER,
        `Title` TEXT,
        `Artist` TEXT,
        `Year` VARCHAR(4),
        `Duo` BOOLEAN,
        `Explicit` INTEGER,
        `Date Added` TIMESTAMP,
        `Styles` TEXT,
        `Languages` TEXT
        )""")
        conn.execute(stmt)
        conn.commit()


def create_list_view():
    with get_db_engine().connect() as conn:
        stmt = text("""CREATE OR REPLACE VIEW `Liste` AS
                 SELECT Name, Title, Artist, entries.Id AS entry_ID, songs.Id AS song_ID, entries.Transferred
                 FROM entries, songs
                 WHERE entries.Song_Id=songs.Id
                 ORDER BY entries.Id ASC
                 """)
        conn.execute(stmt)
        conn.commit()


def create_done_song_view():
    with get_db_engine().connect() as conn:
        stmt = text("""CREATE OR REPLACE VIEW `Abspielliste` AS
                 SELECT CONCAT(Artist," - ", Title) AS Song, Plays AS Wiedergaben
                 FROM songs, done_songs
                 WHERE done_songs.Song_Id=songs.Id""")
        conn.execute(stmt)
        conn.commit()


def create_config_table():
    with get_db_engine().connect() as conn:
        stmt = text("""CREATE TABLE IF NOT EXISTS `config` (
        `Key` VARCHAR(50) NOT NULL PRIMARY KEY,
        `Value` TEXT
        )""")
        conn.execute(stmt)
        conn.commit()


def get_list():
    with get_db_engine().connect() as conn:
        stmt = text("SELECT * FROM Liste")
        cur = conn.execute(stmt)
    return cur.fetchall()


def get_played_list():
    with get_db_engine().connect() as conn:
        stmt = text("SELECT * FROM Abspielliste")
        cur = conn.execute(stmt)
    return cur.fetchall()


def get_song_list():
    with get_db_engine().connect() as conn:
        stmt = text("SELECT Artist || \" - \" || Title AS Song, Id FROM songs;")
        cur = conn.execute(stmt)
    return cur.fetchall()


def get_song_completions(input_string):
    with get_db_engine().connect() as conn:
        prepared_string = f"%{input_string.upper()}%"
        stmt = text(
            "SELECT CONCAT(Artist, ' - ', Title) AS Song, Id FROM songs WHERE CONCAT(Artist, ' - ', Title) LIKE :prepared_string LIMIT 20;")
        cur = conn.execute(
            stmt, {"prepared_string": prepared_string})  # type: ignore
        return cur.fetchall()


def add_entry(name, song_id, client_id):
    with get_db_engine().connect() as conn:
        stmt = text(
            "INSERT INTO entries (Song_Id,Name,Client_Id) VALUES (:par_song_id,:par_name,:par_client_id);")
        conn.execute(stmt, {"par_song_id": song_id, "par_name": name,
                     "par_client_id": client_id})  # type: ignore
        conn.commit()
    return True


def add_sung_song(entry_id):
    with get_db_engine().connect() as conn:
        stmt = text("SELECT Song_Id FROM entries WHERE Id=:par_entry_id")
        cur = conn.execute(stmt, {"par_entry_id": entry_id})  # type: ignore
        song_id = cur.fetchone()[0]  # type: ignore
        stmt = text(
            "INSERT INTO done_songs (Song_Id,Plays) VALUES (:par_song_id,1) ON DUPLICATE KEY UPDATE Plays=Plays + 1;")
        conn.execute(stmt, {"par_song_id": song_id})  # type: ignore
        conn.commit()
        delete_entry(entry_id)
    return True


def toggle_transferred(entry_id):
    with get_db_engine().connect() as conn:
        cur = conn.execute(text("SELECT Transferred FROM entries WHERE ID = :par_entry_id"),
                           {"par_entry_id": entry_id})  # type: ignore
        marked = cur.fetchall()[0][0]
        if (marked == 0):
            conn.execute(text("UPDATE entries SET Transferred = 1 WHERE ID = :par_entry_id"),
                         {"par_entry_id": entry_id})  # type: ignore
        else:
            conn.execute(text("UPDATE entries SET Transferred = 0 WHERE ID = :par_entry_id"),
                         {"par_entry_id": entry_id})  # type: ignore
        conn.commit()
    return True


def check_entry_quota(client_id):
    with get_db_engine().connect() as conn:
        cur = conn.execute(text("SELECT Count(*) FROM entries WHERE entries.Client_Id = :par_client_id"),
                           {"par_client_id": client_id})  # type: ignore
    return cur.fetchall()[0][0]


def check_queue_length():
    with get_db_engine().connect() as conn:
        cur = conn.execute(text("SELECT Count(*) FROM entries"))
    return cur.fetchall()[0][0]


def clear_played_songs():
    with get_db_engine().connect() as conn:
        conn.execute(text("DELETE FROM done_songs"))
        conn.commit()
    return True


def delete_entry(id):
    with get_db_engine().connect() as conn:
        conn.execute(text("DELETE FROM entries WHERE id= :par_id"), {
                     "par_id": id})  # type: ignore
        conn.commit()
    return True


def delete_entries(ids):
    idlist = []
    for x in ids:
        idlist.append((x,))
    try:
        with get_db_engine().connect() as conn:
            cur = conn.execute(text("DELETE FROM entries WHERE id= :par_id"), {
                               "par_id": idlist})
            conn.commit()
        return cur.rowcount
    except Exception:
        return -1


def delete_all_entries() -> bool:
    with get_db_engine().connect() as conn:
        conn.execute(text("DELETE FROM entries"))
        conn.commit()
    return True


def get_config(key: str) -> str:
    try:
        with get_db_engine().connect() as conn:
            cur = conn.execute(
                text("SELECT `Value` FROM config WHERE `Key`= :par_key"), {"par_key": key})  # type: ignore
            conn.commit()
        return cur.fetchall()[0][0]
    except IndexError:
        return ""


def set_config(key: str, value: str) -> bool:
    print(f"Setting config {key} to {value}")
    with get_db_engine().connect() as conn:
        conn.execute(text(
            "INSERT INTO config (`Key`, `Value`) VALUES ( :par_key , :par_value) ON DUPLICATE KEY UPDATE `Value`= :par_value"),
            {"par_key": key, "par_value": value}
        )  # type: ignore
        conn.commit()
    return True


def get_config_list() -> dict:
    with get_db_engine().connect() as conn:
        cur = conn.execute(text("SELECT * FROM config"))
        result_dict = {}
        for row in cur.fetchall():
            result_dict[row[0]] = row[1]
    return result_dict


def check_config_table() -> bool:
    with get_db_engine().connect() as conn:
        if conn.dialect.has_table(conn, 'config'):
            # type: ignore
            # type: ignore
            if (conn.execute(text("SELECT COUNT(*) FROM config")).fetchone()[0] > 0):  # type: ignore
                return True
            else:
                return False
        else:
            return False
