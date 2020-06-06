import pychromecast
from pychromecast.controllers.youtube import YouTubeController
import time


# send a URI to Chromecast and play
def cast_link(source_link, device_ip):
    cast = pychromecast.Chromecast(device_ip)
    cast.wait()
    mc = cast.media_controller
    mc.play_media(source_link, 'video/mp4')
    time.sleep(7)  # wait for CC to be ready to play
    mc.block_until_active()
    mc.play()
    # mc.stop()


# send a youtube videoID and play
def cast_youtube(video_id, device_ip):
    cast = pychromecast.Chromecast(device_ip)
    cast.wait()
    yt = YouTubeController()
    cast.register_handler(yt)
    yt.play_video(video_id)
