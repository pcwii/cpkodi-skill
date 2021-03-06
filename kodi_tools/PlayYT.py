from mycroft.util.log import LOG
import requests
import json


def play_yt(kodi_path, video_id):
    api_path = kodi_path + "/jsonrpc"
    LOG.info('play youtube ID: ' + str(video_id))
    if len(video_id) > 15:
        yt_link = "plugin://plugin.video.youtube/play/?playlist_id=" + video_id + "&play=1&order=shuffle"
    else:
        yt_link = "plugin://plugin.video.youtube/play/?video_id=" + video_id
    json_header = {'content-type': 'application/json'}
    method = "Player.Open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "params": {
            "item": {
                "file": yt_link
            }
        },
        "method": method,
        "id": "libPlayer"
    }
    try:
        LOG.info(yt_link)
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        LOG.info(e)
        return None
