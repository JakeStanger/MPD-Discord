from PersistantMPDClient import PersistentMPDClient

mpd_connection = None

streaming: bool = False


def establish_mpd_connection():
    global mpd_connection
    if mpd_connection:
        return

    import main
    settings = main.get_settings()

    mpd_settings = settings['mpd']
    mpd_connection = PersistentMPDClient(host=mpd_settings['server'], port=mpd_settings['port'])

    mpd_connection.timeout = mpd_settings['timeout']
    mpd_connection.do_connect()


def close_mpd_connection():
    global mpd_connection
    mpd_connection.close()
    mpd_connection.disconnect()
    mpd_connection = None


def get_current_song():
    return mpd_connection.currentsong()


def get_current_playlist():
    return mpd_connection.playlistinfo()


def toggle_playback(pause: bool):
    mpd_connection.pause(1 if pause else 0)


def start_playback():
    current_state = mpd_connection.status()['state']

    if current_state == 'pause':
        mpd_connection.pause(0)
    elif current_state == 'stop':
        if len(mpd_connection.playlist()) > 0:
            mpd_connection.play(0)


def pause_playback():
    mpd_connection.pause(1)


def is_paused():
    return mpd_connection.status()['state'] != 'play'


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


def perform_search(query):
    results = mpd_connection.search(*(entry for entry in generate_query(query)))

    SEARCH_RESULTS = 20  # TODO Include in query
    if len(results) > SEARCH_RESULTS:
        results = results[:SEARCH_RESULTS]

    return results


async def add_to_queue(client, message, song):
    mpd_connection.add(song['file'])

    import utils
    await utils.send_song_embed(client, message, song, additional='Added to queue.')
