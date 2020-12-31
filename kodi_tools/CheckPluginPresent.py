from mycroft.util.log import LOG
import json
import requests


# check if the youtube addon exists
def check_plugin_present(kodi_path, plugin_id):
    # "plugin.video.youtube"
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Addons.GetAddons"
    addon_video = "xbmc.addon.video"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": "1",
        "params": {
            "type": addon_video
        }
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
    except Exception as e:
        LOG.info(e)
        return False
    if plugin_id in kodi_response.text:
        return True
    else:
        return False
