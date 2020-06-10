from mycroft.util.log import LOG
import json
import requests

# activate the kodi root menu system
def show_root(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "GUI.ActivateWindow"
    self.kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "window": "videos",
            "parameters": [
                "library://video/"
            ]
        },
        "id": "1"
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        return kodi_response
    except Exception as e:
        LOG.error(e)
