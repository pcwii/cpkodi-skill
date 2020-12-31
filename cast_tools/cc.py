import pychromecast
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
    pychromecast.discovery.stop_discovery(browser)
    cast = next(cc for cc in casts if cc.device.friendly_name == "Hisense TV")
    cast.wait()
    mc = cast.media_controller
    mc.play_media(filename, 'video/mp4')
    mc.block_until_active()
    return mc.status


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
