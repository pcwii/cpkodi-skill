import requests
import json


def playlist_clear(kodi_path, media_type):
    if "movie" in media_type:
        pl_id = 1
    if ("album" in media_type) or ("title" in media_type) or ("artist" in media_type):
        pl_id = 0
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
