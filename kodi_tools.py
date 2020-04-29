import requests
import json
import urllib.error
import urllib.parse
import urllib.request

from mycroft.util.log import getLogger
from mycroft.util.log import LOG

import helpers

json_header = {'content-type': 'application/json'}


def extract_path_details(kodi_path):
    s = kodi_path
    start = s.find("@") + len("@")
    end = s.find("/jsonrpc")
    substring = s[start:end]
    path_items = substring.split(":")
    return path_items



def is_kodi_playing(kodi_path):
    method = "Player.GetActivePlayers"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        parse_response = json.loads(kodi_response.text)["result"]
        if not parse_response:
            playing_status = False
        else:
            playing_status = True
    except Exception as e:
        LOG.error(e)
    LOG.info("Is Kodi Playing?...", str(playing_status))
    return playing_status


def list_all_movies(kodi_path):
    method = "VideoLibrary.GetMovies"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "properties": [
            ],
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
        movie_list = json.loads(kodi_response.text)["result"]["movies"]
        return movie_list
    except Exception as e:
        LOG.info(e)
        return "NONE"


# activate the kodi root menu system
def show_root(kodi_path):
    method = "GUI.ActivateWindow"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "window": "videos",
            "parameters": [
                "library://video/"
            ]
        },
        "id": "1"
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# clear any active playlists
def clear_playlist(kodi_path):
    method = "Playlist.Clear"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "playlistid": 1
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# add the movieid to the active playlist movieid is an integer
def add_playlist(kodi_path, movieid):
    method = "Playlist.Add"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "playlistid": 1,
            "item": {
                "movieid": movieid
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# play the movie playlist with cinemavision addon, assumes the playlist is already populated
def play_cinemavision(kodi_path):
    method = "Addons.ExecuteAddon"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "addonid": "script.cinemavision",
            "params": [
                "experience", "nodialog"
            ]
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload),
                                      headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# play the movie playlist normally without any addons, assumes there are movies in the playlist
def play_normal(kodi_path):
    method = "player.open"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "item": {
                "playlistid": 1
            }
        },
        "id": 1
    }
    try:
        json_response = requests.post(kodi_path, data=json.dumps(kodi_payload),
                                           headers=json_header)
        LOG.info(json_response.text)
    except Exception as e:
        LOG.error(e)


# add the movieid to the active playlist movieid is an integer
def add_playlist(kodi_path, movieid):
    method = "Playlist.Add"
    kodi_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": {
            "playlistid": 1,
            "item": {
                "movieid": movieid
            }
        }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# pause any playing movie not youtube
def pause_movie(kodi_path):
    method = "Player.PlayPause"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "playerid": 1,
            "play": False},
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# resume any paused movies not youtube
def resume_movie(kodi_path):
    method = "Player.PlayPause"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "playerid": 1,
            "play": True},
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# check if the youtube addon exists
def check_youtube_present(kodi_path):
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
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
    except Exception as e:
        LOG.info(e)
        return False
    if "plugin.video.youtube" in kodi_response.text:
        return True
    else:
        return False

# check if the cinemavision addon exists
def check_cinemavision_present(kodi_path):
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": "Addons.GetAddons",
        "params": {
            "type": "xbmc.addon.executable"
        },
        "id": "1"
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.info(e)
        return False
    if "script.cinemavision" in kodi_response.text:
        return True
    else:
        return False

# returns the full URI of a movie from the kodi library
def get_kodi_movie_path(kodi_path, movie_name):
    movie_id = get_kodi_movie_id(movie_name)
    method = "VideoLibrary.GetMovieDetails"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {"movieid": movie_id,
                   "properties": [
                       # "art",
                       # "cast",
                       # "dateadded",
                       # "director",
                       # "fanart",
                       "file",
                       # "genre",
                       # "imdbnumber",
                       # "lastplayed",
                       # "mpaa",
                       # "originaltitle",
                       # "playcount",
                       # "plot",
                       # "plotoutline",
                       # "premiered",
                       # "rating",
                       # "runtime",
                       # "resume",
                       # "setid",
                       # "sorttitle",
                       # "streamdetails",
                       # "studio",
                       # "tagline",
                       # "thumbnail",
                       # "title",
                       # "trailer",
                       # "userrating",
                       # "votes",
                       # "writer"
                   ],
                   }
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        movie_path = json.loads(kodi_response.text)["result"]["moviedetails"]["file"]
        path_details = extract_path_details(kodi_path)
        kodi_ip = path_details[0]
        kodi_port = path_details[1]
        base_path = 'http://' + kodi_ip + ':' + kodi_port + '/vfs/'
        url_path = base_path + urllib.parse.quote(movie_path, safe='')
        LOG.info('Found Kodi Movie Path ' + url_path)
        return url_path
    except Exception as e:
        LOG.info(e)
        return "NONE"


