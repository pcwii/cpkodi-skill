from mycroft.util.log import LOG
import requests
import json


# add the songid to the active playlist songid is an integer
def create_playlist(kodi_path, id_dict, media_type):
    api_path = kodi_path + "/jsonrpc"
    if ("movie" in media_type) or ("video" in media_type):
        pl_id = 1
        id_type = "movieid"
    elif "tv" in media_type:
        pl_id = 1
        id_type = "episodeid"
    else:
        pl_id = 0
        id_type = "songid"
    json_header = {'content-type': 'application/json'}
    method = "Playlist.Add"
    kodi_payload = []
    for each_id in id_dict:
        kodi_payload_item = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": {
                "playlistid": pl_id,
                "item": {
                    id_type: int(each_id)
                }
            }
        }
        kodi_payload.append(kodi_payload_item)
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        return kodi_response
    except Exception as e:
        return None

