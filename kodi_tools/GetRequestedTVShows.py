from mycroft.util.log import LOG
import requests
import json


def get_tv_show(kodi_path, show_title, season_number, episode_number):
    """
        1. Need to retrieve the tvshowid based on it's name
        2. Need to retreive the episode from the season
        2. return the episode details
    """
    show_id = get_show(kodi_path, show_title)[0]['tvshowid']
    LOG.info('Found ShowID: ' + str(show_id))
    episode_details = get_episode(kodi_path, show_id, season_number, episode_number)
    print('Found Episode Details: ' + str(episode_details))
    return episode_details


def get_show(kodi_path, search_words):
    """
        1. need to confirm the TVShow (returns tvshowID)
        2. Search for VideoLibrary.GetSeasons (uses Season number as integer)
        3. Search for VideoLibrary.GetEpisodes (uses episode number as integer)
    """
    filter_key = []
    for each_word in search_words:
        search_key = {
            "field": "title",
            "operator": "contains",
            "value": each_word.strip()
        }
        filter_key.append(search_key)
    # Make the request
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetTVShows"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": "libTvShows",
        "params": {
            "properties": [
                "file",
                "thumbnail",
                "fanart"
            ],
            "filter": {
                "and": filter_key
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        item_list = json.loads(kodi_response.text)["result"]['tvshows']
        # remove duplicates
        clean_list = []  # this is a dict
        for each_item in item_list:
            item_title = str(each_item['label'])
            info = {
                "label": each_item['label'],
                "tvshowid": each_item['tvshowid'],
                "fanart": each_item['fanart'],
                "thumbnail": each_item['thumbnail'],
                "filename": each_item['file']
            }
            if item_title.lower() not in str(clean_list).lower():
                clean_list.append(info)
            else:
                if len(each_item['label']) == len(item_title):
                    print('Removing Duplicate Entries')
                else:
                    clean_list.append(info)
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None


def get_episode(kodi_path, showID, seasonNum, episodeNum):
    """
        1. need to confirm the TVShow (returns tvshowID)
        2. Search for VideoLibrary.GetSeasons (uses Season number as integer)
        3. Search for VideoLibrary.GetEpisodes (uses episode number as integer)
    """
    search_key = {
        "field": "episode",
        "operator": "contains",
        "value": int(episodeNum)
    }
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetEpisodes"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "tvshowid": showID,
            "season": seasonNum,
            "properties": [
                "season",
                "episode",
                "file",
                "fanart",
                "thumbnail",
                "playcount"
            ],
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        item_list = json.loads(kodi_response.text)["result"]["episodes"]
        for each_item in item_list:
            if each_item["episode"] == episodeNum:
                return each_item
        return None  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None
