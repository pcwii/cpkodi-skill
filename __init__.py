from os.path import dirname

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from adapt.intent import IntentBuilder

from mycroft.util.log import LOG

from helpers import yt_tools, cast_tools, kodi_tools, search_tools


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
        try:
            request_details = search_tools.get_request_details(phrase)  # extract the movie name from the phrase
            LOG.info("Requested search: " + request_details[0] + ", of type: " + request_details[1])
            if "movie" in request_details[1]:
                results = kodi_tools.get_filtered_movies(self.kodi_path, request_details[0])
                LOG.info("Possible movies matches are: " + str(results))
            if results is None:
                return None  # until a match is found
            else:
                if len(results) > 0:
                    match_level = CPSMatchLevel.EXACT
                    data = {
                        "library": results,
                        "request": request_details[0],
                        "type": request_details[1],
                        "subtype": request_details[2]
                    }
                    LOG.info('Searching Kodi found a matching playable item!')
                    return phrase, match_level, data
                else:
                    return None  # until a match is found
        except Exception as e:
            LOG.info('An error was detected')
            LOG.error(e)
            self.on_websettings_changed()

    def CPS_start(self, phrase, data):
        """ Starts playback.
            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        LOG.info('Ready to Play: ' + data["library"])
        LOG.info('Ready to Play: ' + data["request"])
        LOG.info('Ready to Play: ' + data["type"])
        LOG.info('Ready to Play: ' + data["subtype"])
        pass

def create_skill():
    return CPKodiSkill()