from flask import Flask, render_template, abort, request, redirect, send_from_directory, jsonify
from flask.wrappers import Response
import helpers
import database
import data_adapters
import os
import json
from flask_basicauth import BasicAuth
from helpers import nocache
app = Flask(__name__, static_url_path='/static')

basic_auth = BasicAuth(app)
accept_entries = True


@app.route("/")
def home():
    if basic_auth.authenticate():
        return render_template('main_admin.html', list=database.get_list(), auth=basic_auth.authenticate())
    else:
        return render_template('main.html', list=database.get_list(), auth=basic_auth.authenticate())


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/enqueue', methods=['POST'])
@nocache
def enqueue():
    if not request.json:
        print(request.data)
        abort(400)
    client_id = request.json['client_id']
    if not helpers.is_valid_uuid(client_id):
        print(request.data)
        abort(400)
    name = request.json['name']
    song_id = request.json['id']
    if request.authorization:
        database.add_entry(name, song_id, client_id)
        return Response('{"status":"OK"}', mimetype='text/json')
    else:
        if helpers.get_accept_entries(app):
            if not request.json:
                print(request.data)
                abort(400)
            client_id = request.json['client_id']
            if not helpers.is_valid_uuid(client_id):
                print(request.data)
                abort(400)
            name = request.json['name']
            song_id = request.json['id']
            if database.check_queue_length() < int(app.config['MAX_QUEUE']):
                if database.check_entry_quota(client_id) < int(app.config['ENTRY_QUOTA']):
                    database.add_entry(name, song_id, client_id)
                    return Response('{"status":"OK"}', mimetype='text/json')
                else:
                    return Response('{"status":"Du hast bereits ' + str(database.check_entry_quota(client_id)) + ' Songs eingetragen, dies ist das Maximum an Einträgen die du in der Warteliste haben kannst."}', mimetype='text/json', status=423)
            else:
                return Response('{"status":"Die Warteschlange enthält momentan ' + str(database.check_queue_length()) + ' Einträge und ist lang genug, bitte versuche es noch einmal wenn ein paar Songs gesungen wurden."}', mimetype='text/json', status=423)
        else:
            return Response('{"status":"Currently not accepting entries"}', mimetype='text/json', status=423)


@app.route("/list")
def songlist():
    return render_template('songlist.html', list=database.get_song_list(), auth=basic_auth.authenticate())


@app.route("/settings")
@nocache
@basic_auth.required
def settings():
    return render_template('settings.html', app=app, auth=basic_auth.authenticate(), themes=helpers.get_themes())


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
        return render_template('settings.html', app=app, auth=basic_auth.authenticate(), themes=helpers.get_themes())


@app.route("/api/queue")
@nocache
def queue_json():
    list = data_adapters.dict_from_rows(database.get_list())
    return Response(json.dumps(list, ensure_ascii=False).encode('utf-8'), mimetype='text/json')


@app.route("/plays")
@nocache
@basic_auth.required
def played_list():
    return render_template('played_list.html', list=database.get_played_list(), auth=basic_auth.authenticate())


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
    status = database.import_songs(
        helpers.get_songs(helpers.get_catalog_url()))
    print(status)
    return Response('{"status": "%s" }' % status, mimetype='text/json')


@app.route("/api/songs/compl")  # type: ignore
@nocache
def get_song_completions(input_string=""):
    input_string = request.args.get('search', input_string)
    if input_string != "":
        print(input_string)
        result = [list(x) for x in database.get_song_completions(input_string=input_string)]
        return jsonify(result)

    else:
        return 400


@app.route("/api/entries/delete/<entry_id>")
@nocache
@basic_auth.required
def delete_entry(entry_id):
    if database.delete_entry(entry_id):
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/delete", methods=['POST'])
@nocache
@basic_auth.required
def delete_entries():
    if not request.json:
        print(request.data)
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


@app.route("/api/played/clear")
@nocache
@basic_auth.required
def clear_played_songs():
    if database.clear_played_songs():
        return Response('{"status": "OK"}', mimetype='text/json')
    else:
        return Response('{"status": "FAIL"}', mimetype='text/json')


@app.route("/api/entries/delete_all")
@nocache
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
    helpers.load_dbconfig(app)
    helpers.load_version(app)
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


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
