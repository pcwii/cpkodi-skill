from os.path import dirname
import re
import sys
import splitter
import time
import json

from .kodi_tools import *
from importlib import reload

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
        except Exception as e:
            LOG.error(e)

    # listening event used for kodi notifications
    def handle_listen(self, message):
        voice_payload = "Listening"
        if self.notifier_bool:
            try:
                kodi_tools.post_notification(self.kodi_path, voice_payload)
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
                kodi_tools.post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.info('An error was detected in: handle_utterance')
                LOG.error(e)
                self.on_websettings_changed()

    # mycroft speaking event used for kodi notificatons
    def handle_speak(self, message):
        voice_payload = message.data.get('utterance')
        if self.notifier_bool:
            try:
                kodi_tools.post_notification(self.kodi_path, voice_payload)
            except Exception as e:
                LOG.info('An error was detected in: handle_speak')
                LOG.error(e)
                self.on_websettings_changed()

    # stop kodi was requested in the utterance
    @intent_handler(IntentBuilder("").require("StopKeyword").one_of("ItemKeyword", "KodiKeyword", "YoutubeKeyword"))
    def handle_stop_intent(self, message):
        try:
            active_player_id, active_player_type = kodi_tools.get_active_player(self.kodi_path)
            LOG.info(str(active_player_id), str(active_player_type))
            if active_player_type:
                result = kodi_tools.stop_kodi(self.kodi_path, active_player_id)
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
            active_player_id, active_player_type = kodi_tools.get_active_player(self.kodi_path)
            if active_player_id:
                result = kodi_tools.pause_all(self.kodi_path, active_player_id)
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
            active_player_id, active_player_type = kodi_tools.get_active_player(self.kodi_path)
            if active_player_id:
                result = kodi_tools.resume_play(self.kodi_path, active_player_id)
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
                result = kodi_tools.playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Audio Playlist Successful")
            elif "video" in message.data:
                result = None
                result = kodi_tools.playlist_clear(self.kodi_path, "video")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Video Playlist Successful")
            else:
                result = None
                result = kodi_tools.playlist_clear(self.kodi_path, "audio")
                if "OK" in result.text:
                    result = None
                    LOG.info("Clear Audio Playlist Successful")
                    result = kodi_tools.playlist_clear(self.kodi_path, "video")
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
                response = kodi_tools.move_cursor(self.kodi_path, direction_kw)
                if "OK" in response.text:
                    wait_while_speaking()
                    self.speak_dialog("direction", data={"result": direction_kw}, expect_response=True)

    @intent_handler(IntentBuilder('').require('NavigateContextKeyword').one_of('YesKeyword', 'NoKeyword'))
    def handle_navigate_decision_intent(self, message):
        """
            The user answered Yes/No to the question Would you like me to list the movies
        """
        self.set_context('NavigateContextKeyword', '') # Clear the context
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
        """
        if "AddKeyword" in message.data:
            """
                User reqested to add this item to the playlist
                Context does not change
            """
            LOG.info('User responded with...' + message.data.get('AddKeyword'))
            playlist_dict = []
            playlist_dict.append(self.active_library[self.active_index]['movieid'])
            kodi_tools.create_playlist(self.kodi_path, playlist_dict, "movie")
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
        return self.regexes[regex]

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
        # Todo This routine is not language agnostic
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


    def get_request_details(self, phrase):
        """
            matches the phrase against a series of regex's
            all files are .regex
            More types can be added to expand functions
        """
        album_type = re.match(self.translate_regex('album.type'), phrase)
        artist_type = re.match(self.translate_regex('artist.type'), phrase)
        movie_type = re.match(self.translate_regex('movie.type'), phrase)
        song_type = re.match(self.translate_regex('song.type'), phrase)
        if album_type:
            request_type = 'album'
            request_item = album_type.groupdict()['album']
        elif artist_type:
            request_type = 'artist'
            request_item = artist_type.groupdict()['artist']
        elif movie_type:
            request_type = 'movie'
            request_item = movie_type.groupdict()['movie']
        elif song_type:
            request_type = 'title'
            request_item = song_type.groupdict()['title']
        else:
            # Todo Add TV-Show types
            request_type = None
            request_item = None
        return request_item, request_type  # returns the request details and the request type

    def split_compound(self, sentance):
        """
            Used to split compound words that are found in the utterance
            This will make it easier to confirm that all words are found in the search
        """
        search_words = re.split(r'\W+', str(sentance))
        separator = " "
        words_list = splitter.split(separator.join(search_words))
        return words_list

    def CPS_match_query_phrase(self, phrase):
        """
            The method is invoked by the PlayBackControlSkill.
        """
        results = None
        LOG.info('CPKodiSkill received the following phrase: ' + phrase)
        if not self._is_setup:
            LOG.info('CPKodi Skill must be setup at the home.mycroft.ai')
            self.on_websettings_changed()
            return None
        try:
            request_item, request_type = self.get_request_details(phrase)  # extract the item name from the phrase
            if (request_item is None) or (request_type is None):
                LOG.info('GetRequest returned None')
                return None
            else:
                LOG.info("Requested search: " + str(request_item) + ", of type: " + str(request_type))
            if "movie" in request_type:
                word_list = self.split_compound(request_item)
                LOG.info(str(word_list))
                results = kodi_tools.get_requested_movies(self.kodi_path, word_list)
                # LOG.info("Possible movies matches are: " + str(results))
            if ("album" in request_type) or ("title" in request_type) or ("artist" in request_type):
                results = kodi_tools.get_requested_music(self.kodi_path, request_item, request_type)
                LOG.info("Searching for music")
            if results is None:
                LOG.info("Found Nothing!")
                return None  # no match found by this skill
            else:
                if len(results) > 0:
                    match_level = CPSMatchLevel.EXACT
                    data = {
                        "library": results,
                        "request": request_item,
                        "type": request_type
                    }
                    LOG.info('Searching kodi found a matching playable item!')
                    return phrase, match_level, data
                else:
                    return None  # until a match is found
        except Exception as e:
            LOG.info('An error was detected in: CPS_match_query_phrase')
            LOG.error(e)
            self.on_websettings_changed()

    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        LOG.info('cpkodi Library: ' + str(data["library"]))
        LOG.info('cpkodi Request: ' + str(data["request"]))
        LOG.info('cpkodi Type: ' + str(data["type"]))
        request_type = data["type"]
        self.active_library = data["library"]
        self.active_index = 0  # reinitialize the step counter for reading back the library
        playlist_count = len(self.active_library)
        playlist_type = request_type
        #LOG.info(str(self.active_library), str(playlist_type), str(playlist_count))
        playlist_dict = []
        try:
            if "movie" in playlist_type:
                """
                    If type is movie then ask if there are multiple, if one then add to playlist and play
                """
                LOG.info('Preparing to Play Movie')
                for each_item in self.active_library:
                    movie_id = str(each_item["movieid"])
                    playlist_dict.append(movie_id)
                if len(data["library"]) == 1:
                    # Only one item was returned so go ahead and play
                    self.clear_queue_and_play(playlist_dict, playlist_type)
                elif len(data["library"]):  # confirm the library does not have a zero length or is None
                    self.set_context('NavigateContextKeyword', 'NavigateContext')
                    wait_while_speaking()
                    self.speak_dialog('multiple.results', data={"result": str(playlist_count)}, expect_response=True)
                else:
                    wait_while_speaking()
                    self.speak_dialog('no.results', data={"result": str(data["request"])}, expect_response=False)
            if ("album" in playlist_type) or ("title" in playlist_type) or ("artist" in playlist_type):
                """
                    If type is music then add all to playlist and play
                """
                LOG.info('Preparing to Play Music')
                for each_item in self.active_library:
                    song_id = str(each_item["songid"])
                    playlist_dict.append(song_id)
                self.clear_queue_and_play(playlist_dict, playlist_type)
        except Exception as e:
            LOG.info('An error was detected in: CPS_match_query_phrase')
            LOG.error(e)
            self.on_websettings_changed()

    def clear_queue_and_play(self, playlist_items, playlist_type):
        result = None
        try:
            result = kodi_tools.playlist_clear(self.kodi_path, playlist_type)
            if "OK" in result.text:
                result = None
                LOG.info("Clear Playlist Successful")
                result = kodi_tools.create_playlist(self.kodi_path, playlist_items, playlist_type)
            if "OK" in result.text:
                result = None
                LOG.info("Add Playlist Successful")
                wait_while_speaking()
                self.speak_dialog("now.playing", data={"result_type": str(playlist_type)}, expect_response=False)
                result = kodi_tools.play_normal(self.kodi_path, playlist_type)
            if "OK" in result.text:
                result = None
                LOG.info("Now Playing...")
        except Exception as e:
            LOG.info('An error was detected in: clear_queue_and_play')
            LOG.error(e)
            self.on_websettings_changed()


def create_skill():
    return CPKodiSkill()
