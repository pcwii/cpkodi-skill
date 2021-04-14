from mycroft.util.log import LOG
import requests
import json
from .Noop import noop

# based on show_window
def any_window(kodi_path, window_type, window_parameter):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "GUI.ActivateWindow"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "window": window_type,
            "parameters": [
                window_parameter
            ]
        },
        "id": "1"
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        noop(kodi_path)
        return kodi_response
    except Exception as e:
        LOG.error(e)

