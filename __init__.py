import os
import re
import sys
import splitter
import time
import json
import random
import urllib

from importlib import reload

from .cast_tools import *
from .kodi_tools import *
from .youtube_tools import *

from websocket import create_connection

from adapt.intent import IntentBuilder

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.skills.core import intent_handler, intent_file_handler
from mycroft.util.parse import extract_number, match_one, fuzzy_match
from mycroft.util.log import LOG
# from mycroft.audio import wait_while_speaking
from mycroft.messagebus import Message
# Todo: begin GUI implementation
# from mycroft.enclosure.gui import SkillGUI
from mycroft.skills.core import resting_screen_handler

_author__ = 'PCWii'
# Release - '20201229 - Covid-19 Build'

for each_module in sys.modules:
    if "tools" in each_module:
        LOG.info("Attempting to reload tools Modules: " + str(each_module))
        reload(sys.modules[each_module])


class CPKodiSkill(CommonPlaySkill):
    def __init__(self):
        super(CPKodiSkill, self).__init__('CPKodiSkill')
        # self.gui = SkillGUI()
        self.skill_id = 'cpkodi-skill_pcwii'
        self.debug_log = False
        self.enable_chromecast = False
        self.cast_device = ""
        self.cc_device_list = ""
        self.cc_status = None
        # self.friendly_names = ""
        self.kodi_path = ""
        self.kodi_image_path = ""
        self.kodi_filesystem_path = ""
        self.notifier_bool = False
        self.regexes = {}
        self.active_library = None
        self.active_index = 0
        self.active_request = None
        self.kodi_specific_request = False
        self.artist_name = None
        self.movie_library = None
        self.settings_change_callback = self.on_websettings_changed
        self._is_setup = False

    def initialize(self):
        self.load_data_files(os.path.dirname(__file__))
        self.on_websettings_changed()
        self.add_event('recognizer_loop:wakeword', self.handle_listen)
        self.add_event('recognizer_loop:utterance', self.handle_utterance)
        self.add_event('speak', self.handle_speak)

    def on_websettings_changed(self):  # called when updating mycroft home page
        # if not self._is_setup:
        LOG.info('Websettings have changed! Updating path data')
        self.debug_log = self.settings.get("debug_log", False)
        if self.debug_log:
            LOG.info('Debug Logging now enabled!')
        self.enable_chromecast = self.settings.get("enable_chromecast", False)
        self.cast_device = self.settings.get("cast_device", "")
        if len(self.cast_device) == 0:
            self.enable_chromecast = False
        kodi_ip = self.settings.get("kodi_ip", "0.0.0.0")
        kodi_port = self.settings.get("kodi_port", "8080")
        kodi_user = self.settings.get("kodi_user", "")
        kodi_pass = self.settings.get("kodi_pass", "")
        self.kodi_path = "http://" + str(kodi_user) + ":" + str(kodi_pass) + "@" + str(kodi_ip) + ":" + str(kodi_port)
        LOG.info(self.kodi_path)
        self.kodi_image_path = "http://" + str(kodi_user) + ":" + str(kodi_pass) + "@" + str(kodi_ip) + ":" + \
                               str(kodi_port) + "/image/"
        self.kodi_filesystem_path = "http://" + str(kodi_user) + ":" + str(kodi_pass) + "@" + str(kodi_ip) + ":" + \
                                    str(kodi_port) + "/vfs/"
        self._is_setup = True

    def dLOG(self, log_message):
        if self.debug_log:
            LOG.info(str(log_message))

    def send_message(self, message):  # Sends the remote received commands to the messagebus
        self.dLOG("Sending a command to the message bus: " + message)
        payload = json.dumps({
            "type": "recognizer_loop:utterance",
            "context": "",
            "data": {
                "utterances": [message]
            }
        })
        uri = 'ws://localhost:8181/core'
        ws = create_connection(uri)
        ws.send(payload)
        ws.close()

    # listening event used for kodi notifications
    def handle_listen(self, message):
        voice_payload = "Listening"
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.error('An error was detected in: handle_listen: ' + str(e))
                self.on_websettings_changed()

    # utterance event used for kodi notifications
    def handle_utterance(self, message):
        utterance = message.data.get('utterances')
        voice_payload = utterance
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                self.dLOG('An error was detected in: handle_utterance, ' + str(e))
                self.on_websettings_changed()

    # mycroft speaking event used for kodi notificatons
    def handle_speak(self, message):
        voice_payload = message.data.get('utterance')
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                self.dLOG('An error was detected in: handle_speak, ' + str(e))
                self.on_websettings_changed()

    def translate_regex(self, regex):
        """
            All requests types are added here and return the requested items
            A <item>.type.regex should exist in the local/en-us
        """
        self.regexes = {}
        self.dLOG("Using Regex: " + regex)
        if regex not in self.regexes:
            filename = regex + '.rx'
            location = os.path.dirname(os.path.realpath(__file__))
            path = location + '/./regex/en-us/' + filename  # Todo: This is not language agnostic
            # path = self.find_resource(filename)
            self.dLOG("Regex Path: " + path)
            if path:
                with open(path) as f:
                    string = f.read().strip()
                self.regexes[regex] = string
            else:
                return None
        else:
            return None
        return str(self.regexes[regex])

    def convert_multiplicative(self, message):
        """
            This routine will take words like once, twice, three times and convert them to numbers 1, 2, 3
            Since it uses a file we can ensure it is language agnostic
            This routine replaces the get_repeat_words routine
        """
        repeat_value = 0
        value = re.findall(r'\d+', message)
        if value:
            repeat_value = value[0]
            self.dLOG("Multiplicative returning the value, " + str(repeat_value))
        else:
            data = self.load_object_file("MultiplicativeList.json")
            self.dLOG(str(data))
            for each_item in data:
                if each_item in message:
                    repeat_value = data[each_item]
                    self.dLOG("Multiplicative returning the value, " + str(repeat_value))
                    break
        return int(repeat_value)

    def split_compound(self, sentence):
        """
            Used to split compound words that are found in the utterance
            This will make it easier to confirm that all words are found in the search if we filter each part of
            the compound word
        """
        search_words = re.split(r'\W+', str(sentence))
        separator = " "
        raw_list = splitter.split(separator.join(search_words))
        words_list = [list_item.strip() for list_item in raw_list]
        return words_list

    def load_object_file(self, filename):  # loads the workout file json
        location = os.path.dirname(os.path.realpath(__file__))
        object_file = location + '/./json_objects/' + filename  # get the current skill parent directory path
        with open(object_file) as json_file:
            data = json.load(json_file)
            return data

    def get_request_info(self, phrase):
        """
        Retrieve the base data structure form the json file
        parse the phrase with regex to determine what is being requested
        populate the dataStructure accordingly
        """
        request_info = self.load_object_file("baseDataStructure.json")
        # self.dLOG(str(request_info))
        request_info['utterance'] = phrase
        """
        play the movie spiderman 2 with chromecast
        *passed*
        (the|some|)(?P<castItem>.+)(?=\s+(from|with|using|on) chromecast)
        """
        cast_type = re.match(self.translate_regex('cast.type'), phrase)
        if cast_type:
            self.dLOG('Chromecast Type Detected')
            request_info['chromecast']['item'] = cast_type.groupdict()['castItem']
            request_info['chromecast']['active'] = True
            phrase = str(request_info['chromecast']['item'])
        """
        play third day from youtube
        *passed*
        (the|some|)(?P<ytItem>.+)(?=\s+(from|with|using|on) youtube)
        """
        youtube_type = re.match(self.translate_regex('youtube.type'), phrase)
        if youtube_type:  # youtube request "the official captain marvel trailer from youtube"
            self.dLOG('Youtube Type Detected')
            request_info['youtube']['item'] = youtube_type.groupdict()['ytItem']
            request_info['youtube']['active'] = True
        match_album_artist_type = re.match(self.translate_regex('album.artist.type'), phrase)
        match_song_artist_type = re.match(self.translate_regex('song.artist.type'), phrase)
        album_type = re.match(self.translate_regex('album.type'), phrase)
        song_type = re.match(self.translate_regex('song.type'), phrase)
        artist_type = re.match(self.translate_regex('artist.type'), phrase)
        if match_album_artist_type and not request_info['youtube']['active']:
            self.dLOG('album and Artist Type Detected')
            request_info['music']['album'] = match_album_artist_type.groupdict()['album']
            request_info['music']['artist'] = match_album_artist_type.groupdict()['artist']
            request_info['music']['active'] = True
        elif match_song_artist_type and not request_info['youtube']['active']:
            self.dLOG('Song and Artist Type Detected')
            request_info['music']['title'] = match_song_artist_type.groupdict()['title']
            request_info['music']['artist'] = match_song_artist_type.groupdict()['artist']
            request_info['music']['active'] = True
        else:
            self.dLOG('Checking other song types')
            """
            play the song eye on it
            *passed*
            (the |)(song|single) (?P<title>.+)
            """
            if song_type and not request_info['youtube']['active']:
                self.dLOG('Song Type Detected')
                request_info['music']['title'] = song_type.groupdict()['title']
                request_info['music']['active'] = True
            """
            play the artist toby mac
            (the |)(artist|group|band|(something|anything|stuff|music|songs) (by|from)|(some|by)) (?P<artist>.+)
            """
            if artist_type and not request_info['youtube']['active']:
                self.dLOG('Artist Type Detected')
                request_info['music']['artist'] = artist_type.groupdict()['artist']
                request_info['music']['active'] = True
            """
            play the album eye on it
            *passed*
            (the |)(album|disc|lp|cd) (?P<album>.+)
            """
            if album_type and not request_info['youtube']['active']:
                self.dLOG('Album Type Detected')
                request_info['music']['album'] = album_type.groupdict()['album']
                request_info['music']['active'] = True
        """
        play the movie spiderman homecoming
        *passed*
        (the |)(movie|film) (?P<movie>.+)
        """
        movie_type = re.match(self.translate_regex('movie.type'), phrase)
        if movie_type and not request_info['youtube']['active']:  # Movies
            self.dLOG('Movie Type Detected')
            request_info['movies']['title'] = movie_type.groupdict()['movie']
            request_info['movies']['active'] = True
        """
        play a movie
        *passed*
        (a|random|some|any) (?=.*(movie|film))(?P<random>.+)
        """
        random_movie_type = re.match(self.translate_regex('random.movie.type'), phrase)
        if random_movie_type and not request_info['youtube']['active']:
            self.dLOG('Random Movie Type Detected')
            request_info['random'] = True
            request_info['movies']['active'] = True
        """
        play some music
        *failed, random and music artist*
        (a|random|some|any) (?=.*(music|song))(?P<random>.+)
        """
        random_music_type = re.match(self.translate_regex('random.music.type'), phrase)
        if random_music_type and not request_info['youtube']['active']:  # rand
            self.dLOG('Random Music Type Detected')
            request_info['random'] = True
            request_info['music']['active'] = True
        """
        play the outer limits season 1 episode 2
        (.*?)(?P<showname>.*)(season (?P<season>\d{1,3}))(.+episode (?P<episode>\d{1,3}))
        """
        show_details_type = re.match(self.translate_regex('show.details'), phrase)
        if show_details_type and not request_info['youtube']['active']:  # TV Shows
            self.dLOG('TV Show Type Detected')
            request_info['tv']['title'] = show_details_type.groupdict()['showname']
            request_info['tv']['season'] = show_details_type.groupdict()['season']
            request_info['tv']['episode'] = show_details_type.groupdict()['episode']
            request_info['tv']['active'] = True
            request_info['tv']['type'] = "all"
        else:
            """
            play the tv show stargirl
            (the |)(tv|)(show) (?P<showname>.+)     
            """
            show_type = re.match(self.translate_regex('show.type'), phrase)
            if show_details_type and not request_info['youtube']['active']:  # TV Shows
                self.dLOG('Show Details Type Detected')
                request_info['tv']['title'] = show_type.groupdict()['showname']
                request_info['tv']['active'] = True
                request_info['tv']['type'] = "title"
        """
        specify with Kodi
        (the |some|)(?P<kodiItem>.+)(?=\s+(from|with|using|on) kodi)
        """
        kodi_request = re.match(self.translate_regex('with.kodi'), phrase)
        if kodi_request:  # kodi was specifically requested in the utterance
            self.dLOG('Kodi Type Detected')
            request_info['kodi']['active'] = True
            request_info['kodi']['item'] = kodi_request.groupdict()['kodiItem']
        """
        specify with chromecast
        (the |some|)(?P<castItem>.+)(?=\s+(from|with|using|on) chromecast)
        """
        cast_request = re.match(self.translate_regex('with.chromecast'), phrase)
        if self.enable_chromecast and cast_request:  # kodi was specifically requested in the utterance
            self.dLOG('Cast Type Detected')
            request_info['chromecast']['active'] = True
            request_info['chromecast']['item'] = cast_request.groupdict()['castItem']
        request_info['activeItem'] = (request_info['youtube']['active'] or
                                      request_info['tv']['active'] or
                                      request_info['music']['active'] or
                                      request_info['movies']['active'])
        return request_info

    def CPS_match_query_phrase(self, phrase):
        """
            The method is invoked by the PlayBackControlSkill.
            It should check to see if this skill can play the requested media
            Phrase is provided without the word "play"
            We imediatly check for the kodi specific request and strip this from the phase
        """
        # Todo: Handle Cinemavision options
        # Todo: Cinemavision is not expected to function in the next Kodi Release
        self.dLOG('CPKodiSkill received the following phrase: ' + phrase)
        if not self._is_setup:
            self.dLOG('CPKodi Skill must be setup at the home.mycroft.ai')
            self.on_websettings_changed()
            return None
        # try:
        if True:
            request_data = self.get_request_info(phrase)  # Parse the utterance (phrase)
            self.dLOG('Phrase was parsed with the following request... ' + str(request_data))
            if not request_data['activeItem']:
                self.dLOG('GetRequest returned None, no regex matches were found')
                return None
            else:  # Active regex data was parsed
                if request_data['movies']['active']:
                    if request_data['random']:
                        # Extend the CPS timeout while we search the whole library
                        self.bus.emit(Message('play:query.response', {"phrase": phrase,
                                                                      "skill_id": self.skill_id,
                                                                      "searching": True}))
                        self.dLOG('Searching for Random movie')
                        results = self.random_movie_select()
                    else:
                        word_list = self.split_compound(request_data['movies']['title'])
                        results = get_requested_movies(self.kodi_path, word_list)
                if request_data['music']['active']:
                    # Extend the CPS timeout while we search the whole library
                    self.bus.emit(Message('play:query.response', {"phrase": phrase,
                                                                  "skill_id": self.skill_id,
                                                                  "searching": True}))
                    if request_data['random']:
                        self.dLOG('Searching for Random music')
                        results = self.random_music_select()
                    else:
                        results = get_requested_music(self.kodi_path, request_data['music'])  # Type is not required
                        self.dLOG("Found: " + str(results))
                if request_data['tv']['active']:
                    request_type = request_data['tv']['type']
                    if "all" in request_type:
                        results = get_tv_show(self.kodi_path, request_data['tv'])
                    if "title" in request_type:
                        results = get_show(self.kodi_path, request_data['tv']['title'])
                        #Todo: Write tvshow file here
                if request_data['youtube']['active'] and check_plugin_present(self.kodi_path, "plugin.video.youtube"):
                    results = search_youtube(request_data['youtube']['item'])
                if results:
                    if len(results) > 0:
                        if request_data['kodi']['active']:
                            match_level = CPSMatchLevel.EXACT
                        else:
                            # match_level = CPSMatchLevel.EXACT
                            match_level = CPSMatchLevel.MULTI_KEY
                        data = {
                            "library": results,  # Contains the playlist items
                            "details": request_data  # Contains the json object for the request
                        }
                        self.dLOG('Searching kodi found a matching playable item! ' + str(match_level))
                        return phrase, match_level, data
                    else:
                        return None
                else:
                    return None

    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
            data contains the following json data
            {
                "library": results,  # Contains the playlist items
                "details": request_data  # Contains the json object for the request "baseDataStructure.json"
            }
        """
        request_data = data["details"]  # the original request data
        self.active_library = data["library"]  # a results playlist of what was found
        playlist_count = len(self.active_library)  # how many items were returned
        playlist_dict = []
        if True:
            if request_data['youtube']['active']:
                """
                    if Type is youtube then plugin and source has already been confirmed so go ahead and play
                    we only currently extract the first item in the results
                """
                if self.active_library['playlists']:  # Youtube Requests contains a playlist item
                    yt_id = self.active_library['playlists'][0]['playlistId']
                    yt_title = self.active_library['playlists'][0]['title']
                else:  # Youtube Requests does not contain a playlist item
                    yt_id = self.active_library['videos'][0]['videoId']
                    yt_title = self.active_library['videos'][0]['title']
                self.speak_dialog('play.youtube',
                                  data={"result": str(yt_title)},
                                  expect_response=False,
                                  wait=True)
                self.dLOG('Attempting to Play youtube items: ' + str(yt_title))
                play_yt(self.kodi_path, yt_id)
            if request_data['movies']['active']:
                """
                    If type is movie then ask if there are multiple, if one then add to playlist and play
                """
                self.dLOG('Preparing to Play Movie' + str(self.active_library))
                self.dLOG('Returned Library Length = ' + str(len(data["library"])))
                if len(data["library"]) == 1:  # Only one item was returned so go ahead and play
                    movie_id = str(self.active_library[0]["movieid"])
                    playlist_dict.append(movie_id)
                    if request_data['chromecast']['active']:
                        self.cast_play(movie_id)
                    else:
                        self.clear_queue_and_play(playlist_dict, 'movie')
                elif len(data["library"]) > 1:  # confirm the library does not have a zero length or is None
                    # Todo: give the option to add all items to the playlist immediately
                    self.set_context('NavigateContextKeyword', 'NavigateContext')
                    self.speak_dialog('multiple.results',
                                      data={"result": str(playlist_count)},
                                      expect_response=True,
                                      wait=True)
                else:  # no items were found in the library
                    self.speak_dialog('no.results',
                                      data={"result": str(data["request"])},
                                      expect_response=False,
                                      wait=True)
            if request_data['music']['active']:
                """
                    If type is music then add all to playlist and play
                """
                self.dLOG('Preparing to Play Music')
                for each_item in self.active_library:
                    song_id = str(each_item["songid"])
                    playlist_dict.append(song_id)
                # Todo: add the Cast Option here
                self.clear_queue_and_play(playlist_dict, 'audio')  # Pass the entire Music Structure
            if request_data['tv']['active']:
                """
                    If type is TV Episode if one then add to playlist and play
                """
                self.dLOG('Preparing to Play TV Show' + str(self.active_library))
                if len(data["library"]) == 1:  # Only one item was returned so go ahead and play
                    episode_id = str(self.active_library[0]["episodeid"])
                    playlist_dict.append(episode_id)
                    if request_data['chromecast']['active']:
                        self.cast_play(episode_id)
                    else:
                        self.clear_queue_and_play(playlist_dict, 'tv')
                elif len(data["library"]) > 1:  # confirm the library does not have a zero length or is None
                    # Todo: give the option to add all items to the playlist immediately
                    self.set_context('NavigateContextKeyword', 'NavigateContext')
                    self.speak_dialog('multiple.results',
                                      data={"result": str(playlist_count)},
                                      expect_response=True,
                                      wait=True)
                else:  # no items were found in the library
                    self.speak_dialog('no.results',
                                      data={"result": str(data["request"])},
                                      expect_response=False,
                                      wait=True)

    def store_tv_show_data(self):
        self.dLOG("Saving File..." + str(self.active_library[0]))
        # File stored in ~/.mycroft/skills/CPKodiSkill/
        with self.file_system.open("episode_details.json", "w") as f:
            f.write(str(self.active_library[0]))

    def clear_queue_and_play(self, playlist_items, playlist_type):
        result = None
        if playlist_type == "movie":
            playlist_label = str(self.active_library[0]["label"])
        else:
            playlist_label = ""
        try:
            # if True:  # Remove after testing
            result = playlist_clear(self.kodi_path, playlist_type)
            if "OK" in result.text:
                result = None
                self.dLOG("Clear Playlist Successful")
                result = create_playlist(self.kodi_path, playlist_items, playlist_type)
            if "OK" in result.text:
                result = None
                self.dLOG("Add Playlist Successful: " + str(playlist_items))
                # Todo: This displays a random image Update with proper thumbnails
                self.gui.clear()
                self.enclosure.display_manager.remove_active()
                self.gui.show_image("https://source.unsplash.com/1920x1080/?+random",
                                    "Example Long Caption That Needs Wrapping Very Long Text Example That Is",
                                    "Example Title")
                self.speak_dialog("now.playing",
                                  data={"result_type": str(playlist_type), "result_label": str(playlist_label)},
                                  expect_response=False,
                                  wait=True)
                time.sleep(2)  # wait for playlist before playback
                if "tv" in str(playlist_type):
                    self.store_tv_show_data()
                result = play_pl(self.kodi_path, playlist_type)
            if "OK" in result.text:
                self.dLOG("Now Playing..." + str(result.text))
                result = None

        except Exception as e:
            self.dLOG('An error was detected in: clear_queue_and_play')
            LOG.error(e)
            self.on_websettings_changed()


    def random_movie_select(self):
        self.dLOG('Random Movie Selected')
        full_list = get_all_movies(self.kodi_path)
        random_id = random.randint(1, len(full_list))
        random_entry = [full_list[random_id]]
        return random_entry

    def random_music_select(self):
        full_list = get_all_music(self.kodi_path)
        item_count = random.randint(10, 20)  # how many items to grab
        self.dLOG('Randomly Selecting: ' + str(item_count) + ' entries.')
        random_id = random.sample(range(len(full_list)), item_count)
        random_entry = []
        for each_id in random_id:
            # print(full_list[int(each_id)])
            random_entry.append(full_list[int(each_id)])
        return random_entry

    def cast_play(self, item_id):
        # Todo: provide dialog for multiple cast devices
        cc_devices = ""
        if len(self.cc_device_list) > 1:  # Found more than 1 CC device on network
            # Begin Context Dialog for choosing Chromecast
            self.set_context('CastContextKeyword', 'CastContext')
            self.set_context('ListCCContextKeyword', '')
            self.speak_dialog('multiple.cc.results',
                              data={"result": str(len(self.cc_device_list))},
                              expect_response=True,
                              wait=True)
        else:
            # Go ahead and cast the item since only one was CC found
            self.set_context('CastContextKeyword', '')
            self.set_context('ListCCContextKeyword', '')
            url_path = get_movie_path(self.kodi_path, item_id)
            self.dLOG("casting the file: " + url_path)
            self.cc_status = cc_cast_file(self.cast_device, url_path)
            self.dLOG(self.cc_status)

    """
        All vocal intents appear here
    """
    @intent_handler(IntentBuilder('').require('CastContextKeyword').one_of('YesKeyword', 'NoKeyword'))
    def handle_cc_decision_intent(self, message):
        """
            The user answered Yes/No to the question Would you like me to list the CC devices
        """
        self.set_context('CastContextKeyword', '')  # Clear the context
        if "YesKeyword" in message.data:
            """
                If yes was spoken the read the first item and request next steps
            """
            self.dLOG('User responded with...' + message.data.get('YesKeyword'))
            self.set_context('ListCCContextKeyword', 'ListCCContext')
            # msg_payload = str(self.active_library[self.active_index]['label'])
            # self.speak_dialog('navigate', data={"result": msg_payload}, expect_response=True)
        else:  # No was spoken to navigate the list, reading the first item
            self.dLOG('User responded with...' + message.data.get('NoKeyword'))
            self.speak_dialog('cancel',
                              expect_response=False,
                              wait=True)

    # stop kodi was requested in the utterance
    @intent_handler(IntentBuilder("").require("StopKeyword").one_of("AudioItemKeyword",
                                                                    "FilmItemKeyword",
                                                                    "KodiKeyword",
                                                                    "YoutubeKeyword",
                                                                    "ChromecastKeyword"))
    def handle_stop_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            self.dLOG(str(active_player_id) + ', ' + str(active_player_type))
            if active_player_type:
                result = stop_kodi(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    self.dLOG("Stopped")
                    self.speak_dialog('stopped',
                                      expect_response=False,
                                      wait=True)
            else:
                self.dLOG('Kodi does not appear to be playing anything at the moment')
                # Check Chromecast
                # self.cc_status = cc_stop(self.cast_device, self.cc_status["media_session_id"])
            self.on_websettings_changed()
        except Exception as e:
            self.dLOG('An error was detected in: handle_stop_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # request to Pause a playing kodi instance
    @intent_handler(IntentBuilder("").require("PauseKeyword").one_of("AudioItemKeyword",
                                                                     "FilmItemKeyword",
                                                                     "KodiKeyword",
                                                                     "YoutubeKeyword"))
    def handle_pause_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            if active_player_id is not None:
                result = pause_all(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    self.dLOG("paused")
                    self.speak_dialog('paused',
                                      expect_response=False,
                                      wait=True)
            else:
                self.dLOG('Kodi does not appear to be playing anything at the moment')
        except Exception as e:
            self.dLOG('An error was detected in: handle_pause_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # request to resume a paused kodi instance
    @intent_handler(IntentBuilder('').require("ResumeKeyword").one_of("AudioItemKeyword",
                                                                      "FilmItemKeyword",
                                                                      "KodiKeyword",
                                                                      "YoutubeKeyword"))
    def handle_resume_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            if active_player_id is not None:
                result = resume_play(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    self.dLOG("Resumed")
                    self.speak_dialog('resumed',
                                      expect_response=False,
                                      wait=True)
            else:
                self.dLOG('Kodi does not appear to be playing anything at the moment')
        except Exception as e:
            self.dLOG('An error was detected in: handle_resume_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # clear Playlists
    @intent_handler(IntentBuilder('').require("ClearKeyword").require("PlaylistKeyword").
                    one_of("AudioItemKeyword",
                           "FilmItemKeyword",
                           "KodiKeyword",
                           "YoutubeKeyword"))
    def handle_clear_playlist_intent(self, message):
        try:
            if "AudioItemKeyword" in message.data:
                result = None
                result = playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    self.dLOG("Clear Audio Playlist Successful")
            elif "FilmItemKeyword" in message.data:
                result = None
                result = playlist_clear(self.kodi_path, "video")
                if "OK" in result.text:
                    result = None
                    self.dLOG("Clear Video Playlist Successful")
            else:
                result = None
                result = playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    self.dLOG("Clear Audio Playlist Successful")
                    result = playlist_clear(self.kodi_path, "video")
                    if "OK" in result.text:
                        result = None
                        self.dLOG("Clear Video Playlist Successful")
            self.on_websettings_changed()
        except Exception as e:
            self.dLOG('An error was detected in: handle_clear_playlist_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # turn notifications on requested in the utterance
    @intent_handler(IntentBuilder('').require("NotificationKeyword").require("OnKeyword").require("KodiKeyword"))
    def handle_notification_on_intent(self, message):
        self.notifier_bool = True
        self.speak_dialog("notification.on",
                          expect_response=False,
                          wait=True)

    # turn notifications off requested in the utterance
    @intent_handler(IntentBuilder('').require("NotificationKeyword").require("OffKeyword").require("KodiKeyword"))
    def handle_notification_off_intent(self, message):
        self.notifier_bool = False
        self.speak_dialog("notification.off",
                          expect_response=False,
                          wait=True)

    # move cursor utterance
    @intent_handler(IntentBuilder('').require('MoveKeyword').require('CursorKeyword').
                    one_of('UpKeyword', 'DownKeyword', 'LeftKeyword', 'RightKeyword', 'EnterKeyword',
                           'SelectKeyword', 'BackKeyword'))
    def handle_move_cursor_intent(self, message):  # a request was made to move the kodi cursor
        """
            This routine will move the kodi cursor
            Context is set so the user only has to say the direction on future navigation
        """
        self.set_context('MoveKeyword', 'move')
        self.set_context('CursorKeyword', 'cursor')
        direction_kw = None
        if "UpKeyword" in message.data:
            direction_kw = "Up"  # these english words are required by the kodi api
        if "DownKeyword" in message.data:
            direction_kw = "Down"  # these english words are required by the kodi api
        if "LeftKeyword" in message.data:
            direction_kw = "Left"  # these english words are required by the kodi api
        if "RightKeyword" in message.data:
            direction_kw = "Right"  # these english words are required by the kodi api
        if "EnterKeyword" in message.data:
            direction_kw = "Enter"  # these english words are required by the kodi api
        if "SelectKeyword" in message.data:
            direction_kw = "Select"  # these english words are required by the kodi api
        if "BackKeyword" in message.data:
            direction_kw = "Back"  # these english words are required by the kodi api
        # repeat_count = self.get_repeat_words(message.data.get('utterance'))
        repeat_count = self.convert_multiplicative(message.data.get('utterance'))
        self.dLOG(str(direction_kw))
        if direction_kw:
            for each_count in range(0, int(repeat_count)):
                response = move_cursor(self.kodi_path, direction_kw)
                if "OK" in response.text:
                    self.speak_dialog("direction",
                                      data={"result": direction_kw},
                                      expect_response=True,
                                      wait=True)

    @intent_handler(IntentBuilder('').require('NavigateContextKeyword').one_of('YesKeyword', 'NoKeyword'))
    def handle_navigate_decision_intent(self, message):
        """
            The user answered Yes/No to the question Would you like me to list the movies
        """
        self.set_context('NavigateContextKeyword', '')  # Clear the context
        if "YesKeyword" in message.data:
            """
                If yes was spoken the read the first item and request next stesp
            """
            self.dLOG('User responded with...' + message.data.get('YesKeyword'))
            self.set_context('ListContextKeyword', 'ListContext')
            msg_payload = str(self.active_library[self.active_index]['label'])
            self.speak_dialog('navigate',
                              data={"result": msg_payload},
                              expect_response=True,
                              wait=True)
        else:  # No was spoken to navigate the list, reading the first item
            self.dLOG('User responded with...' + message.data.get('NoKeyword'))
            self.speak_dialog('cancel',
                              expect_response=False,
                              wait=True)

    @intent_handler(IntentBuilder('').require('ListContextKeyword').
                    one_of('AddKeyword', 'NextKeyword', 'StartKeyword', 'StopKeyword'))
    def handle_navigate_library_intent(self, message):
        """
            Conversational Context to handle listing of found movies
            This will walk you through each movie in the found list
        """
        last_index = len(self.active_library) - 1
        self.dLOG(
            "list length is: " + str(len(self.active_library)) + ", Processing item: " + str(self.active_index + 1))
        if "AddKeyword" in message.data:
            """
                User requested to add this item to the playlist
                Context does not change
            """
            self.dLOG('User responded with...' + message.data.get('AddKeyword'))
            playlist_dict = [self.active_library[self.active_index]['movieid']]
            create_playlist(self.kodi_path, playlist_dict, "movie")
            """
                Next we must read back the next item in the list and ask what to do
            """
            self.active_index += 1
            msg_payload = str(self.active_library[self.active_index]['label'])
            self.speak_dialog('navigate',
                              data={"result": msg_payload},
                              expect_response=True,
                              wait=True)
        elif "NextKeyword" in message.data:
            """
                User requested the next item in the list therefore we need to read back
                the next item in the list and ask what to do
                Context does not change
            """
            self.dLOG('User responded with...' + message.data.get('NextKeyword'))
            self.active_index += 1
            if self.active_index < last_index:  # We have not reached the end of the list
                msg_payload = str(self.active_library[self.active_index]['label'])
                self.speak_dialog('navigate',
                                  data={"result": msg_payload},
                                  expect_response=True,
                                  wait=True)
            else:
                self.dLOG('We have reached the last item in the list')
                msg_payload = str(self.active_library[self.active_index]['label'])
                self.speak_dialog('last.result',
                                  data={"result": msg_payload},
                                  expect_response=True,
                                  wait=True)
                self.active_index = 0
        elif "StartKeyword" in message.data:
            """
                The user requested to play the currently listed item
                Any active playlists are cleared and this item is played
                Context is cleared
            """
            self.dLOG('User responded with...' + message.data.get('StartKeyword'))
            self.set_context('ListContextKeyword', '')
            playlist_dict = [self.active_library[self.active_index]['movieid']]
            self.active_index = 0
            self.clear_queue_and_play(playlist_dict, "movie")
        elif "StopKeyword" in message.data:
            self.active_index = 0
            self.dLOG('User responded with...' + message.data.get('StopKeyword'))
            self.set_context('ListContextKeyword', '')
        else:
            self.set_context('ListContextKeyword', '')
            self.active_index = 0
            self.speak_dialog('cancel',
                              expect_response=False,
                              wait=True)

    # Adjust the volume in kodi
    @intent_handler(IntentBuilder('').require('SetsKeyword').require('KodiKeyword').require('VolumeKeyword'))
    def handle_set_volume_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        volume_level = re.findall('\d+', str_remainder)
        if volume_level:
            if int(volume_level[0]) < 101:
                new_volume = set_volume(self.kodi_path, int(volume_level[0]))
                self.dLOG("Kodi Volume Now: " + str(new_volume))
                self.speak_dialog('volume.set',
                                  data={'result': str(new_volume)},
                                  expect_response=False,
                                  wait=True)
            else:
                self.speak_dialog('volume.error',
                                  data={'result': str(int(volume_level[0]))},
                                  expect_response=False,
                                  wait=True)

    # the user requested to skip the movie timeline forward or backward
    @intent_handler(IntentBuilder('').require("SkipKeyword").optionally('KodiKeyword').optionally('FilmKeyword').
                    one_of('ForwardKeyword', 'BackwardKeyword'))
    def handle_skip_movie_intent(self, message):
        backward_kw = message.data.get("BackwardKeyword")
        if backward_kw:
            dir_skip = "smallbackward"
        else:
            dir_skip = "smallforward"
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        self.dLOG(str(active_player_id) + ', ' + str(active_player_type))
        if active_player_type:
            result = skip_play(self.kodi_path, dir_skip)
            self.dLOG('Kodi Skip Result: ' + str(result))
        else:
            self.dLOG('Kodi does not appear to be playing anything at the moment')

    # the movie information dialog was requested in the utterance
    @intent_handler(IntentBuilder('').require('VisibilityKeyword').require('InfoKeyword').
                    optionally('KodiKeyword').optionally('FilmKeyword'))
    def handle_show_movie_info_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        self.dLOG(str(active_player_id) + ', ' + str(active_player_type))
        if active_player_type:
            result = show_movie_info(self.kodi_path)
            self.dLOG('Kodi Show Info Result: ' + str(result))
        else:
            self.dLOG('Kodi does not appear to be playing anything at the moment')

    # user has requested to turn on the movie subtitles
    @intent_handler(IntentBuilder('').require("KodiKeyword").require('SubtitlesKeyword').require('OnKeyword'))
    def handle_subtitles_on_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        self.dLOG(str(active_player_id) + ', ' + str(active_player_type))
        if active_player_type:
            result = show_subtitles(self.kodi_path)
            self.dLOG('Kodi Show Subtitles Result: ' + str(result))
        else:
            self.dLOG('Kodi does not appear to be playing anything at the moment')

    # user has requested to turn off the movie subtitles
    @intent_handler(IntentBuilder('').require("KodiKeyword").require('SubtitlesKeyword').require('OffKeyword'))
    def handle_subtitles_off_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        self.dLOG(str(active_player_id) + ', ' + str(active_player_type))
        if active_player_type:
            result = hide_subtitles(self.kodi_path)
            self.dLOG('Kodi Hide Subtitles Result: ' + str(result))
        else:
            self.dLOG('Kodi does not appear to be playing anything at the moment')

    # user has requested to show the recently added movies list
    @intent_handler(IntentBuilder('').require("ListKeyword").require('RecentKeyword').require('FilmKeyword'))
    def handle_show_movies_added_intent(self, message):
        window_path = "videodb://recentlyaddedmovies/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("RecentKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed by genres
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('GenreKeyword'))
    def handle_show_movies_genres_intent(self, message):
        window_path = "videodb://movies/genres/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("GenreKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed by actor
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('ActorKeyword'))
    def handle_show_movies_actors_intent(self, message):
        window_path = "videodb://movies/actors/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("ActorKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed by studio
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('StudioKeyword'))
    def handle_show_movies_studio_intent(self, message):
        window_path = "videodb://movies/studios/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("StudioKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed by title
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('TitleKeyword'))
    def handle_show_movies_title_intent(self, message):
        window_path = "videodb://movies/titles/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("TitleKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed by movie sets
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('SetsKeyword'))
    def handle_show_movies_sets_intent(self, message):
        window_path = "videodb://movies/sets/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("SetsKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to show the movies listed all movies
    @intent_handler(IntentBuilder('').require("ListKeyword").require('AllKeyword').require('FilmKeyword'))
    def handle_show_all_movies_intent(self, message):
        window_path = "videodb://movies/sets/"
        result = show_window(self.kodi_path, window_path)
        self.dLOG('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("AllKeyword")
        self.speak_dialog('sorted.by',
                          data={"result": sort_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to refresh the movie library database
    @intent_handler(IntentBuilder('').require("CleanKeyword").require('KodiKeyword').require('LibraryKeyword'))
    def handle_clean_library_intent(self, message):
        method = "VideoLibrary.Clean"
        result = update_library(self.kodi_path, method)
        self.dLOG('Kodi Update Library Result: ' + str(result))
        # self.music_library = get_all_music(self.kodi_path)
        update_kw = message.data.get("CleanKeyword")
        self.speak_dialog('update.library',
                          data={"result": update_kw},
                          expect_response=False,
                          wait=True)

    # user has requested to update the movie database
    @intent_handler(IntentBuilder('').require("ScanKeyword").require('KodiKeyword').require('LibraryKeyword'))
    def handle_scan_library_intent(self, message):
        method = "VideoLibrary.Scan"
        result = update_library(self.kodi_path, method)
        self.dLOG('Kodi Update Library Result: ' + str(result))
        # self.music_library = get_all_music(self.kodi_path
        update_kw = message.data.get("ScanKeyword")
        self.speak_dialog('update.library',
                          data={"result": update_kw},
                          expect_response=False,
                          wait=True)

    @intent_handler(IntentBuilder('').require("MuteKeyword").require('KodiKeyword'))
    def handle_mute_toggle_intent(self, message):
        mute_state = mute_kodi(self.kodi_path)
        # self.speak_dialog('update.library', data={"result": update_kw}, expect_response=False)

    @intent_handler(IntentBuilder('').require("LoadKeyword").require('KodiKeyword').require('SettingsKeyword'))
    def handle_mute_toggle_intent(self, message):
        self.on_websettings_changed()
        self.speak_dialog('update.settings',
                          expect_response=False,
                          wait=True)

    # user has requested to cast something
    @intent_handler(IntentBuilder('').require("CastKeyword"))
    def handle_cast_movies_intent(self, message):
        """
            This intent will re-format the request and send it to the messagebus to be handled by the
            common play system
            "cast something" will be re-formatted to "play something with chromecast"
        """
        self.cc_device_list = cc_get_names()
        if self.enable_chromecast and self.cc_device_list:
            str_remainder = str(message.utterance_remainder())
            self.dLOG('Request to CAST something: ' + str_remainder)
            # Todo: This is not likely language agnostic
            new_request = "play " + str(str_remainder) + ' with chromecast'
            self.send_message(new_request)
        else:
            self.speak_dialog('no.chromecast',
                              expect_response=False,
                              wait=True)
            self.on_websettings_changed()
            return False  # if Chromecast is not enabled then fallback to another skill


def create_skill():
    return CPKodiSkill()
