import requests
from bs4 import BeautifulSoup
import json
import os

data_directory = "data"
config_file = data_directory+"/config.json"

def create_data_directory():
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)


def get_catalog_url():
    r = requests.get('https://www.karafun.de/karaoke-song-list.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    url = soup.findAll('a', href=True, text='CSV')[0]['href']
    return url

def get_songs(url):
    r = requests.get(url)
    return r.text

def check_config_exists():
    return os.path.isfile(config_file)

def setup_config(app):
    if check_config_exists():
        config = json.load(open(config_file))
        with open(config_file, 'r') as handle:
            config = json.load(handle)
        print("Loaded existing config")
    else:
        config = {'username': 'admin', 'password': 'changeme'}
        with open(config_file, 'w') as handle:
            json.dump(config, handle, indent=4, sort_keys=True)
        print("Wrote new config")
    app.config['BASIC_AUTH_USERNAME'] = config['username']
    app.config['BASIC_AUTH_PASSWORD'] = config['password']