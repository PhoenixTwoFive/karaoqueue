from flask import Flask, render_template, abort, request, redirect, send_from_directory, jsonify
from flask.wrappers import Response
import helpers
import database
import data_adapters
import os
import json
from flask_basicauth import BasicAuth
from helpers import nocache
from werkzeug.utils import secure_filename
app = Flask(__name__, static_url_path='/static')

basic_auth = BasicAuth(app)
accept_entries = True


@app.route("/")
def home():
    if basic_auth.authenticate():
        return render_template('main_admin.html', list=database.get_list(), auth=basic_auth.authenticate(), debug=app.config['DEBUG'])
    else:
        return render_template('main.html', list=database.get_list(), auth=basic_auth.authenticate(), debug=app.config['DEBUG'])


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/enqueue', methods=['POST'])
@nocache
def enqueue():
    if not request.json:
        abort(400)
    client_id = request.json['client_id']
    if not helpers.is_valid_uuid(client_id):
        abort(400)
    name = request.json['name'].strip()
    song_id = request.json['id']
    if request.authorization:
        entry_id = database.add_entry(name, song_id, client_id)
        return Response(f"""{{"status":"OK", "entry_id":{entry_id}}}""", mimetype='text/json')
    else:
        if helpers.get_accept_entries(app):
            if not request.json:
                abort(400)
            client_id = request.json['client_id']
            if not helpers.is_valid_uuid(client_id):
                abort(400)
            name = request.json['name']
            song_id = request.json['id']
            if database.check_queue_length() < int(app.config['MAX_QUEUE']):
                if database.check_entry_quota(client_id) < int(app.config['ENTRY_QUOTA']):
                    entry_id = database.add_entry(name, song_id, client_id)
                    return Response(f"""{{"status":"OK", "entry_id":{entry_id}}}""", mimetype='text/json')
                else:
                    return Response('{"status":"Du hast bereits ' + str(database.check_entry_quota(client_id)) + ' Songs eingetragen, dies ist das Maximum an Einträgen die du in der Warteliste haben kannst."}', mimetype='text/json', status=423)
            else:
                return Response('{"status":"Die Warteschlange enthält momentan ' + str(database.check_queue_length()) + ' Einträge und ist lang genug, bitte versuche es noch einmal wenn ein paar Songs gesungen wurden."}', mimetype='text/json', status=423)
        else:
            return Response('{"status":"Currently not accepting entries"}', mimetype='text/json', status=423)


@app.route("/list")
def songlist():
    return render_template('songlist.html', list=database.get_song_list(), auth=basic_auth.authenticate(), debug=app.config['DEBUG'])


@app.route("/settings")
@nocache
@basic_auth.required
def settings():
    return render_template('settings.html', app=app, auth=basic_auth.authenticate(), themes=helpers.get_themes(), debug=app.config['DEBUG'])


@app.route("/settings", methods=['POST'])
@nocache
@basic_auth.required
def settings_post():
    entryquota = request.form.get("entryquota")
    maxqueue = request.form.get("maxqueue")
    theme = request.form.get("theme")
    username = request.form.get("username")
    password = request.form.get("password")
    changed_credentials = False
    if entryquota.isnumeric() and int(entryquota) > 0:  # type: ignore
        app.config['ENTRY_QUOTA'] = int(entryquota)  # type: ignore
    else:
        abort(400)
    if maxqueue.isnumeric and int(maxqueue) > 0:  # type: ignore
        app.config['MAX_QUEUE'] = int(maxqueue)  # type: ignore
    else:
        abort(400)
    if theme is not None and theme in helpers.get_themes():
        helpers.set_theme(app, theme)
    else:
        abort(400)
    if username != "" and username != app.config['BASIC_AUTH_USERNAME']:
        app.config['BASIC_AUTH_USERNAME'] = username
        changed_credentials = True
    if password != "":
        app.config['BASIC_AUTH_PASSWORD'] = password
        changed_credentials = True
    helpers.persist_config(app=app)
    if changed_credentials:
        return redirect("/")
    else:
        return render_template('settings.html', app=app, auth=basic_auth.authenticate(), themes=helpers.get_themes(), debug=app.config['DEBUG'])


@app.route("/api/queue")
@nocache
def queue_json():
    list = data_adapters.dict_from_rows(database.get_list())
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')


@app.route("/plays")
@nocache
@basic_auth.required
def played_list():
    return render_template('played_list.html', list=database.get_played_list(), auth=basic_auth.authenticate(), debug=app.config['DEBUG'])


@app.route("/api/songs")
@nocache
def songs():
    list = database.get_song_list()
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')


@app.route("/api/songs/update")
@nocache
@basic_auth.required
def update_songs():
    database.delete_all_entries()
    helpers.reset_current_event_id(app)
    status = database.import_songs(
        helpers.get_songs(helpers.get_catalog_url()))
    print(status)
    return Response('{"status": "%s" }' % status, mimetype='text/json')


@app.route("/api/songs/compl")  # type: ignore
@nocache
def get_song_completions(input_string=""):
    input_string = request.args.get('search', input_string)
    if input_string != "":
        result = [list(x) for x in database.get_song_completions(input_string=input_string)]
        return jsonify(result)

    else:
        return 400


