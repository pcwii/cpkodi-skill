import requests
import json


def play_normal(kodi_path, media_type):
    if "movie" in media_type:
        pl_id = 1
    if ("album" in media_type) or ("title" in media_type) or ("artist" in media_type):
        pl_id = 0
    json_header = {'content-type': 'application/json'}
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "playlistid": int(pl_id)
            }
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
