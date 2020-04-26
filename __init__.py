from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
import re
from mycroft.util.parse import extract_number
from mycroft.audio import wait_while_speaking

import pafy
import pychromecast
from pychromecast.controllers.youtube import YouTubeController

import urllib.error
import urllib.parse
import urllib.request

import requests
import re
import time
import json
import random

_author__ = 'PCWii'
# Release - 20120426

class CPKodiSkill(CommonPlaySkill):
    def __init__(self):
        super(CPKodiSkill, self).__init__('CPKodiSkill')

    def CPS_match_query_phrase(self, phrase):
        """
            The method is invoked by the PlayBackControlSkill.
        """
        self.log.info('CPKodiSkill received the following phrase: ' + phrase)
        device_list = ['chromecast', 'kodi']
        for device_id in device_list:
            if device_id in phrase:
                match_level = CPSMatchLevel.EXACT
                playback_device = device_id
        data = {
            "track": "my Movie Name"
        }
        if match_level:
            return (phrase, match_level, data)
        else:
            return None

    def CPS_start(self, phrase, data):
        """ Starts playback.

            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        self.log.info('CPKodi Skill received the following phrase and Data: ' + phrase + ' ' + data['track'])
        pass

def create_skill():
    return CPKodiSkill()