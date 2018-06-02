import functools

import discord
from mpd import MPDClient
from datetime import timedelta
import mpd_album_art

mpd_connection = None


def establish_mpd_connection():
    global mpd_connection
    if mpd_connection:
        return

    import main
    settings = main.get_settings()

    mpd_connection = MPDClient()

    mpd_settings = settings['mpd']

    mpd_connection.timeout = mpd_settings['timeout']
    mpd_connection.connect(mpd_settings['server'], mpd_settings['port'])


def close_mpd_connection():
    global mpd_connection
    mpd_connection.close()
    mpd_connection.disconnect()
    mpd_connection = None


def requires_mpd():
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args):
            try:
                establish_mpd_connection()
                return func(*args)
            finally:
                close_mpd_connection()

        return wrapped

    return wrapper


def generate_query(query):
    QUERY_TYPES = [
        'artist',
        'album',
        'title',
        'track',
        'name',
        'genre',
        'date',
        'composer',
        'performer',
        'comment',
        'disc',
        'filename',
        'any']

    query_dict = {}
    key = 'any'
    for word in query:
        if any(t in word for t in QUERY_TYPES):
            key = word.split(':')[0]
            word = word.split(':')[1]

        if key in query_dict:
            query_dict[key] += ' ' + word
        else:
            query_dict[key] = word

    return [item for k in query_dict for item in (k, query_dict[k])]


@requires_mpd()
def get_playing(args):
    current_song = mpd_connection.currentsong()
    if len(current_song) == 0:
        return {'message': "Nothing playing."}

    import main
    settings = main.get_settings()
    grabber_settings = settings['mpd']['art_grabber']

    grabber = mpd_album_art.Grabber(
        save_dir=grabber_settings['save_dir'],
        library_dir=grabber_settings['library_dir']
    )

    grabber.get_local_art(current_song)

    # message = 'Currently playing: **%s** - **%s** by **%s**.' \
    #           % (current_song['title'], current_song['album'], current_song['artist']) \
    #     if len(current_song) > 0 else "Nothing."

    embed = discord.Embed(color=0xff0ff, title=current_song['title'],
                          description=current_song['album'] + " - " + current_song['artist'])

    IMAGE_URL = 'https://files.jakestanger.com/mpd/current.png'  # TODO Add to config
    embed.set_thumbnail(url=IMAGE_URL)

    return {'embed': embed}


@requires_mpd()
def search(query):
    results = mpd_connection.search(*(entry for entry in generate_query(query)))

    SEARCH_RESULTS = 15  # TODO Include in query
    if len(results) > SEARCH_RESULTS:
        results = results[:SEARCH_RESULTS]

    message = ''.join('**%s** - **%s** by **%s**. (%s)\n'
                      % (
                          song['title'], song['album'], song['artist'],
                          timedelta(seconds=round(float(song['duration']))))
                      for song in results) if len(results) > 0 else "No results."

    return {'message': message}
