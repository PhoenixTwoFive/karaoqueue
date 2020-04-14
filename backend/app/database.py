# -*- coding: utf_8 -*-

import sqlite3
import pandas
import pymongo
from bson.regex import Regex
from io import StringIO

db_name = "karaoqueue"
song_collection_name  = "songs"
entry_collection_name = "entries"
playback_collection_name  = "played"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def open_db_client():
    mongoClient = pymongo.MongoClient("mongodb://localhost:27017")
    return mongoClient

def import_songs(song_csv):
    print("Start importing Songs...")
    client = open_db_client()
    db = client[db_name]    
    if not song_collection_name in db.list_collection_names():
        songsCollection = db[song_collection_name]
        songsCollection.create_index("karafun_id", unique=True)
        songsCollection.create_index([("title","text"),("artist","text")])
    else:
        songsCollection = db[song_collection_name]
    
    def f(x): return (x.split(","))

    df = pandas.read_csv(StringIO(song_csv), sep=';',
                         engine='python', parse_dates=["Date Added"])
    df.Styles = df.Styles.apply(f, convert_dtype=True)
    df.Languages = df.Languages.apply(f, convert_dtype=True)
    df.Duo = df.Duo.astype('bool')
    df.Explicit = df.Explicit.astype('bool')
    df.columns = map(str.lower, df.columns)
    df.rename(columns={'id': 'karafun_id'}, inplace=True)
    num_songs = df.shape[0]
    song_dict = df.to_dict('records')
    try:
        songsCollection.insert_many(song_dict)
    except pymongo.errors.BulkWriteError as bwe:
        return(bwe.details)
    finally:
        client.close()
    print("Imported songs ({} in Database)".format(num_songs))
    return("Imported songs ({} in Database)".format(num_songs))     

def get_list():
    client = open_db_client()
    db = client[db_name]
    collection = db[entry_collection_name]

    query = {}
    cursor = collection.find()

    result = {}

    try:
        for doc in cursor:
            result += doc
    finally:
        client.close()

def get_played_list():
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Abspielliste")
    return cur.fetchall()

def get_song_list():
    conn =open_db_client()
    cur = conn.cursor()
    cur.execute("SELECT Artist || \" - \" || Title AS Song, Id FROM songs;")
    return cur.fetchall()

def get_song_completions(input_string):
    client = open_db_client()
    db = client[db_name]
    collection = db[song_collection_name]

    cursor = collection.find({'$text': {'$search': input_string}}, {'_txtscr': {'$meta': 'textScore'}}, limit=30).sort([('_txtscr', {'$meta': 'textScore'})])

    result = []

    try:
        for doc in cursor:
            tmpdoc = doc
            tmpdoc["_id"] = str(tmpdoc["_id"])
            result.append(doc)
    finally:
        client.close()
    # conn = open_db_client()
    # conn.row_factory = dict_factory
    # cur = conn.cursor()
    # # Don't look, it burns...
    # prepared_string = "%{0}%".format(input_string).upper()  # "Test" -> "%TEST%"
    # print(prepared_string)
    # cur.execute(
    #     "SELECT * FROM songs WHERE REPLACE(REPLACE(REPLACE(REPLACE(UPPER( Title ),'ö','Ö'),'ü','Ü'),'ä','Ä'),'ß','ẞ') LIKE (?) LIMIT 20;", (prepared_string,))
    print(result)
    return result

def add_entry(name,song_id):
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO entries (Song_Id,Name) VALUES(?,?);", (song_id,name))
    conn.commit()
    conn.close()
    return

def add_sung_song(entry_id):
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute("""SELECT Song_Id FROM entries WHERE Id=?""",(entry_id,))
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

def clear_played_songs():
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute("DELETE FROM done_songs")
    conn.commit()
    conn.close()
    return True

def delete_entry(id):
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return True


def delete_entries(ids):
    idlist = []
    for x in ids:
        idlist.append( (x,) )
    try:
        conn = open_db_client()
        cur = conn.cursor()
        cur.executemany("DELETE FROM entries WHERE id=?", idlist)
        conn.commit()
        conn.close()
        return cur.rowcount
    except sqlite3.Error as error:
        return -1

def delete_all_entries():
    conn = open_db_client()
    cur = conn.cursor()
    cur.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return True
