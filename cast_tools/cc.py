from mycroft.util.log import LOG
import pychromecast
import time
#myFile = "http://192.168.0.32:8080/vfs/%2Fhome%2Fosmc%2Fmnt%2FnfsMovies%2FMarvel%2FSpider-Man%2FSpider.Man.2.2004.1080p.mp4"


def cc_get_names():
    casts, browser = pychromecast.get_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    deviceList = []
    if len(casts) == 0:
        return None
    LOG.info("Found cast devices:")
    for cast in casts:
        this_device = {}
        this_device['name'] = cast.name
        deviceList.append(this_device)
    return deviceList


def cc_cast_file(deviceName, filename):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    pychromecast.discovery.stop_discovery(browser)
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.play_media(filename, 'video/mp4')
    time.sleep(2)
    device_status = {}
    device_status['player_state'] = mc.status.player_state
    device_status['media_session_id'] = mc.status.media_session_id
    device_status['duration'] = mc.status.duration
    device_status['content_type'] = mc.status.content_type
    device_status['content_id'] = mc.status.content_id
    pychromecast.discovery.stop_discovery(browser)
    return device_status


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


def cc_stop(deviceName, sessionID):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    time.sleep(1)
    if isinstance(mc.status.media_session_id, int):
        if mc.status.media_session_id == sessionID:
            mc.stop()
        else:
            LOG.info('Chromecast: sessionID did not match!')
        time.sleep(1)
    else:
        LOG.info('Chromecast: Nothing is Playing!')
    device_status = {}
    device_status['player_state'] = mc.status.player_state
    device_status['media_session_id'] = mc.status.media_session_id
    device_status['duration'] = mc.status.duration
    device_status['content_type'] = mc.status.content_type
    device_status['content_id'] = mc.status.content_id
    pychromecast.discovery.stop_discovery(browser)
    return device_status
