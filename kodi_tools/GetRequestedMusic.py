from mycroft.util.log import LOG
import requests
import json


def get_requested_music(kodi_path, search_item, search_type):
    """
        returns a music list based on the search item string and the search type
        search_type =  album, artist, label
    """
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "AudioLibrary.GetSongs"
    search_filter = []
    if "artist" in search_type:
        if "title" in search_type:
            artist_words = ''.join((item for item in search_item[0] if not item.isdigit())).split()
        else:
            artist_words = ''.join((item for item in search_item if not item.isdigit())).split()
        for each_word in artist_words:  # Build a filter based on the words in the title
            search_key = {
                "field": "artist",
                "operator": "contains",
                "value": each_word.strip()
            }
            search_filter.append(search_key)
    if "title" in search_type:
        if "artist" in search_type:
            title_words = ''.join((item for item in search_item[1] if not item.isdigit())).split()
        else:
            title_words = ''.join((item for item in search_item if not item.isdigit())).split()
        for each_word in title_words:  # Build a filter based on the search words
            search_key = {
                "field": "title",
                "operator": "contains",
                "value": each_word.strip()
            }
            search_filter.append(search_key)
    # LOG.info(str(search_filter))
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
                "and": search_filter
            },
            "sort": {
                "order": "ascending",
                "method": "track",
                "ignorearticle": True
            }
        }
    }
    if True:
    #try:
        # LOG.info("payload: " + str(kodi_payload))
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        song_list = json.loads(kodi_response.text)['result']['songs']
        LOG.info(str(song_list))
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
#    except Exception as e:
#        LOG.info(e)
#        return None
