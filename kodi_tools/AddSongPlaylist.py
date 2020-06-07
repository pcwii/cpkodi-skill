import requests
import json


# add the songid to the active playlist songid is an integer
def add_song_playlist(kodi_path, songid_dict):
    json_header = {'content-type': 'application/json'}
    method = "Playlist.Add"
    kodi_payload = []
    for each_id in songid_dict:
        kodi_payload_item = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": {
                "playlistid": 1,
                "item": {
                    "songid": each_id
                }
            }
        }
        kodi_payload.append(kodi_payload_item)
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response.text
    except Exception as e:
        return e



