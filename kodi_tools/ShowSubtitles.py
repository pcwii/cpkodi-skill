from mycroft.util.log import LOG
import requests
import json

def show_subtitles(kodi_path):
    """
        Confirm that Koid i splaying before Executing this script
    """
    json_header = {'content-type': 'application/json'}
    method = "Player.SetSubtitle"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "playerid": 1,
            "subtitle": "on"
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        LOG.error(e)
