import requests
import json


def play_path(kodi_path, media_path):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "file": media_path
            }
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
