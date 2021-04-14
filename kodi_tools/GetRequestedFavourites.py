from mycroft.util.log import LOG
import requests
import json


def get_requested_favourites(kodi_path, search_data):
    """
        Returns a favourites list based on the search item string.
        Based on get_requested_music.
    """
    api_path = kodi_path + "/jsonrpc"
    json_header = {'content-type': 'application/json'}
    method = "Favourites.GetFavourites"
    search_filter = search_data.split(' ')

    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
                "window",
                "windowparameter",
                "path" ]
        }
    }

    if True:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        item_count = int(json.loads(kodi_response.text)['result']['limits']['total'])
        if item_count > 0:
            def sortkey(favourite):
                return(- sum(term in favourite for term in search_filter))
            item_list = json.loads(kodi_response.text)['result']['favourites']
            matching_list = []
            for each_favourite in item_list:
                if any(term in each_favourite['title'].lower() for term in search_filter):
                    matching_list.append(each_favourite)
            return sorted(matching_list, key=sortkey)
        else:
            LOG.info('No Favourites Found!')
            return None
