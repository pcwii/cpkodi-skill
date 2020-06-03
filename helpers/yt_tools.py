from mycroft.util.log import getLogger
from mycroft.util.log import LOG

import urllib.error
import urllib.parse
import urllib.request
import re


# extract the requested youtube item from the utterance
def youtube_query_regex(req_string):
    return_list = []
    pri_regex = re.search(r'(?P<item1>.*) from youtube', req_string)
    sec_regex = re.search(r'some (?P<item1>.*) from youtube|the (?P<item2>.*)from youtube', req_string)
    if pri_regex:
        if sec_regex:  # more items requested
            temp_results = sec_regex
        else:  # single item requested
            temp_results = pri_regex
    if temp_results:
        item_result = temp_results.group(temp_results.lastgroup)
        return_list = item_result
        LOG.info(return_list)
        return return_list


# extract the youtube links from the provided search_list
def get_youtube_links(search_list):
    # search_text = str(search_list[0])
    search_text = str(search_list)
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
            cleaned_pl = each_playlist.split(sep, 1)[0]  # clean up dirty playlists
            temp_links.append(cleaned_pl)
    playlist_links = temp_links
    yt_links = []
    if video_links:
        yt_links.append(video_links[0])
        LOG.info("Found Single Links: " + str(video_links))
    if playlist_links:
        yt_links.append(playlist_links[0])
        LOG.info("Found Playlist Links: " + str(playlist_links))
    return yt_links


def get_yt_audio_url(youtube_url):
    base_url = 'https://www.youtube.com'
    abs_url = base_url + youtube_url
    LOG.debug('pafy processing: ' + abs_url)
    streams = pafy.new(abs_url)
    LOG.debug('audiostreams found: ' + str(streams.audiostreams));
    bestaudio = streams.getbestaudio()
    LOG.debug('audiostream selected: ' + str(bestaudio));
    return bestaudio.url
