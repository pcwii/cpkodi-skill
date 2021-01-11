from mycroft.util.log import LOG
import requests
import json


def set_volume(kodi_path, level):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Application.SetVolume"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "volume": level
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        # returns the volume that it was set to
        return json.loads(kodi_response.text)["result"]
    except Exception as e:
        return None

def mute_kodi(kodi_path):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Application.SetMute"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "mute": "toggle"
        }
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        mute_state = json.loads(kodi_response.text)["result"]
        return mute_state
    except Exception as e:
        return None