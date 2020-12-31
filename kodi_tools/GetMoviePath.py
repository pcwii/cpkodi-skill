from mycroft.util.log import LOG
import requests
import json
import urllib.parse


def get_movie_path(kodi_path, movieID):
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
        kodi_response = requests.post(kodi_path, data=json.dumps(kodi_payload), headers=json_header)
        movie_path = json.loads(kodi_response.text)["result"]["moviedetails"]["file"]
        """
        This must be handled by the return function
        basePath = 'http://'+kodi_ip+':'+kodi_port+'/vfs/'
        url_path = basePath + urllib.parse.quote(movie_path, safe='')
        print(url_path)
        """
        LOG.info(str(movie_path))
        return str(movie_path)
    except Exception as e:
        LOG.info(e)
        return None
