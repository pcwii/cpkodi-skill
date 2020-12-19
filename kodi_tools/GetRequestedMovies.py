from mycroft.util.log import LOG
import requests
import json

def roman_to_int(input_string):
    """
    :type s: str
    :rtype: int
    """
    result_string = ""
    result_list = []
    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, 'IV': 4, 'IX': 9, 'XL': 40, 'XC': 90,
             'CD': 400, 'CM': 900}
    all_words = input_string.split()
    for each_word in all_words:
        isRoman = all(romanCheck in roman for romanCheck in each_word)
        i = 0
        num = 0
        if isRoman:
            while i < len(each_word):
                if i + 1 < len(each_word) and each_word[i:i + 2] in roman:
                    num += roman[each_word[i:i + 2]]
                    i += 2
                else:
                    num += roman[each_word[i]]
                    i += 1
            result_list.append(str(num))
        else:
            result_list.append(each_word)
    result_string = ' '.join(result_list)
    return result_string


def int_to_Roman(str_integer):
    input_num = int(str_integer)
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while input_num > 0:
        for _ in range(input_num // val[i]):
            roman_num += syb[i]
            input_num -= val[i]
        i += 1
    return roman_num

def get_requested_movies(kodi_path, search_words):
    """
        Searches the Kodi Library for movies that contain all the words in movie_name
        first we build a filter that contains each word in the requested phrase
        will only return the movies that contain the words from the utterance
        It will exclude the numbers in the utterance initially
    """
    all_numbers = [int(s) for s in search_words if s.isdigit()]
    all_words = [str(s) for s in search_words if not s.isdigit()]
    LOG.info('Searching Movies for... ' + str(search_words))
    LOG.info('Movies keydigits... ' + str(all_numbers))
    LOG.info('Movies keywords... ' + str(all_words))

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
        movie_list = json.loads(kodi_response.text)["result"]["movies"]
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
        LOG.info('Searching for Numbers in title')
        for each_number in all_numbers:
            filtered_dict = [x for x in clean_list if str(each_number) in str(x['label']).split()]
            if len(filtered_dict) > 0:
                LOG.info('Found Integers in Titles')
                clean_list = filtered_dict
            else:
                LOG.info('No Integers Found in Titles, Searching Roman Numerals for: ' + str(each_number))
                roman_value = int_to_Roman(int(each_number))
                filtered_dict = [x for x in clean_list if roman_value in str(x['label']).split()]
                if len(filtered_dict) > 0:
                    LOG.info('Found Roman Numerals in Titles')
                    clean_list = filtered_dict
                else:
                    LOG.info('No Roman Numerals in Selected Titles')
        return clean_list  # returns a dictionary of matched movies
    except Exception as e:
        print(e)
        return None

