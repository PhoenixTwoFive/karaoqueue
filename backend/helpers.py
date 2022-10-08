import requests
from bs4 import BeautifulSoup
import json
import os
import uuid
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

data_directory = "data"
config_file = data_directory+"/config.json"

def create_data_directory():
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)


def get_catalog_url():
    r = requests.get('https://www.karafun.de/karaoke-song-list.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    url = soup.findAll('a', href=True, text='Verfügbar in CSV-Format')[0]['href']
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
    return os.path.isfile(config_file)

def load_version(app):
    if os.environ.get("SOURCE_VERSION"):
        app.config['VERSION'] = os.environ.get("SOURCE_VERSION")[0:7] # type: ignore
    elif os.path.isfile(".version"):
        with open('.version', 'r') as file:
            data = file.read().replace('\n', '')
            if data:
                app.config['VERSION'] = data
            else:
                app.config['VERSION'] = ""
    else:
        app.config['VERSION'] = ""
        
def load_dbconfig(app):
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
            app.config['DBCONNSTRING'] = ""

def setup_config(app):
    if os.environ.get("DEPLOYMENT_PLATFORM") == "Docker":
        app.config['BASIC_AUTH_USERNAME'] = os.environ.get('BASIC_AUTH_USERNAME')
        app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('BASIC_AUTH_PASSWORD')
        app.config['ENTRY_QUOTA'] = os.environ.get('ENTRY_QUOTA')
        app.config['MAX_QUEUE'] = os.environ.get('MAX_QUEUE')
    else:
        if check_config_exists():
            config = json.load(open(config_file))
            with open(config_file, 'r') as handle:
                config = json.load(handle)
            print("Loaded existing config")
        else:
            config = {'username': 'admin', 'password': 'changeme', 'entryquota': 3, 'maxqueue': 20}
            with open(config_file, 'w') as handle:
                json.dump(config, handle, indent=4, sort_keys=True)
            print("Wrote new config")
        app.config['BASIC_AUTH_USERNAME'] = config['username']
        app.config['BASIC_AUTH_PASSWORD'] = config['password']
        app.config['ENTRY_QUOTA'] = config['entryquota']
        app.config['MAX_QUEUE'] = config['maxqueue']



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