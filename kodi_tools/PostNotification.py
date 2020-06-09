from mycroft.util.log import LOG
import json
import requests


def post_notification(kodi_path, message):
    json_header = {'content-type': 'application/json'}
    method = "GUI.ShowNotification"
    display_timeout = 5000
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "title": "Kelsey.AI",
            "message": str(message),
            "displaytime": display_timeout,
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        return kodi_response
    except Exception as e:
        LOG.error(e)
