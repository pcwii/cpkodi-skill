from .generateSerialID import get_id
from mycroft.util.log import LOG
import json
import requests


# activate the kodi root menu system
def move_cursor(kodi_path, direction_kw):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Input." + direction_kw.capitalize()
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
        return None

def move_cursor_batch(kodi_path, direction_kws):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    kodi_payload = [{
        "jsonrpc": "2.0",
        "method": "Input." + kw.capitalize(),
        "id": get_id()
    } for kw in direction_kws]
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e
        return None
