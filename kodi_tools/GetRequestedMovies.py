from mycroft.util.log import LOG
import requests
import json
import kodi_tools.convertRoman as RomanNumerals



def get_requested_movies(kodi_path, search_words):
    """
        Searches the Kodi Library for movies that contain all the words in movie_name
        first we build a filter that contains each word in the requested phrase
        will only return the movies that contain the words from the utterance
        It will exclude the numbers in the utterance initially
    """
    all_numbers = [int(s) for s in search_words if s.isdigit()]
    all_words = [str(s) for s in search_words if not s.isdigit()]
    filter_key = []
    for each_word in all_words:
        search_key = {
            "field": "title",
            "operator": "contains",
            "value": each_word.strip()
        }
        filter_key.append(search_key)
    # Make the request
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetMovies"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
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
        # LOG.info(kodi_response.text)
        movie_list = json.loads(kodi_response.text)["result"]["movies"]
        # LOG.info('GetReqeustedMovies found: ' + str(movie_list))
        # remove duplicates
        clean_list = []  # this is a dict
        for each_movie in movie_list:
            movie_title = str(each_movie['label'])
            info = {
                "label": each_movie['label'],
                "movieid": each_movie['movieid'],
                "fanart": each_movie['fanart'],
                "thumbnail": each_movie['thumbnail'],
                "filename": each_movie['file']
            }
            if movie_title.lower() not in str(clean_list).lower():
                clean_list.append(info)
            else:
                if len(each_movie['label']) == len(movie_title):
                    LOG.info('Removing Duplicate Entries')
                else:
                    clean_list.append(info)
        '''
        At this point we have the list returned based on the words in the utterance. We will now filter again based
        on any numbers returned in the utterance. We will also check the numbers against roman numerals.
        if there are no numbers in the utterance then clean_list is retained
        '''
        for each_number in all_numbers:
            filtered_dict = [x for x in clean_list if str(each_number) in str(x['label']).split()]
            if len(filtered_dict) > 0:
                clean_list = filtered_dict
            else:
                roman_value = RomanNumerals.int_to_Roman(each_number)
                filtered_dict = [x for x in clean_list if roman_value in str(x['label']).split()]
                if len(filtered_dict) > 0:
                    clean_list = filtered_dict
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None

