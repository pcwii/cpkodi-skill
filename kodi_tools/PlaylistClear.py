import requests
import json


def playlist_clear(kodi_path, media_type):
    api_path = kodi_path + "/jsonrpc"
    if ("movie" in media_type) or ("video" in media_type) or ("tv" in media_type):
        pl_id = 1
    else:
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
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
