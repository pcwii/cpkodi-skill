#from mycroft.util.log import getLogger
#from mycroft.util.log import LOG
#from mycroft.util.parse import extract_number
import re

def numeric_replace(in_words=""):
    word_list = in_words.split()
    return_list = []
    for each_word in word_list:
        try:
            new_word = w2n.word_to_num(each_word)
        except Exception as e:
            # print(e)
            new_word = each_word
        return_list.append(new_word)
        return_string = ' '.join(str(e) for e in return_list)
    return return_string


# use regex to find any movie names found in the utterance
def get_request_details(phrase):
    request_type = "movie"
    request_subtype = None
    film_regex = r"((movie|film) (?P<Film1>.*))"
    utt_str = phrase
    film_matches = re.finditer(film_regex, utt_str, re.MULTILINE | re.DOTALL)
    for film_match_num, film_match in enumerate(film_matches):
        group_id = "Film1"
        request_details = "{group}".format(group=film_match.group(group_id))
    request_details = re.sub('\W', ' ', request_details)
    request_details = re.sub(' +', ' ', request_details)
    return request_details.strip(), request_type, request_subtype  # returns the request details and the request type


# check the cursor control utterance for repeat commands
def repeat_regex(message):
    value = extract_number(message)
    if value:
        repeat_value = value
    elif "once" in message:
        repeat_value = 1
    elif "twice" in message:
        repeat_value = 2
    else:
        repeat_value = 1
    return repeat_value