# play the supplied video_id with the youtube addon
def play_youtube_video(kodi_path, video_id):
    LOG.info('play youtube ID: ' + str(video_id))
    method = "Player.Open"
    # Playlist links are longer than individual links
    # individual links are 11 characters long
    if len(video_id) > 11:
        yt_link = "plugin://plugin.video.youtube/play/?playlist_id=" + video_id + "&play=1&order=shuffle"
    else:
        yt_link = "plugin://plugin.video.youtube/play/?video_id=" + video_id
    kodi_payload = {
        "jsonrpc": "2.0",
        "params": {
            "item": {
                "file": yt_link
            }
        },
        "method": method,
        "id": "libPlayer"
    }
    LOG.info(yt_link)
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)

# stop any playing movie not youtube
def stop_movie(kodi_path):
    method = "Player.Stop"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "playerid": 1
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)


# push a message to the kodi notification popup
def post_kodi_notification(kodi_path, message):
    method = "GUI.ShowNotification"
    display_timeout = 5000
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "title": "Kelsey.AI",
            "message": str(message),
            "displaytime": display_timeout,
        },
        "id": 1
    }
    try:
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info(kodi_response.text)
    except Exception as e:
        LOG.error(e)

def handle_skip_movie_intent(kodi_path, message):
    method = "Player.Seek"
    backward_kw = message.data.get("BackwardKeyword")
    if backward_kw:
        dir_skip = "smallbackward"
    else:
        dir_skip = "smallforward"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": {
            "playerid": 1,
            "value": dir_skip
        },
        "id": 1
    }
    if is_kodi_playing():
        try:
            kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload),
                                          headers=json_header)
            LOG.info(kodi_response.text)
        except Exception as e:
            LOG.error(e)
    else:
        LOG.info("There is no movie playing to skip")


# play the movie based on movie ID
def play_film(kodi_path, movieid):
    clear_playlist(kodi_path)
    add_playlist(kodi_path, movieid)
    play_normal(kodi_path)

# find the movies in the library that match the optional search criteria
def find_movies_with_filter(kodi_path, title=""):
    title = helpers.numeric_replace(title)
    found_list = []  # this is a dict
    movie_list = list_all_movies(kodi_path)
    title_list = title.replace("-", "").lower().split()
    for each_movie in movie_list:
        movie_name = each_movie["label"].replace("-", "")
        movie_name = self.numeric_replace(movie_name)
        LOG.info(movie_name)
        if all(words in movie_name.lower() for words in title_list):
            LOG.info("Found " + movie_name + " : " + "MovieID: " + str(each_movie["movieid"]))
            info = {
                "label": each_movie['label'],
                "movieid": each_movie['movieid']
            }
            found_list.append(info)
    temp_list = []  # this is a dict
    for each_movie in found_list:
        movie_title = str(each_movie['label'])
        info = {
            "label": each_movie['label'],
            "movieid": each_movie['movieid']
        }
        if movie_title not in str(temp_list):
            temp_list.append(info)
        else:
            if len(each_movie['label']) == len(movie_title):
                LOG.info('found duplicate')
            else:
                temp_list.append(info)
    found_list = temp_list
    return found_list  # returns a dictionary of matched movies


# return the id of a movie from the kodi library based on its name
def get_kodi_movie_id(kodi_path, movie_name):
    found_list = find_movies_with_filter(kodi_path, movie_name)
    my_id = found_list[0]["movieid"]
    return my_id
