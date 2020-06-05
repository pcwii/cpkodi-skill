import requests
import json
import re
import urllib.parse

def get_requested_movies(kodi_path, search_item):
    """
        Searches the Kodi Library for movies that contain all the words in movie_name
    """
    search_words = re.split(r'\W+', str(search_item))
    # Build the filter from each word in the movie_name
    filter_key = []
    for each_word in search_words:
        search_key = {
            "field": "title",
            "operator": "contains",
            "value": each_word
        }
        filter_key.append(search_key)
    # Make the request
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetMovies"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
            ],
            "filter": {
                "and": filter_key
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        movie_list = json.loads(kodi_response.text)["result"]["movies"]
        ## remove duplicates
        clean_list = []  # this is a dict
        for each_movie in movie_list:
            movie_title = str(each_movie['label'])
            info = {
                "label": each_movie['label'],
                "movieid": each_movie['movieid']
            }
            if movie_title.lower() not in str(clean_list).lower():
                clean_list.append(info)
            else:
                if len(each_movie['label']) == len(movie_title):
                    print('found duplicate')
                else:
                    clean_list.append(info)
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None


def get_requested_music(kodi_path, search_item, search_type):
    """
        returns a music list based on the search item string and the search type
        search_type =  album, artist, label
    """
    json_header = {'content-type': 'application/json'}
    method = "AudioLibrary.GetSongs"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
                "artist",
                "duration",
                "album",
                "track"
            ],
            "filter": {
                "field": search_type,
                "operator": "contains",
                "value": search_item
            },
            "sort": {
                "order": "ascending",
                "method": "track",
                "ignorearticle": True
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        song_list = json.loads(kodi_response.text)["result"]["songs"]
        ## remove duplicates
        clean_list = []  # this is a dict
        for each_song in song_list:
            song_title = str(each_song['label'])
            info = {
                "label": each_song['label'],
                "songid": each_song['songid'],
                "artist": each_song['artist']
            }
            if song_title.lower() not in str(clean_list).lower():
                clean_list.append(info)
            else:
                if len(each_song['label']) == len(song_title):
                    print('found duplicate')
                else:
                    clean_list.append(info)
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None


def get_active_player(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "Player.GetActivePlayers"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        active_player_id = json.loads(kodi_response.text)["result"][0]["playerid"]
        active_player_type = json.loads(kodi_response.text)["result"][0]["type"]
        return active_player_id, active_player_type
    except Exception as e:
        # print(e)
        return e


def get_poster_url(kodi_path, kodi_image_path):
    json_header = {'content-type': 'application/json'}
    player_id, player_type = get_active_player(kodi_path)
    method = "Player.GetItem"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "playerid": player_id,
            "properties": [
                "art"
            ]
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        image_raw_uri = json.loads(kodi_response.text)["result"]["item"]["art"]  # ["poster"]
        if image_raw_uri:
            if "audio" in player_type:
                image_raw_uri = image_raw_uri["album.thumb"]
            else:
                image_raw_uri = image_raw_uri["poster"]
            image_raw_uri = format_image_url(image_raw_uri)
            image_url = kodi_image_path + image_raw_uri
            return image_url
        else:
            return None
    except Exception as e:
        # print(e)
        return e


def format_image_url(raw_url):
    clean_url = urllib.parse.unquote_plus(raw_url)
    urllib.parse.unquote_plus(clean_url)
    clean_url = clean_url[:-1]
    clean_url = clean_url.replace('image://', 'image%3A%2F%2F')
    clean_url = clean_url.replace('http://', 'http%253a%252f%252f')
    clean_url = clean_url.replace('/', '%252f')
    clean_url = clean_url.replace(' ', '%2520')
    return clean_url
