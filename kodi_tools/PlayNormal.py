import requests
import json


def play_normal(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "playlistid": 1
            }
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response.text
    except Exception as e:
        return e
