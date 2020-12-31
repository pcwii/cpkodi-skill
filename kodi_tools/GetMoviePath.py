from mycroft.util.log import LOG
import requests
import json
import urllib.parse
import urllib.error
import urllib.request


def get_movie_path(kodi_path, movieID):
    api_path = kodi_path + "/jsonrpc"
    vfs_path = kodi_path + "/vfs/"
    json_header = {'content-type': 'application/json'}
    method = "VideoLibrary.GetMovieDetails"
    kodi_payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": 1,
        "params": {
            "movieid": movieID,
            "properties": [
                "file",
            ],
        }
    }
    try:
        kodi_response = requests.post(api_path, data=json.dumps(kodi_payload), headers=json_header)
        LOG.info("kodi responded with: " + str(kodi_response.text))
        movie_path = json.loads(kodi_response.text)["result"]["moviedetails"]["file"]
        url_path = vfs_path + urllib.parse.quote(str(movie_path), safe='')
        LOG.info(url_path)
        return url_path
    except Exception as e:
        LOG.info(e)
        return None
