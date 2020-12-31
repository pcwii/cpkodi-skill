from mycroft.util.log import LOG
import requests
import json


def show_window(kodi_path, window_path):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "GUI.ActivateWindow"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "window": "videos",
            "parameters": [
                window_path
            ]
        },
        "id": "1"
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        LOG.error(e)

