import requests
import json


def playlist_clear(kodi_path, pl_id=1):
    json_header = {'content-type': 'application/json'}
    method = "Playlist.Clear"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "playlistid": pl_id
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return json.loads(kodi_response.text)["result"]
    except Exception as e:
        return e
