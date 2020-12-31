import requests
import json


def get_poster_url(kodi_path, kodi_image_path):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    player_id, player_type = get_active_player(kodi_path)
    method = "Player.GetItem"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "playerid": player_id,
            "properties": [
                "art"
            ]
        }
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        image_raw_uri = json.loads(kodi_response.text)["result"]["item"]["art"]  # ["poster"]
        if image_raw_uri:
            if "audio" in player_type:
                image_raw_uri = image_raw_uri["album.thumb"]
            else:
                image_raw_uri = image_raw_uri["poster"]
            image_raw_uri = format_image_url(image_raw_uri)
            image_url = kodi_image_path + image_raw_uri
            return image_url
        else:
            return None
    except Exception as e:
        # print(e)
        return e