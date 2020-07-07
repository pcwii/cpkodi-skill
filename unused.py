def get_request_details(self, phrase):
    """
        matches the phrase against a series of regex's
        all files are .regex
        More types can be added to expand functions
        request_type is the type of media being requested
        request_item is the specific item that was requested
    """
    request_atributes = {}
    youtube_type = None
    album_type = None
    artist_type = None
    movie_type = None
    song_type = None
    show_type = None
    random_movie_type = None
    random_music_type = None
    self.artist_name = None
    youtube_type = re.match(self.translate_regex('youtube.type'), phrase)
    if youtube_type:  # youtube request "the official captain marvel trailer from youtube"
        request_type = 'youtube'
        request_item = youtube_type.groupdict()['ytItem']
        LOG.info('Youtube Type was requested: ' + str(request_item))
        # package the return json
        request_data = {
            "type": request_type,
            "item": request_item,
            "atributes": request_atributes,
        }
        return request_data  # request_item, request_type  # returns the request details and the request type
    else:
        album_type = re.match(self.translate_regex('album.type'), phrase)
        song_type = re.match(self.translate_regex('song.type'), phrase)
        show_type = re.match(self.translate_regex('show.type'), phrase)
        random_movie_type = re.match(self.translate_regex('random.movie.type'), phrase)
        if random_movie_type is None:
            movie_type = re.match(self.translate_regex('movie.type'), phrase)
        random_music_type = re.match(self.translate_regex('random.music.type'), phrase)
        if random_music_type is None:
            artist_type = re.match(self.translate_regex('artist.type'), phrase)
    if album_type:  # Music by: Album
        LOG.info('Album Type')
        request_type = 'album'
        request_item = album_type.groupdict()['album']
        # artist_specified = re.match(self.translate_regex('artist.name'), str(request_item))
        if artist_type:
            LOG.info('Artist also specified')
            artist_name = artist_type.groupdict()['artist']
            phrase = str(phrase).replace(str(artist_name), '')
            # Todo: add artist filter to album search
            request_atributes = {
                "artist": str(artist_name)
            }
    elif song_type:  # Music: by Song
        LOG.info('Song Type')
        request_type = 'title'
        request_item = song_type.groupdict()['title']
        # artist_specified = re.match(self.translate_regex('artist.name'), str(request_item))
        if artist_type:
            LOG.info('Artist also specified')
            artist_name = artist_type.groupdict()['artist']
            phrase = str(phrase).replace(str(artist_name), '')
            # Todo: add artist filter to album search
            request_atributes = {
                "artist": str(artist_name)
            }
    elif artist_type and not (album_type or artist_type):  # Music by: Artist only not a subtype
        LOG.info('Artist Type')
        request_type = 'artist'
        request_item = artist_type.groupdict()['artist']
    elif movie_type:  # Movies
        LOG.info('Movie Type')
        request_type = 'movie'
        request_item = movie_type.groupdict()['movie']
    elif random_movie_type:
        LOG.info('Random Movie Type')
        request_type = 'movie'
        request_item = 'random'
    elif random_music_type:  # rand
        LOG.info('Random Music Type')
        request_type = 'title'
        request_item = 'random'
    elif show_type:  # TV Shows
        # play the outer limits season 1 episode 2
        LOG.info('Show Type')
        request_type = 'show'
        request_item = show_type.groupdict()['showname']
        LOG.info("Show Name: " + str(request_item))
        request_specific = show_type.groupdict()['episode']
        LOG.info("Episode: " + str(request_specific))
        show_details = re.match(self.translate_regex('show.details'), str(request_specific))
        season_number = show_details.groupdict()['season']
        episode_number = show_details.groupdict()['episode']
        LOG.info(str(season_number) + ':' + str(episode_number))
        request_atributes = {
            "season": int(season_number),
            "episode": int(episode_number)
        }
    else:
        request_type = None
        request_item = None
    # package the return json
    request_data = {
        "type": request_type,
        "item": request_item,
        "atributes": request_atributes,
    }
    return request_data  # request_item, request_type # returns the request details and the request type
