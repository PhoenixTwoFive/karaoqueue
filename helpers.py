import requests
from bs4 import BeautifulSoup

def get_catalog_url():
    r = requests.get('https://www.karafun.de/karaoke-song-list.html')
    soup = BeautifulSoup(r.content, 'html.parser')
    url = soup.findAll('a', href=True, text='CSV')[0]['href']
    return url

def get_songs(url):
    r = requests.get(url)
    return r.text
