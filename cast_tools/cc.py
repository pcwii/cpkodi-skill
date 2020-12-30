import time
import pychromecast

#myFile = "http://192.168.0.32:8080/vfs/%2Fhome%2Fosmc%2Fmnt%2FnfsMovies%2FMarvel%2FSpider-Man%2FSpider.Man.2.2004.1080p.mp4"


def cc_get_names():
    services, browser = pychromecast.discovery.discover_chromecasts()
    pychromecast.discovery.stop_discovery(browser)
    deviceList = []
    for each_device in services:
        this_device = {}
        this_device['type'] = each_device[2]
        this_device['name'] = each_device[3]
        this_device['ip'] = each_device[4]
        this_device['port'] = each_device[5]
        deviceList.append(this_device)
    pychromecast.discovery.stop_discovery(browser)
    return deviceList


def cc_cast_file(deviceName, filename):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    # chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Hisense TV"])
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.play_media(filename, 'video/mp4')
    mc.block_until_active()
    pychromecast.discovery.stop_discovery(browser)
    return mc.status


def cc_get_status(deviceName):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    # chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Hisense TV"])
    cast = chromecasts[0]
    cast.wait()
    pychromecast.discovery.stop_discovery(browser)
    return cast.status


def cc_pause(deviceName):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    # chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Hisense TV"])
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.pause()
    pychromecast.discovery.stop_discovery(browser)
    return mc.status


def cc_play(deviceName):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    # chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Hisense TV"])
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.play()
    pychromecast.discovery.stop_discovery(browser)
    return mc.status


def cc_stop(deviceName):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[deviceName])
    # chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=["Hisense TV"])
    cast = chromecasts[0]
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    mc.stop()
    pychromecast.discovery.stop_discovery(browser)
    return mc.status
