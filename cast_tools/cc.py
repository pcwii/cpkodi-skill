import pychromecast
import time
#myFile = "http://192.168.0.32:8080/vfs/%2Fhome%2Fosmc%2Fmnt%2FnfsMovies%2FMarvel%2FSpider-Man%2FSpider.Man.2.2004.1080p.mp4"

def cc_get_names():
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    deviceList = []
    if len(casts) == 0:
        return None
    print("Found cast devices:")
    for cast in casts:
        this_device = {}
        this_device['name'] = cast.name
        deviceList.append(this_device)
    return deviceList


def cc_cast_file(deviceName, filename):
    casts, browser = pychromecast.get_chromecasts()
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    mc = cast.media_controller
    mc.play_media(filename, 'video/mp4')
    mc.block_until_active()
    # Wait for player_state PLAYING
    player_state = cast.media_controller.status.player_state
    t = 10
    is_playing = False
    while (not is_playing) or (t > 0):
        if player_state != cast.media_controller.status.player_state:
            player_state = cast.media_controller.status.player_state
            print("Player state:", player_state)
        if player_state == "PLAYING":
            is_playing = True
        else:
            is_playing = False
        time.sleep(0.1)
        t = t - 0.1
    # Shut down discovery
    pychromecast.discovery.stop_discovery(browser)
    return is_playing


def cc_get_status(deviceName):
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    return cast.status


def cc_pause(deviceName):
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.pause()
    return mc.status


def cc_play(deviceName):
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.play()
    return mc.status


def cc_stop(deviceName):
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.stop()
    return mc.status
