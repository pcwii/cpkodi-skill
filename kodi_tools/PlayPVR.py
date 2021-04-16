import requests
import json
from mycroft.util.log import LOG

def play_channel_number(kodi_path, channel_number):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "channelid": channel_number
            }
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return kodi_response
    except Exception as e:
        return e

def check_channel_number(kodi_path, channel_number):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "channelid": channel_number
            }
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        kodi_response = json.loads(kodi_response.text)
        if 'error' in kodi_response.keys():
            return False
        return kodi_response
    except Exception as e:
        return e

def get_channel_list(kodi_path, channelgroupid="alltv"):
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "PVR.GetChannels"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "channelgroupid": channelgroupid
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        return json.loads(kodi_response.text)
    except Exception as e:
        return e

def find_channel(kodi_path, query):
    channel_list = get_channel_list(kodi_path)
    search_filter = query.split(' ')
    if 'error' in channel_list:
        return None
    channel_list = channel_list['result']['channels']
    if len(channel_list) > 0:
        LOG.info(channel_list)
        channel_list = [channel for channel in channel_list
                        if any(term in channel['label'] for term in search_filter)]
        def sortkey(channel):
            return(- sum(term in channel['label'] for term in search_filter))
        return sorted(channel_list, key=sortkey)
    else:
        LOG.info('No Channels Found!')
        return None
