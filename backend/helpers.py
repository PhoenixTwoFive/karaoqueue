import requests
from bs4 import BeautifulSoup
import json
import os
import uuid
from flask import make_response, Flask
from functools import wraps, update_wrapper
from datetime import datetime
import database

def get_catalog_url():
    r = requests.get('https://www.karafun.de/karaoke-song-list.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    url = soup.findAll(
        'a', href=True, text='Verfügbar in CSV-Format')[0]['href']
    return url


def get_songs(url):
    r = requests.get(url)
    return r.text


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def check_config_exists():
    return database.check_config_table()


def load_version(app: Flask):
    if os.environ.get("SOURCE_VERSION"):
        app.config['VERSION'] = os.environ.get("SOURCE_VERSION")[0:7]  # type: ignore # noqa: E501
    elif os.path.isfile(".version"):
        with open('.version', 'r') as file:
            data = file.read().replace('\n', '')
            if data:
                app.config['VERSION'] = data
            else:
                app.config['VERSION'] = ""
    else:
        app.config['VERSION'] = ""


def load_dbconfig(app: Flask):
    if os.environ.get("FLASK_ENV") == "development":
        app.config['DBCONNSTRING'] = os.environ.get("DBSTRING")
    else:
        if os.environ.get("DEPLOYMENT_PLATFORM") == "Heroku":
            if os.environ.get("JAWSDB_MARIA_URL"):
                app.config['DBCONNSTRING'] = os.environ.get("JAWSDB_MARIA_URL")
            else:
                app.config['DBCONNSTRING'] = ""
        if os.environ.get("DEPLOYMENT_PLATFORM") == "Docker":
            if os.environ.get("DBSTRING"):
                app.config['DBCONNSTRING'] = os.environ.get("DBSTRING")
            else:
                app.config['DBCONNSTRING'] = ""
        elif os.path.isfile(".dbconn"):
            with open('.dbconn', 'r') as file:
                data = file.read().replace('\n', '')
                if data:
                    app.config['DBCONNSTRING'] = data
                else:
                    app.config['DBCONNSTRING'] = ""
        else:
            exit("No database connection string found. Cannot continue. Please set the environment variable DBSTRING or create a file .dbconn in the root directory of the project.")

# Check if config exists in DB, if not, create it.


def setup_config(app: Flask):
    if check_config_exists() == False:
        print("No config found, creating new config")
        initial_username = os.environ.get("INITIAL_USERNAME")
        initial_password = os.environ.get("INITIAL_PASSWORD")
        if initial_username is None:
            print(
                "No initial username set. Please set the environment variable INITIAL_USERNAME")
            exit()
        if initial_password is None:
            print(
                "No initial password set. Please set the environment variable INITIAL_PASSWORD")
            exit()
        default_config = {'username': initial_username,
                          'password': initial_password,
                          'entryquota': 3,
                          'maxqueue': 20,
                          'entries_allowed': 1,
                          'theme': 'default.css'}
        for key, value in default_config.items():
            database.set_config(key, value)
        print("Created new config")
    config = database.get_config_list()
    app.config['BASIC_AUTH_USERNAME'] = config['username']
    app.config['BASIC_AUTH_PASSWORD'] = config['password']
    app.config['ENTRY_QUOTA'] = config['entryquota']
    app.config['MAX_QUEUE'] = config['maxqueue']
    app.config['ENTRIES_ALLOWED'] = bool(config['entries_allowed'])
    app.config['THEME'] = config['theme']

# set queue admittance


def set_accept_entries(app: Flask, allowed: bool):
    if allowed:
        app.config['ENTRIES_ALLOWED'] = True
        database.set_config('entries_allowed', '1')
    else:
        app.config['ENTRIES_ALLOWED'] = False
        database.set_config('entries_allowed', '0')

# get queue admittance


def get_accept_entries(app: Flask) -> bool:
    state = bool(int(database.get_config('entries_allowed')))
    app.config['ENTRIES_ALLOWED'] = state
    return state


# Write settings from current app.config to DB
def persist_config(app: Flask):
    config = {'username': app.config['BASIC_AUTH_USERNAME'], 'password': app.config['BASIC_AUTH_PASSWORD'],
              'entryquota': app.config['ENTRY_QUOTA'], 'maxqueue': app.config['MAX_QUEUE']}
    for key, value in config.items():
        database.set_config(key, value)

# Get available themes from themes directory


def get_themes():
    themes = []
    for theme in os.listdir('./static/css/themes'):
        themes.append(theme)
    return themes

# Set theme


def set_theme(app: Flask, theme: str):
    if theme in get_themes():
        app.config['THEME'] = theme
        database.set_config('theme', theme)
    else:
        print("Theme not found, not setting theme.")


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()  # type: ignore
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)
