from flask import Flask, render_template, Response, abort, request
import helpers
import database
import os, errno
import json
app = Flask(__name__, static_url_path='/static')
@app.route("/")
def home():
    return render_template('main.html', list=database.get_list())

@app.route('/api/enqueue', methods=['POST'])
def enqueue():
    if not request.json:
        print(request.data)
        abort(400)
    name = request.json['name']
    song_id = request.json['id']
    database.add_entry(name,song_id)
    return Response('{"status":"OK"}', mimetype='text/json')

@app.route("/list")
def songlist():
    return render_template('songlist.html', list=database.get_song_list())

@app.route("/api/songs")
def songs():
    list = database.get_song_list()
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')


@app.route("/api/songs/compl/<input_string>")
def get_song_completions(input_string):
    list = database.get_song_completions(input_string=input_string)
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

if __name__ == "__main__":
    """try:
        os.remove("test.db")
        print("removed database")
    except OSError:
        print("failed to remove database")
        pass"""
    database.create_entry_table()
    database.create_list_view()
    database.import_songs(helpers.get_songs(helpers.get_catalog_url()))
    app.run(debug=True, host='0.0.0.0')
