from os.path import dirname

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from mycroft.util.log import getLogger
from mycroft.util.log import LOG


from mycroft.audio import wait_while_speaking

import pafy
import pychromecast
from pychromecast.controllers.youtube import YouTubeController


import requests
import re
import time
import json
import random
import kodi_tools
import youtube_tools
import helpers


_author__ = 'PCWii'
# Release - 20120426

class CPKodiSkill(CommonPlaySkill):
    def __init__(self):
        super(CPKodiSkill, self).__init__('CPKodiSkill')
        self.kodi_path = ""
        self.youtube_id = []
        self.youtube_search = ""
        self.kodi_payload = ""
        self.cv_payload = ""
        self.list_payload = ""
        self.json_header = {'content-type': 'application/json'}
        self.json_response = ""
        self.cv_response = ""
        self.list_response = ""
        self._is_setup = False
        self.playing_status = False
        self.notifier_bool = False
        self.movie_list = []
        self.movie_index = 0
        self.cv_request = False
        self.use_cv = False
        self.device_list = ['chromecast', 'kodi'] #list the devices that can operate this skill
        self.remote_sources = ['youtube', "you tube"]
        self.remote_match = False
        self.device_match = False

    def initialize(self):
        self.load_data_files(dirname(__file__))
        # Check and then monitor for credential changes
        # self.settings.set_changed_callback(self.on_websettings_changed)
        self.settings_change_callback = self.on_websettings_changed
        self.on_websettings_changed()

        self.add_event('recognizer_loop:wakeword', self.handle_listen)
        self.add_event('recognizer_loop:utterance', self.handle_utterance)
        self.add_event('speak', self.handle_speak)

        # eg. stop the movie
        stop_film_intent = IntentBuilder("StopFilmIntent"). \
            require("StopKeyword").one_of("FilmKeyword", "KodiKeyword", "YoutubeKeyword").build()
        self.register_intent(stop_film_intent, self.handle_stop_film_intent)

        # eg. pause the movie
        pause_film_intent = IntentBuilder("PauseFilmIntent"). \
            require("PauseKeyword").one_of("FilmKeyword", "KodiKeyword").build()
        self.register_intent(pause_film_intent, self.handle_pause_film_intent)

        # eg. resume the movie
        resume_film_intent = IntentBuilder("ResumeFilmIntent"). \
            require("ResumeKeyword").require("FilmKeyword").build()
        self.register_intent(resume_film_intent, self.handle_resume_film_intent)

        # eg. turn kodi notifications on
        notification_on_intent = IntentBuilder("NotifyOnIntent"). \
            require("NotificationKeyword").require("OnKeyword"). \
            require("KodiKeyword").build()
        self.register_intent(notification_on_intent, self.handle_notification_on_intent)

        # eg. turn kodi notifications off
        notification_off_intent = IntentBuilder("NotifyOffIntent"). \
            require("NotificationKeyword").require("OffKeyword"). \
            require("KodiKeyword").build()
        self.register_intent(notification_off_intent, self.handle_notification_off_intent)

    def on_websettings_changed(self):  # called when updating mycroft home page
        # if not self._is_setup:
        LOG.info('Websettings have changed! Updating path data')
        kodi_ip = self.settings.get("kodi_ip", "192.168.0.32")
        kodi_port = self.settings.get("kodi_port", "8080")
        kodi_user = self.settings.get("kodi_user", "")
        kodi_pass = self.settings.get("kodi_pass", "")
        try:
            if kodi_ip and kodi_port:
                kodi_ip = self.settings["kodi_ip"  ]
                kodi_port = self.settings["kodi_port"]
                kodi_user = self.settings["kodi_user"]
                kodi_pass = self.settings["kodi_pass"]
                self.kodi_path = "http://" + kodi_user + ":" + kodi_pass + "@" + kodi_ip + ":" + str(kodi_port) + \
                                 "/jsonrpc"
                LOG.info(self.kodi_path)
                self._is_setup = True
        except Exception as e:
            LOG.error(e)


    # listening event used for kodi notifications
    def handle_listen(self, message):
        voice_payload = "Listening"
        if self.notifier_bool:
            try:
                self.post_kodi_notification(voice_payload)
            except Exception as e:
                LOG.error(e)
                self.on_websettings_changed()

    # utterance event used for kodi notifications
    def handle_utterance(self, message):
        utterance = message.data.get('utterances')
        voice_payload = utterance
        if self.notifier_bool:
            try:
                self.post_kodi_notification(voice_payload)
            except Exception as e:
                LOG.error(e)
                self.on_websettings_changed()

    # mycroft speaking event used for kodi notificatons
    def handle_speak(self, message):
        voice_payload = message.data.get('utterance')
        if self.notifier_bool:
            try:
                self.post_kodi_notification(voice_payload)
            except Exception as e:
                LOG.error(e)
                self.on_websettings_changed()


    def CPS_match_query_phrase(self, phrase):
        """
            The method is invoked by the PlayBackControlSkill.
        """
        self.log.info('CPKodiSkill received the following phrase: ' + phrase)
        self.device_match = False
        self.remote_match = False
        for device_id in self.device_list:
            if device_id in phrase:
                self.device_match = True
                playback_device = device_id
        for remote_id in self.remote_sources:
            if remote_id in phrase:
                self.remote_match = True
        if self.remote_match and kodi_tools.check_youtube_present(self.kodi_path):
            self.youtube_search = youtube_tools.youtube_query_regex(phrase)
            self.youtube_id = youtube_tools.get_youtube_links(self.youtube_search)
            if self.youtube_id:
                self.remote_match = True  # kodi can play remote content with plugin
        else:
            self.remote_match = False  # kodi can't play remote content, no plugin
        # Check if the movie exists before deciding if we can play this request
        movie_name = self.movie_regex(phrase)  # extract the movie name from the phrase
        try:
            LOG.info("movie: " + movie_name)
            results = self.find_movies_with_filter(movie_name)
            self.movie_list = results
            self.movie_index = 0
            LOG.info("possible movies are: " + str(results))
            if self.device_match and len(results): # One of the playback devices were specified
                match_level = CPSMatchLevel.EXACT
            elif self.remote_match:  # A youtube Item was found and is playable
                match_level = CPSMatchLevel.EXACT
            else:
                LOG.info('Couldn\'t find anything to play on kodi')
            if len(results):
                data = {"local", playback_device, movie_name, results}
            elif self.youtube_id:
                data = {"remote", playback_device, self.youtube_search, self.youtube_id}
        except Exception as e:
            LOG.info('an error was detected')
            LOG.error(e)
            self.on_websettings_changed()

        if match_level:
            return (phrase, match_level, data)
        else:
            return None

    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        play_type = data[0]
        playback_device = data[1]
        item_name = data[2]
        results = data[3]
#        if len(results) == 1:
#            self.play_film(results[0]['movieid'])
#        elif len(results):
#            self.set_context('NavigateContextKeyword', 'NavigateContext')
#            self.speak_dialog('multiple.results', data={"result": str(len(results))}, expect_response=True)
#        else:
#            self.speak_dialog('no.results', data={"result": movie_name}, expect_response=False)
        pass

def create_skill():
    return CPKodiSkill()