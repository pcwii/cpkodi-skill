from mycroft.util.log import LOG
import requests
import json

# Based on pause_player
def noop(kodi_path, player_id=1):
    """
    Sends a no-op input.  This wakes the display.
    """
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Input.ExecuteAction"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "action": "noop"
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        LOG.error(e)
