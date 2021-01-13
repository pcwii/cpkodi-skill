from mycroft.util.log import LOG
import requests
import json


def get_tv_show(kodi_path, show_data):
    """
        1. Need to retrieve the tvshowid based on it's name
        2. Need to retreive the episode from the season
        2. return the episode details
    """
    api_path = kodi_path + "/jsonrpc"
    show_id = get_show(api_path, show_data["title"])[0]["tvshowid"]
    LOG.info('Found ShowID: ' + str(show_id))
    episode_details = get_episode(api_path, show_id, show_data)
    LOG.info('Found Episode Details: ' + str(episode_details))
    return episode_details


def get_show(api_path, search_data):
    """
        1. need to confirm the TVShow (returns tvshowID)
        2. Search for VideoLibrary.GetSeasons (uses Season number as integer)
        3. Search for VideoLibrary.GetEpisodes (uses episode number as integer)
    """
    search_filter = []
    key_words = str(search_data).split()
    for each_word in key_words:  # Build a filter based on the words in the title
        if each_word.isdigit():
            search_value = int(each_word)
        else:
            search_value = each_word.strip()
        filter_item = {
            "field": "title",
            "operator": "contains",
            "value": search_value
        }
        search_filter.append(filter_item)
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
                "and": search_filter
            }
        }
    }
    kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
    item_list = json.loads(kodi_response.text)['result']['tvshows']
    LOG.info(item_list)
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
                LOG.info('Removing Duplicate Entries')
            else:
                clean_list.append(info)
    return clean_list  # returns a dictionary of matched movies


def get_episode(api_path, show_id, show_data):
    """
        1. need to confirm the TVShow (returns tvshow_id)
        2. Search for VideoLibrary.GetSeasons (uses Season number as integer)
        3. Search for VideoLibrary.GetEpisodes (uses episode number as integer)
    """
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetEpisodes"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "tvshowid": int(show_id),
            "season": int(show_data['season']),
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
    kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
    item_list = json.loads(kodi_response.text)['result']['episodes']
    LOG.info(item_list)
    for each_item in item_list:
        if int(each_item["episode"]) == int(show_data['episode']):
            return each_item
    return None  # returns a dictionary of matched movies
