from mycroft.util.log import LOG
import requests
import json


def update_library(kodi_path, method):
    json_header = {'content-type': 'application/json'}
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "showdialogs": True
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        LOG.error(e)
        return None

