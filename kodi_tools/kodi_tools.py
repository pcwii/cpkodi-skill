import requests
import json
import urllib.parse


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


