from mycroft.util.log import LOG
import requests
import json


def get_all_music(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "AudioLibrary.GetSongs"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
            ],
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        music_list = json.loads(kodi_response.text)["result"]["songs"]
        return music_list
    except Exception as e:
        LOG.info(e)
        return None
