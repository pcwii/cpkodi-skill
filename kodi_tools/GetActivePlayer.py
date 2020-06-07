import json
import requests


def get_active_player(kodi_path):
    json_header = {'content-type': 'application/json'}
    method = "Player.GetActivePlayers"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        active_player_id = json.loads(kodi_response.text)["result"][0]["playerid"]
        active_player_type = json.loads(kodi_response.text)["result"][0]["type"]
        return active_player_id, active_player_type
    except Exception as e:
        # print(e)
        return e
