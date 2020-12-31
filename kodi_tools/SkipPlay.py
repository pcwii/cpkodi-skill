from mycroft.util.log import LOG
import requests
import json


def skip_play(kodi_path, dir_skip):
    """
        Confirm that Koid i splaying before Executing this script
    """
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Player.Seek"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "playerid": 1,
            "value": dir_skip
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        return kodi_response
    except Exception as e:
        LOG.error(e)
