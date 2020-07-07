from os.path import dirname
import re
import sys
import splitter
import time
import json
import random
# from threading import Timer
# import threading


from .kodi_tools import *
from importlib import reload
import urllib.error
import urllib.parse
import urllib.request


from adapt.intent import IntentBuilder

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.skills.core import intent_handler, intent_file_handler

from mycroft.util.parse import extract_number, match_one, fuzzy_match
from mycroft.util.log import LOG

from mycroft.audio import wait_while_speaking

from mycroft.messagebus import Message


_author__ = 'PCWii'
# Release - '20200603 - Covid-19 Build'

for each_module in sys.modules:
    if "kodi_tools" in each_module:
        LOG.info("Attempting to reload Kodi_tools Module: " + str(each_module))
        reload(sys.modules[each_module])


class CPKodiSkill(CommonPlaySkill):
    def __init__(self):
        super(CPKodiSkill, self).__init__('CPKodiSkill')
        self.kodi_path = ""
        self.kodi_image_path = ""
        self._is_setup = False
        self.notifier_bool = False
        self.regexes = {}
        self.active_library = None
        self.active_index = 0
        self.active_request = None
        self.kodi_specific_request = False
        self.artist_name = None
        self.skill_id = 'cpkodi-skill_pcwii'
        #self.music_library = None
        #self.read_library_thread = threading.Thread(target=self.update_library)
        # self.settings_change_callback = self.on_websettings_changed

    def initialize(self):
        self.load_data_files(dirname(__file__))
        self.on_websettings_changed()
        self.add_event('recognizer_loop:wakeword', self.handle_listen)
        self.add_event('recognizer_loop:utterance', self.handle_utterance)
        self.add_event('speak', self.handle_speak)


    def on_websettings_changed(self):  # called when updating mycroft home page
        # if not self._is_setup:
        LOG.info('Websettings have changed! Updating path data')
        kodi_ip = self.settings.get("kodi_ip", "192.168.0.32")
        kodi_port = self.settings.get("kodi_port", "8080")
        kodi_user = self.settings.get("kodi_user", "")
        kodi_pass = self.settings.get("kodi_pass", "")
        try:
            if kodi_ip and kodi_port:
                kodi_ip = self.settings["kodi_ip"]
                kodi_port = self.settings["kodi_port"]
                kodi_user = self.settings["kodi_user"]
                kodi_pass = self.settings["kodi_pass"]
                self.kodi_path = "http://" + kodi_user + ":" + kodi_pass + "@" + kodi_ip + ":" + str(kodi_port) + \
                                 "/jsonrpc"
                LOG.info(self.kodi_path)
                self.kodi_image_path = "http://" + kodi_ip + ":" + str(kodi_port) + "/image/"
                self._is_setup = True
                #self.music_library = get_all_music(self.kodi_path)
        except Exception as e:
            LOG.error(e)

    # listening event used for kodi notifications
    def handle_listen(self, message):
        voice_payload = "Listening"
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.info('An error was detected in: handle_listen')
                LOG.error(e)
                self.on_websettings_changed()

    # utterance event used for kodi notifications
    def handle_utterance(self, message):
        utterance = message.data.get('utterances')
        voice_payload = utterance
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.info('An error was detected in: handle_utterance')
                LOG.error(e)
                self.on_websettings_changed()

    # mycroft speaking event used for kodi notificatons
    def handle_speak(self, message):
        voice_payload = message.data.get('utterance')
        if self.notifier_bool:
            try:
                post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.info('An error was detected in: handle_speak')
                LOG.error(e)
                self.on_websettings_changed()

    def translate_regex(self, regex):
        """
            All requests types are added here and return the requested items
            A <item>.type.regex should exist in the local/en-us
        """
        self.regexes = {}
        if regex not in self.regexes:
            path = self.find_resource(regex + '.regex')
            if path:
                with open(path) as f:
                    string = f.read().strip()
                self.regexes[regex] = string
            else:
                return None
        else:
            return None
        return str(self.regexes[regex])

    def convert_cardinal(self, message):
        """
            This routine will take words like once, twice, three times and convert them to numbers 1, 2, 3
            Since it uses a file we can ensure it is language agnostic
            This routine replaces the get_repeat_words routine
        """
        value = extract_number(message)
        path = self.find_resource("CardrdinalList.json")
        if value:
            repeat_value = value
            return repeat_value
        else:
            with open(path) as f:
                data = json.load(f)
            LOG.info(str(data))
            for each_item in data:
                for cardinal, value in each_item.items():
                    print(cardinal, value)  # example usage
                    if cardinal in message:
                        repeat_value = value
                        return repeat_value

    def get_repeat_words(self, message):
        # Todo This routine is not language agnostic, use regex files
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

    def split_compound(self, sentance):
        """
            Used to split compound words that are found in the utterance
            This will make it easier to confirm that all words are found in the search
        """
        search_words = re.split(r'\W+', str(sentance))
        separator = " "
        words_list = splitter.split(separator.join(search_words))
        return words_list

    def get_request_info(self, phrase):
        request_info = {
            'utternace': phrase,
            'random': False,
            'activeItem': False,
            'requestItem': phrase,
            'kodi': {
                'active': False,
                'item': None
            },
            'youtube': {
                'item': None,
                'active': False
            },
            'music': {
                'type': None,
                'album': None,
                'title': None,
                'artist': None,
                'active': False
            },
            'tv': {
                'title': None,
                'season': None,
                'episode': None,
                'active': False
            },
            'movies': {
                'title': None,
                'active': False
            },
        }
        """
        play third day from youtube
        *passed*
        (the|some|)(?P<ytItem>.+)(?=\s+(from|with|using|on) youtube)
        """
        youtube_type = re.match(self.translate_regex('youtube.type'), phrase)
        if youtube_type:  # youtube request "the official captain marvel trailer from youtube"
            request_info['youtube']['item'] = youtube_type.groupdict()['ytItem']
            request_info['youtube']['active'] = True
        """
        play the album eye on it
        *passed*
        (the |)(album|disc|lp|cd) (?P<album>.+)
        """
        album_type = re.match(self.translate_regex('album.type'), phrase)
        if album_type:
            request_info['music']['type'] = 'album'
            request_info['music']['album'] = album_type.groupdict()['album']
            request_info['music']['active'] = True
        """
        play the song eye on it
        *passed*
        (the |)(song|single) (?P<title>.+)
        """
        song_type = re.match(self.translate_regex('song.type'), phrase)
        if song_type:
            request_info['music']['type'] = 'title'
            request_info['music']['title'] = song_type.groupdict()['title']
            request_info['music']['active'] = True
        """
        play the artist toby mac
        (the |)(artist|group|band|(something|anything|stuff|music|songs) (by|from)|(some|by)) (?P<artist>.+)
        """
        artist_type = re.match(self.translate_regex('artist.type'), phrase)
        if artist_type:
            request_info['music']['type'] = 'artist'
            request_info['music']['artist'] = artist_type.groupdict()['artist']
            request_info['music']['active'] = True
        """
        play the movie spiderman homecoming
        *passed*
        (the |)(movie|film) (?P<movie>.+)
        """
        movie_type = re.match(self.translate_regex('movie.type'), phrase)
        if movie_type:  # Movies
            request_info['movies']['title'] = movie_type.groupdict()['movie']
            request_info['movies']['active'] = True
        """
        play a movie
        *passed*
        (a|random|some|any) (?=.*(movie|film))(?P<random>.+)
        """
        random_movie_type = re.match(self.translate_regex('random.movie.type'), phrase)
        if random_movie_type:
            request_info['random'] = True
            request_info['movies']['active'] = True
        """
        play some music
        *faild, random and music artist*
        (a|random|some|any) (?=.*(music|song))(?P<random>.+)
        """
        random_music_type = re.match(self.translate_regex('random.music.type'), phrase)
        if random_music_type:  # rand
            request_info['random'] = True
            request_info['music']['active'] = True
        """
        play the outer limits season 1 episode 2
        (the\s+|)(?P<showname>.+)(?=\s+season)(?P<episode>.+)       
        """
        show_details_type = re.match(self.translate_regex('show.details.type'), phrase)
        if show_details_type:  # TV Shows
            request_info['tv']['title'] = show_details_type.groupdict()['showname']
            request_info['tv']['details'] = show_details_type.groupdict()['episode']
            """
            (season (?P<season>\d{1,3}))(.+episode (?P<episode>\d{1,3}))
            """
            show_details = re.match(self.translate_regex('show.details'), str(request_info['tv']['details']))
            if show_details:
                request_info['tv']['season'] = int(show_details.groupdict()['season'])
                request_info['tv']['episode'] = int(show_details.groupdict()['episode'])
                request_info['tv']['active'] = True
        """
        play the tv show stargirl
        (the |)(tv|)(show) (?P<showname>.+)     
        """
        show_type = re.match(self.translate_regex('show.type'), phrase)
        if show_details_type:  # TV Shows
            request_info['tv']['title'] = show_type.groupdict()['showname']
            request_info['tv']['active'] = True
            #ToDo: get last episode played
        """
        specify with Kodi
        (the |some|)(?P<kodiItem>.+)(?=\s+(from|with|using|on) kodi)
        """
        kodi_request = re.match(self.translate_regex('with.kodi'), phrase)
        if kodi_request:  # kodi was specifically requested in the utterance
            request_info['kodi']['active'] = True
            request_info['kodi']['item'] = kodi_request.groupdict()['kodiItem']
        # Todo: need to correct item requested from utterance
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
        # LOG.info(str(self.get_request_info(phrase)))
        # Todo: Handle Cinemavision options
        # Todo: Handle Youtube searches
        LOG.info('CPKodiSkill received the following phrase: ' + phrase)
        if not self._is_setup:
            LOG.info('CPKodi Skill must be setup at the home.mycroft.ai')
            self.on_websettings_changed()
            return None
        # try:
        if True:
            #request_data = self.get_request_details(phrase)  # extract the item name from the phrase
            request_data = self.get_request_info(phrase)
            if not request_data['activeItem']:
                LOG.info('GetRequest returned None, no regex matches were found')
                return None
            else:
            if request_data['movies']['active']:
                if request_data['random']:
                    # Extend the CPS timeout while we search the whole library
                    self.bus.emit(Message('play:query.response', {"phrase": phrase,
                                                                  "skill_id": self.skill_id,
                                                                  "searching": True}))
                    results = self.random_movie_select()
                else:
                    word_list = self.split_compound(request_data['movies']['title'])
                    results = get_requested_movies(self.kodi_path, word_list)
            if request_data['music']['active']:
                if request_data['random']:
                    # Extend the CPS timeout while we search the whole library
                    self.bus.emit(Message('play:query.response', {"phrase": phrase,
                                                                  "skill_id": self.skill_id,
                                                                  "searching": True}))
                    results = self.random_music_select()
                else:
                    request_type = request_data['music']['type']
                    request_item = request_data['music'][request_type]
                    results = get_requested_music(self.kodi_path, request_item, request_type)
            if request_data['youtube']['active'] and check_plugin_present(self.kodi_path, "plugin.video.youtube"):
                results = self.get_youtube_links(request_data['youtube']['item'])
            else:
                if len(results) > 0:
                    if request_data['kodi']['active']:
                        match_level = CPSMatchLevel.EXACT
                    else:
                        # match_level = CPSMatchLevel.EXACT
                        match_level = CPSMatchLevel.MULTI_KEY
                    data = {
                        "library": results,
                        "details": request_data
                    }
                    LOG.info('Searching kodi found a matching playable item! ' + str(match_level))
                    return phrase, match_level, data
                else:
                    return None  # until a match is found

    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        request_data = data["details"]  # the original data
        self.active_library = data["library"]  # a results list of what was found
        playlist_count = len(self.active_library)  # how many items were returned
        playlist_dict = []
        try:
            if request_data['youtube']['active']:
                """
                    if Type is youtube then plugin and source has already been confirmed so go ahead and play
                """
                wait_while_speaking()
                self.speak_dialog('play.youtube', data={"result": self.active_request}, expect_response=False)
                LOG.info('Attempting to Play youtube items: ' + str(self.active_library))
                play_yt(self.kodi_path, self.active_library[0])
            if request_data['movies']['active']:
                """
                    If type is movie then ask if there are multiple, if one then add to playlist and play
                """
                LOG.info('Preparing to Play Movie')
                for each_item in self.active_library:
                    movie_id = str(each_item["movieid"])
                    playlist_dict.append(movie_id)
                if len(data["library"]) == 1:
                    # Only one item was returned so go ahead and play
                    self.clear_queue_and_play(playlist_dict, 'movie')
                elif len(data["library"]):  # confirm the library does not have a zero length or is None
                    # Todo: give the option to add all items to the playlist imediatly
                    self.set_context('NavigateContextKeyword', 'NavigateContext')
                    wait_while_speaking()
                    self.speak_dialog('multiple.results', data={"result": str(playlist_count)}, expect_response=True)
                else:
                    wait_while_speaking()
                    self.speak_dialog('no.results', data={"result": str(data["request"])}, expect_response=False)
            if request_data['music']['active']:
                """
                    If type is music then add all to playlist and play
                """
                LOG.info('Preparing to Play Music')
                for each_item in self.active_library:
                    song_id = str(each_item["songid"])
                    playlist_dict.append(song_id)
                self.clear_queue_and_play(playlist_dict, request_data['music']['type'])
        except Exception as e:
            LOG.info('An error was detected in: CPS_match_query_phrase')
            LOG.error(e)
            self.on_websettings_changed()

    def clear_queue_and_play(self, playlist_items, playlist_type):
        result = None
        try:
            result = playlist_clear(self.kodi_path, playlist_type)
            if "OK" in result.text:
                result = None
                LOG.info("Clear Playlist Successful")
                result = create_playlist(self.kodi_path, playlist_items, playlist_type)
            if "OK" in result.text:
                result = None
                LOG.info("Add Playlist Successful")
                wait_while_speaking()
                self.speak_dialog("now.playing", data={"result_type": str(playlist_type)}, expect_response=False)
                time.sleep(2) # wait for playlist before playback
                result = play_normal(self.kodi_path, playlist_type)
            if "OK" in result.text:
                LOG.info("Now Playing..." + str(result.text))
                result = None
        except Exception as e:
            LOG.info('An error was detected in: clear_queue_and_play')
            LOG.error(e)
            self.on_websettings_changed()

    def random_movie_select(self):
        LOG.info('Random Movie Selected')
        full_list = get_all_movies(self.kodi_path)
        random_id = random.randint(1, len(full_list))
        selected_entry = full_list[random_id]
        return selected_entry

    def random_music_select(self):
        full_list = get_all_music(self.kodi_path)
        item_count = random.randint(10, 20)  # how many items to grab
        LOG.info('Randomly Selecting: ' + str(item_count) + ' entries.')
        random_id = random.sample(range(len(full_list)), item_count)
        random_entry = []
        for each_id in random_id:
            # print(full_list[int(each_id)])
            random_entry.append(full_list[int(each_id)])
        return random_entry

    def get_youtube_links(self, search_text):
        LOG.info(search_text)
        query = urllib.parse.quote(search_text)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib.request.urlopen(url)
        html = response.read()
        # Get all video links from page
        temp_links = []
        all_video_links = re.findall(r'href=\"\/watch\?v=(.{11})', html.decode())
        for each_video in all_video_links:
            if each_video not in temp_links:
                temp_links.append(each_video)
        video_links = temp_links
        # Get all playlist links from page
        temp_links = []
        all_playlist_results = re.findall(r'href=\"\/playlist\?list\=(.{34})', html.decode())
        sep = '"'
        for each_playlist in all_playlist_results:
            if each_playlist not in temp_links:
                cleaned_pl = each_playlist.split(sep, 1)[0]
                temp_links.append(cleaned_pl)
        playlist_links = temp_links
        yt_links = []
        if video_links:
            yt_links.append("?video_id=" + video_links[0])
        if playlist_links:
            yt_links.append("?playlist_id=" + playlist_links[0] + "&play=1&order=shuffle")
        return yt_links

    """
        All vocal intents apear here
    """
    # stop kodi was requested in the utterance
    @intent_handler(IntentBuilder("").require("StopKeyword").one_of("ItemKeyword", "KodiKeyword", "YoutubeKeyword"))
    def handle_stop_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            LOG.info(str(active_player_id) + ', ' + str(active_player_type))
            if active_player_type:
                result = stop_kodi(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    LOG.info("Stopped")
                    self.speak_dialog('stopped', expect_response=False)
            else:
                LOG.info('Kodi does not appear to be playing anything at the moment')
        except Exception as e:
            LOG.info('An error was detected in: handle_stop_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # request to Pause a playing kodi instance
    @intent_handler(IntentBuilder("").require("PauseKeyword").one_of("ItemKeyword", "KodiKeyword", "YoutubeKeyword"))
    def handle_pause_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            if active_player_id:
                result = pause_all(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    LOG.info("paused")
                    self.speak_dialog('paused', expect_response=False)
            else:
                LOG.info('Kodi does not appear to be playing anything at the moment')
        except Exception as e:
            LOG.info('An error was detected in: handle_pause_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # request to resume a paused kodi instance
    @intent_handler(IntentBuilder('').require("ResumeKeyword").one_of("ItemKeyword", "KodiKeyword", "YoutubeKeyword"))
    def handle_resume_intent(self, message):
        try:
            active_player_id, active_player_type = get_active_player(self.kodi_path)
            if active_player_id:
                result = resume_play(self.kodi_path, active_player_id)
                if "OK" in result.text:
                    LOG.info("Resumed")
                    self.speak_dialog('resumed', expect_response=False)
            else:
                LOG.info('Kodi does not appear to be playing anything at the moment')
        except Exception as e:
            LOG.info('An error was detected in: handle_resume_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # clear Playlists
    @intent_handler(IntentBuilder('').require("ClearKeyword").require("PlaylistKeyword").
                    one_of("ItemKeyword", "KodiKeyword", "YoutubeKeyword"))
    def handle_clear_playlist_intent(self, message):
        try:
            if "audio" in message.data:
                result = None
                result = playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Audio Playlist Successful")
            elif "video" in message.data:
                result = None
                result = playlist_clear(self.kodi_path, "video")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Video Playlist Successful")
            else:
                result = None
                result = playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Audio Playlist Successful")
                    result = playlist_clear(self.kodi_path, "video")
                    if "OK" in result.text:
                        result = None
                        LOG.info("Clear Video Playlist Successful")
        except Exception as e:
            LOG.info('An error was detected in: handle_clear_playlist_intent')
            LOG.error(e)
            self.on_websettings_changed()

    # turn notifications on requested in the utterance
    @intent_handler(IntentBuilder('').require("NotificationKeyword").require("OnKeyword").require("KodiKeyword"))
    def handle_notification_on_intent(self, message):
        self.notifier_bool = True
        self.speak_dialog("notification.on")

    # turn notifications off requested in the utterance
    @intent_handler(IntentBuilder('').require("NotificationKeyword").require("OffKeyword").require("KodiKeyword"))
    def handle_notification_off_intent(self, message):
        self.notifier_bool = False
        self.speak_dialog("notification.off")

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
        repeat_count = self.get_repeat_words(message.data.get('utterance'))
        if direction_kw:
            for each_count in range(0, int(repeat_count)):
                response = move_cursor(self.kodi_path, direction_kw)
                if "OK" in response.text:
                    wait_while_speaking()
                    self.speak_dialog("direction", data={"result": direction_kw}, expect_response=True)

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
            LOG.info('User responded with...' + message.data.get('YesKeyword'))
            self.set_context('ListContextKeyword', 'ListContext')
            msg_payload = str(self.active_library[self.active_index]['label'])
            self.speak_dialog('navigate', data={"result": msg_payload}, expect_response=True)
        else:  # No was spoken to navigate the list, reading the first item
            LOG.info('User responded with...' + message.data.get('NoKeyword'))
            self.speak_dialog('cancel', expect_response=False)

    @intent_handler(IntentBuilder('').require('ListContextKeyword').
                    one_of('AddKeyword', 'NextKeyword', 'PlayKeyword', 'StopKeyword'))
    def handle_navigate_library_intent(self, message):
        """
            Conversational Context to handle listing of found movies
            This will walk you through each movie in the found list
        """
        if "AddKeyword" in message.data:
            """
                User reqested to add this item to the playlist
                Context does not change
            """
            LOG.info('User responded with...' + message.data.get('AddKeyword'))
            playlist_dict = []
            playlist_dict.append(self.active_library[self.active_index]['movieid'])
            create_playlist(self.kodi_path, playlist_dict, "movie")
            """
                Next we must readback the next item in the list and ask what to do
            """
            self.active_index += 1
            msg_payload = str(self.active_library[self.active_index]['label'])
            wait_while_speaking()
            self.speak_dialog('navigate', data={"result": msg_payload}, expect_response=True)
        elif "NextKeyword" in message.data:
            """
                User reqested the next item in the list therfore we need to readback
                the next item in the list and ask what to do
                Context does not change
            """
            LOG.info('User responded with...' + message.data.get('NextKeyword'))
            self.active_index += 1
            msg_payload = str(self.active_library[self.active_index]['label'])
            wait_while_speaking()
            self.speak_dialog('navigate', data={"result": msg_payload}, expect_response=True)
        elif "PlayKeyword" in message.data:
            """
                The user requested to play the currently listed item
                Any active playlists are cleared and this item is played
                Context is cleared
            """
            LOG.info('User responded with...' + message.data.get('PlayKeyword'))
            self.set_context('ListContextKeyword', '')
            playlist_dict = []
            playlist_dict.append(self.active_library[self.active_index]['movieid'])
            self.clear_queue_and_play(playlist_dict, "movie")
        elif "StopKeyword" in message.data:
            LOG.info('User responded with...' + message.data.get('StopKeyword'))
            self.set_context('ListContextKeyword', '')
        else:
            self.set_context('ListContextKeyword', '')
            wait_while_speaking()
            self.speak_dialog('cancel', expect_response=False)

    # the movie information dialog was requested in the utterance
    @intent_handler(IntentBuilder('').require('SetsKeyword').require('KodiKeyword').require('VolumeKeyword'))
    def handle_set_volume_intent(self, message):
        str_remainder = str(message.utterance_remainder())
        volume_level = re.findall('\d+', str_remainder)
        if volume_level:
            if int(volume_level[0]) < 101:
                new_volume = set_volume(self.kodi_path, int(volume_level[0]))
                LOG.info("Kodi Volume Now: " + str(new_volume))
                self.speak_dialog('volume.set', data={'result': str(new_volume)}, expect_response=False)
            else:
                self.speak_dialog('volume.error', data={'result': str(int(volume_level[0]))}, expect_response=False)

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
        LOG.info(str(active_player_id), str(active_player_type))
        if active_player_type:
            result = skip_play(self.kodi_path, dir_skip)
            LOG.info('Kodi Skip Result: ' + str(result))
        else:
            LOG.info('Kodi does not appear to be playing anything at the moment')

    # the movie information dialog was requested in the utterance
    @intent_handler(IntentBuilder('').require('VisibilityKeyword').require('InfoKeyword').
                    optionally('KodiKeyword').optionally('FilmKeyword'))
    def handle_show_movie_info_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        LOG.info(str(active_player_id), str(active_player_type))
        if active_player_type:
            result = show_movie_info(self.kodi_path)
            LOG.info('Kodi Show Info Result: ' + str(result))
        else:
            LOG.info('Kodi does not appear to be playing anything at the moment')

    # user has requested to turn on the movie subtitles
    @intent_handler(IntentBuilder('').require("KodiKeyword").require('SubtitlesKeyword').require('OnKeyword'))
    def handle_subtitles_on_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        LOG.info(str(active_player_id), str(active_player_type))
        if active_player_type:
            result = show_subtitles(self.kodi_path)
            LOG.info('Kodi Show Subtitles Result: ' + str(result))
        else:
            LOG.info('Kodi does not appear to be playing anything at the moment')

    # user has requested to turn off the movie subtitles
    @intent_handler(IntentBuilder('').require("KodiKeyword").require('SubtitlesKeyword').require('OffKeyword'))
    def handle_subtitles_off_intent(self, message):
        active_player_id, active_player_type = get_active_player(self.kodi_path)
        LOG.info(str(active_player_id), str(active_player_type))
        if active_player_type:
            result = hide_subtitles(self.kodi_path)
            LOG.info('Kodi Hide Subtitles Result: ' + str(result))
        else:
            LOG.info('Kodi does not appear to be playing anything at the moment')

    # user has requested to show the recently added movies list
    @intent_handler(IntentBuilder('').require("ListKeyword").require('RecentKeyword').require('FilmKeyword'))
    def handle_show_movies_added_intent(self, message):
        window_path = "videodb://recentlyaddedmovies/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("RecentKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed by genres
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('GenreKeyword'))
    def handle_show_movies_genres_intent(self, message):
        window_path = "videodb://movies/genres/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("GenreKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed by actor
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('ActorKeyword'))
    def handle_show_movies_actors_intent(self, message):
        window_path = "videodb://movies/actors/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("ActorKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed by studio
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('StudioKeyword'))
    def handle_show_movies_studio_intent(self, message):
        window_path = "videodb://movies/studios/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("StudioKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed by title
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('TitleKeyword'))
    def handle_show_movies_title_intent(self, message):
        window_path = "videodb://movies/titles/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("TitleKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed by movie sets
    @intent_handler(IntentBuilder('').require("ListKeyword").require('FilmKeyword').require('SetsKeyword'))
    def handle_show_movies_sets_intent(self, message):
        window_path = "videodb://movies/sets/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("SetsKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to show the movies listed all movies
    @intent_handler(IntentBuilder('').require("ListKeyword").require('AllKeyword').require('FilmKeyword'))
    def handle_show_all_movies_intent(self, message):
        window_path = "videodb://movies/sets/"
        result = show_window(self.kodi_path, window_path)
        LOG.info('Kodi Show Window Result: ' + str(result))
        sort_kw = message.data.get("AllKeyword")
        self.speak_dialog('sorted.by', data={"result": sort_kw}, expect_response=False)

    # user has requested to refresh the movie library database
    @intent_handler(IntentBuilder('').require("CleanKeyword").require('KodiKeyword').require('LibraryKeyword'))
    def handle_clean_library_intent(self, message):
        method = "VideoLibrary.Clean"
        result = update_library(self.kodi_path, method)
        LOG.info('Kodi Update Library Result: ' + str(result))
        #self.music_library = get_all_music(self.kodi_path)
        update_kw = message.data.get("CleanKeyword")
        self.speak_dialog('update.library', data={"result": update_kw}, expect_response=False)

    # user has requested to update the movie database
    @intent_handler(IntentBuilder('').require("ScanKeyword").require('KodiKeyword').require('LibraryKeyword'))
    def handle_scan_library_intent(self, message):
        method = "VideoLibrary.Scan"
        result = update_library(self.kodi_path, method)
        LOG.info('Kodi Update Library Result: ' + str(result))
        #self.music_library = get_all_music(self.kodi_path
        update_kw = message.data.get("ScanKeyword")
        self.speak_dialog('update.library', data={"result": update_kw}, expect_response=False)


def create_skill():
    return CPKodiSkill()
