from mycroft.util.log import LOG
import requests
import json


def get_requested_music(kodi_path, search_item, search_type):
    """
        returns a music list based on the search item string and the search type
        search_type =  album, artist, label
    """
    json_header = {'content-type': 'application/json'}
    method = "AudioLibrary.GetSongs"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
                "artist",
                "duration",
                "album",
                "track"
            ],
            "filter": {
                "field": search_type,
                "operator": "contains",
                "value": search_item
            },
            "sort": {
                "order": "ascending",
                "method": "track",
                "ignorearticle": True
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        song_list = json.loads(kodi_response.text)["result"]["songs"]
        # remove duplicates
        clean_list = []  # this is a dict
        for each_song in song_list:
            song_title = str(each_song['label'])
            info = {
                "label": each_song['label'],
                "songid": each_song['songid'],
                "artist": each_song['artist']
            }
            if song_title.lower() not in str(clean_list).lower():
                clean_list.append(info)
            else:
                if len(each_song['label']) == len(song_title):
                    LOG.info('Removing Duplicate Entries')
                else:
                    clean_list.append(info)
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None
