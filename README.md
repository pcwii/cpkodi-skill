**Be aware that this repo is currently undergoing development and Testing. As a result breaking changes may be introduced occassionally during testing**
# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/tv.svg' card_color='#40DBB0' width='50' height='50' style='vertical-align:bottom'/> CP Kodi Control
Control KODI open source media center with Mycroft.ai using the Common Play architecture

## About 
Utilize the kodi API and Python library for controlling the KODI open source media center with Mycroft.ai.
The Kodi Skill uses conversational dialog to help you to control your KODI instance more naturally. 

## Examples -Movies-
*[x] "play the movie guardians of the galaxy"
*[x] "play the film planet of the apes"
*[x] "play a random movie"
*[ ] "turn kodi subtitles on"
*[ ] "turn kodi subtitles off"
*[ ] "skip kodi forward"
*[ ] "skip kodi backward"
*[ ] "pause the film"
*[ ] "re-start the film"
*[ ] "stop the movie"
*[ ] "show kodi movie information"
*[ ] "hide kodi movie information"
*[x] "list recently added movies"
*[x] "list the movies by genre"
*[x] "list the movies by studio"
*[x] "list movie sets"
*[x] "list movies by title"
*[x] "list movies by actor"
*[x] "list all movies"
*[x] "clear the movie playlist"
* **Movie titles containing Roman Numerals will automatically be searched**
**eg.** 
*[x] "play the movie star wars 3" - will locate *star wars III* 
## Examples -Music-
*[x] "play the artist elvis presley”
*[x] "play the song blue suede shoes"
*[x] "play the album appeal to reason”
*[x] "the song Cinematic by Owl City"
*[x] "the album Cinematic by Owl City"
*[x] "play some music" --will play a random selection
*[x] "clear the music playlist"
*[x] "pause the music"
*[x] "resume the music"
## Examples -Youtube-
- Requires Youtube Kodi [Plugin](https://github.com/anxdpanic/plugin.video.youtube/releases)
- Requires Youtube Kodi [API](https://github.com/anxdpanic/plugin.video.youtube/wiki/Personal-API-Keys)
*[x] "play the captain marvel official trailer from youtube”
*[x] "play helix with youtube”
*[x] "play some Elton John using youtube"
## Examples -TV Shows-
*[x] "play the outer limits season 1 episode 2”
## Examples -Miscellaneous-
*[x] "pause kodi"
*[x] "re-start kodi"
*[x] "stop kodi"
*[x] "clear the kodi playlist"
*[x] "set kodi volume to 100"
*[x] "set kodi volume to 25"
*[x] "turn kodi notifications on"
*[x] "turn kodi notifications off"
*[ ] "move the kodi cursor up / down / left / right / back / select / cancel"
  - After the first cursor command just say the direction "up / down / left / right / back / select / cancel"
*[x] "move the kodi cursor right 3 times"
*[x] "move the kodi cursor down twice"
*[ ] "update the kodi library"
*[ ] "clean the kodi library"
## Conversational Context
*[ ] If mycroft.ai locates more than one movie that matches your request it will permit you to itterate through your requests
using conversational context.
* eg. "hey mycroft:"
* Request: "play the move Iron Man"
* Response: "I have located 3 movies with the name Iron Man, 
* Response: "Would you like me to list them?"
* Request: "yes"
* Response: "Iron Man, to add to Playlist say Add, to Skip, say Next, say play, to play, or Cancel, to stop"
* Request: "next"
* Response: "Iron Man 2"
* Request: "play" / "select"
* Response: "o-k, attempting to play, Iron Man 2"
## Cinemavision Addon
*[ ] If mycroft.ai locates the addon CinemaVision it will prompt the user if this addon should be used during the 
playback of the movie that was selected.
* Response: "Would you like to play the movie using cinemavision?"
* Request: "yes / no"
## Chromecast Support
CP Kodi skill is capable of "casting" any of your personal library files to a chromecast enabled device
*[ ] "cast the movie guardians of the galaxy"
## Credits 
* PCWii
## Category
**Media**
## Tags
'#kodi, #Krypton #Leia, #mycroft.ai, #python, #skills #youtube #common play #cps'
## Require
Tested on platform_picroft (others untested) 
## Other Requirements
- [Mycroft](https://docs.mycroft.ai/installing.and.running/installation)
## Dependancies **Automatically Installed**
* python:
    - requests
    - bs4
    - requests_cache
    - PyChromecast>=7.0.1
    - pyenchant
    - compound-word-splitter
* system:
    - apt-get: libenchant1c2a
## Further Reading
- [KODI API](https://kodi.wiki/index.php?title=JSON-RPC_API/v8)
- [CinemaVision](https://kodi.wiki/view/Add-on:CinemaVision)
## Installation Notes
- SSH to your device and run: `msm install https://github.com/pcwii/cpkodi-skill.git`
- Configure Kodi to “allow remote control via HTTP”, under the Kodi settings:services
- Configure Kodi to “allow remote control from applications on other systems”, under the Kodi settings:services
- Under Kodi settings:services note the port number (8080)
- Configure home.mycroft.ai to set your kodi instance ip address and port number
## Todo
- ~~Added movies search with roman numerals based on numbers in the utterance~~ (Completed 20201214)
- ~~Make repeat words language agnostic "MultiplicativeList.json"~~ (Completed 2021214)
- ~~Add the ability to search music by album and artist~~ (Completed 20210110)
- ~~Correct the random music request "play some music"~~ (Completed 20201228) 
- ~~Confirm TV Show request by season and episode "play the outer limits season 1 episode 2"~~ (Completed 20201229)
- ~~Confirm music request by artist "play the artist Elvis"~~ (Completed 20210110)
- Confirm TV Show request by Title with dialog "play the tv show stargirl" (Todo 20201214)
- ~~Correct index out of range when iterating through a list of found movies~~ (Complete 20201223)
- ~~Todo Add new dialog response when we reach the end of the list~~ (Completed 20201224)
- ~~Add Option to toggle debug log entries in websettings~~ (Completed 20201229)
- Confirm Chromecast support for local library (20201229)