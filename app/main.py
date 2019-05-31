from flask import Flask, render_template, Response, abort, request, redirect
import helpers
import database
import os, errno
import json
from flask_basicauth import BasicAuth
app = Flask(__name__, static_url_path='/static')

basic_auth = BasicAuth(app)

@app.route("/")
def home():
    if basic_auth.authenticate():
        return render_template('main_admin.html', list=database.get_list(), auth=basic_auth.authenticate())
    else:
        return render_template('main.html', list=database.get_list(), auth=basic_auth.authenticate())

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
    return render_template('songlist.html', list=database.get_song_list(), auth=basic_auth.authenticate())

@app.route("/api/songs")
def songs():
    list = database.get_song_list()
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

@app.route("/api/songs/update")
@basic_auth.required
def update_songs():
    database.delete_all_entries()
    status = database.import_songs(helpers.get_songs(helpers.get_catalog_url()))
    print(status)
    return Response('{"status": "%s" }' % status, mimetype='text/json')


@app.route("/api/songs/compl")
def get_song_completions(input_string=""):
    input_string = request.args.get('search',input_string)
    if input_string!="":
        print(input_string)
        list = database.get_song_completions(input_string=input_string)
        return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')

    else:
        return 400


@app.route("/api/entries/delete/<entry_id>")
@basic_auth.required
def delete_entry(entry_id):
    if database.delete_entry(entry_id):
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
    database.create_entry_table()
    database.create_song_table()
    database.create_list_view()
    helpers.setup_config(app)


if __name__ == "__main__":    
    app.run(debug=True, host='0.0.0.0')