@app.route("/api/songs/search")
@nocache
def query_songs_with_details(input_string=""):
    input_string = request.args.get("q", input_string)
    if input_string == "":
        return Response(status=400)
    result = []
    for x in database.get_songs_with_details(input_string):
        # Turn row into dict. Add field labels.
        result.append(dict(zip(['karafun_id', 'title', 'artist', 'year', 'duo', 'explicit', 'styles', 'languages'], x)))
    return jsonify(result)


@app.route("/api/songs/suggest")
@nocache
def query_songs_with_details_suggest(input_string=""):
    input_string = request.args.get("count", input_string)
    if input_string == "":
        return Response(status=400)
    result = []
    if not input_string.isnumeric():
        return Response(status=400)
    count: int = int(input_string)
    for x in database.get_song_suggestions(count):
        # Turn row into dict. Add field labels.
        result.append(dict(zip(['karafun_id', 'title', 'artist', 'year', 'duo', 'explicit', 'styles', 'languages'], x)))
    return jsonify(result)


@app.route("/api/songs/stats")
@nocache
# Return the data from long_term_stats as json
def get_stats():
    db_result = database.get_long_term_stats()
    data = []
    for row in db_result:
        data.append(dict(zip(['id', 'count'], row)))
    return jsonify(data)


@app.route("/api/songs/stats.csv")
@nocache
# Return data from long_term_stats as csv
def get_stats_csv():
    db_result = database.get_long_term_stats()
    csv = "Id,Playbacks\n"
    for row in db_result:
        csv += str(row[0]) + "," + str(row[1]) + "\n"
    return Response(csv, mimetype='text/csv')


@app.route("/api/songs/stats.csv", methods=['POST'])
@nocache
@basic_auth.required
# Update long_term_stats from csv
def update_stats_csv():
    if not request.files:
        abort(400)
    file = request.files['file']
    if file.filename is None:
        abort(400)
    else:
        filename = secure_filename(file.filename)
    if filename == '':
        abort(400)
    if not filename.endswith('.csv'):
        abort(400)
    if file:
        if database.import_stats(file):
            return Response('{"status": "OK"}', mimetype='text/json')
        else:
            return Response('{"status": "FAIL"}', mimetype='text/json', status=400)
    else:
        abort(400)


@app.route("/api/songs/details/<song_id>")
def get_song_details(song_id):
    result = database.get_song_details(song_id)
    if result is None:
        abort(404)
    else:
        return jsonify(dict(zip(['karafun_id', 'title', 'artist', 'year', 'duo', 'explicit', 'styles', 'languages'], result[0])))


@app.route("/api/entries/delete/<entry_id>", methods=['GET'])
@nocache
@basic_auth.required
def delete_entry_admin(entry_id):
    if database.delete_entry(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/delete/<entry_id>", methods=['POST'])
@nocache
def delete_entry_user(entry_id):
    if not request.json:
        abort(400)
    client_id = request.json['client_id']
    if not helpers.is_valid_uuid(client_id):
        abort(400)
    if database.get_raw_entry(entry_id)[3] != client_id:  # type: ignore
        abort(403)
    if database.delete_entry(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/delete", methods=['POST'])
@nocache
@basic_auth.required
def delete_entries():
    if not request.json:
        abort(400)
        return
    updates = database.delete_entries(request.json)
    if updates >= 0:
        return Response('{"status": "OK", "updates": ' + str(updates) + '}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json', status=400)


@app.route("/api/entries/mark_sung/<entry_id>")
@nocache
@basic_auth.required
def mark_sung(entry_id):
    if database.add_sung_song(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/mark_transferred/<entry_id>")
@nocache
@basic_auth.required
def mark_transferred(entry_id):
    if database.toggle_transferred(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/accept/<value>")
@nocache
@basic_auth.required
def set_accept_entries(value):
    if (value == '0' or value == '1'):
        helpers.set_accept_entries(app, bool(int(value)))
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json', status=400)


@app.route("/api/entries/accept")
@nocache
def get_accept_entries():
    accept_entries = helpers.get_accept_entries(app)
    return Response('{"status": "OK", "value": ' + str(int(accept_entries)) + '}', mimetype='text/json')


@app.route("/api/event/close")
@nocache
@basic_auth.required
def close_event():
    try:
        database.transfer_playbacks()
        database.clear_played_songs()
        database.delete_all_entries()
        helpers.reset_current_event_id(app)
        return Response('{"status": "OK"}', mimetype='text/json')
    except Exception:
        response = jsonify({"status": "FAIL", "message": "An error occured while closing the event."})
        response.status_code = 400
        return response


@app.route("/api/entries/delete_all")
@nocache
@basic_auth.required
def delete_all_entries():
    if database.delete_all_entries():
        helpers.reset_current_event_id(app)
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/login")
@basic_auth.required
def admin():
    return redirect("/", code=303)


@app.route("/api/events/current")
@nocache
def get_current_event():
    return Response('{"status": "OK", "event": "' + helpers.get_current_event_id(app) + '"}', mimetype='text/json')


def activate_job():
    with app.app_context():
        helpers.load_dbconfig(app)
        helpers.load_version(app)
        database.create_schema()
        database.create_entry_table()
        database.create_song_table()
        database.create_done_song_table()
        database.create_list_view()
        database.create_done_song_view()
        database.create_config_table()
        helpers.setup_config(app)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'private, max-age=600, no-cache, must-revalidate'
    return response


@app.context_processor
def inject_version():
    return dict(karaoqueue_version=app.config['VERSION'])


# Perform setup here so it will be executed when the module is imported by the WSGI server.
activate_job()
