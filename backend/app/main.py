from flask import Flask, render_template, Response, abort, request, redirect
from flask_cors import CORS
import helpers
import database
import data_adapters
import os, errno
import json

from flask_basicauth import BasicAuth
from pprint import pprint
app = Flask(__name__, static_url_path='/static')

CORS(app)
basic_auth = BasicAuth(app)
accept_entries = False

@app.route("/")
def home():
    if basic_auth.authenticate():
        return render_template('main_admin.html', list=database.get_list(), auth=basic_auth.authenticate())
    else:
        return render_template('main.html', list=database.get_list(), auth=basic_auth.authenticate())

@app.route('/api/enqueue', methods=['POST'])
def enqueue():
    if accept_entries:
        if not request.json:
            print(request.data)
            abort(400)
        name = request.json['name']
        song_id = request.json['id']
        database.add_entry(name, song_id)
        return Response('{"status":"OK"}', mimetype='text/json')
    else:
        return Response('{"status":"Currently not accepting entries"}', mimetype='text/json',status=423)
    

@app.route("/list")
def songlist():
    return render_template('songlist.html', list=database.get_song_list(), auth=basic_auth.authenticate())

@app.route("/api/queue")
def queue_json():
    list = data_adapters.dict_from_rows(database.get_list())
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

@app.route("/plays")
@basic_auth.required
def played_list():
    return render_template('played_list.html', list=database.get_played_list(), auth=basic_auth.authenticate())

@app.route("/api/songs")
def songs():
    list = database.get_song_list()
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

@app.route("/api/songs/update")
@basic_auth.required
def update_songs():
#    database.delete_all_entries()
    status = database.import_songs(helpers.get_songs(helpers.get_catalog_url()))
    print(status)
    return Response('{"status": "%s" }' % status, mimetype='text/json')


@app.route("/api/songs/compl")
def get_song_completions(input_string=""):
    input_string = request.args.get('search',input_string)
    if input_string!="":
        print(input_string)
        list = database.get_song_completions(input_string=input_string)
        return Response(json.dumps(list, default=helpers.serialization_helper).encode('utf-8'), mimetype='application/json')
#        return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

    else:
        return 400


@app.route("/api/entries/delete/<entry_id>")
@basic_auth.required
def delete_entry(entry_id):
    if database.delete_entry(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/delete", methods=['POST'])
@basic_auth.required
def delete_entries():
    if not request.json:
        print(request.data)
        abort(400)
        return
    updates = database.delete_entries(request.json)
    if updates >= 0:
        return Response('{"status": "OK", "updates": '+str(updates)+'}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json', status=400)


@app.route("/api/entries/mark_sung/<entry_id>")
@basic_auth.required
def mark_sung(entry_id):
    if database.add_sung_song(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')

@app.route("/api/entries/accept/<value>")
@basic_auth.required
def set_accept_entries(value):
    global accept_entries
    if (value=='0' or value=='1'):
        accept_entries=bool(int(value))
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json', status=400)


@app.route("/api/entries/accept")
def get_accept_entries():
    global accept_entries
    return Response('{"status": "OK", "value": '+str(int(accept_entries))+'}', mimetype='text/json')
    

@app.route("/api/played/clear")
@basic_auth.required
def clear_played_songs():
    if database.clear_played_songs():
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')

@app.route("/api/entries/delete_all")
@basic_auth.required
def delete_all_entries():
    if database.delete_all_entries():
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')

@app.route("/login")
@basic_auth.required
def admin():
    return redirect("/", code=303)

@app.before_first_request
def activate_job():
    helpers.create_data_directory()
    helpers.setup_config(app)


if __name__ == "__main__":    
    app.run(debug=True, host='0.0.0.0')
