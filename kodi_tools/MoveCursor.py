from mycroft.util.log import LOG
import json
import requests


# activate the kodi root menu system
def move_cursor(kodi_path, direction_kw):
    json_header = {'content-type': 'application/json'}
    method = "Input." + direction_kw.capitalize()
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
        return None
