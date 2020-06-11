from mycroft.util.log import LOG
import json
import requests


def get_active_player(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "Player.GetActivePlayers"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": "Player.GetActivePlayers",
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        print(kodi_response.text)
        if json.loads(kodi_response.text)["result"]:
            active_player_id = json.loads(kodi_response.text)["result"][0]["playerid"]
            active_player_type = json.loads(kodi_response.text)["result"][0]["type"]
        else:
            active_player_id = None
            active_player_type = None
        # {"id":1,"jsonrpc":"2.0","result":[{"playerid":1,"playertype":"internal","type":"video"}]}
        #
        return active_player_id, active_player_type
    except Exception as e:
        return None, None