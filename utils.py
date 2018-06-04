import main
import requests
import discord
import constants
from datetime import timedelta

settings = main.settings


def get_album_art_url(song):
    import mpd_album_art

    grabber_settings = settings['mpd']['art_grabber']

    artist_album = '%s - %s.jpg' % (song['artist'], song['album'])

    grabber = mpd_album_art.Grabber(
        save_dir=grabber_settings['save_dir'],
        library_dir=grabber_settings['library_dir'],
        link_path=artist_album
    )

    grabber.get_local_art(song)

    return settings['download_servers']['art_url'] + requests.utils.quote(artist_album)


def get_track_download(song):
    return settings['download_servers']['music_url'] + requests.utils.quote(song['file'])


def get_song_embed(song, additional=None):
    embed = discord.Embed(color=0xff0ff, title=song['title'],
                          description=song['album'] + " - " + song['artist'])

    embed.set_thumbnail(url=get_album_art_url(song))

    if additional:
        embed.description += '\n**%s**' % additional

    download_link = get_track_download(song)
    embed.add_field(name='Download Link', value=f'[Click Here]({download_link})')

    return embed


def get_results_embed(results, title: str='Search Results', empty: str='No results.'):
    alphabet = [chr(i) for i in range(constants.UPPER_A_VALUE, constants.UPPER_Z_VALUE)]

    message = ''.join('%s: **%s** - **%s** by **%s**. (%s)\n'
                      % (alphabet[results.index(song)],
                         song['title'], song['album'], song['artist'],
                         timedelta(seconds=round(float(song['time']))))
                      for song in results) if len(results) > 0 else empty

    embed = discord.Embed(color=0xff00ff, title=title, description=message)

    return embed


async def send_song_embed(client, message, song, additional=None):
    embed = get_song_embed(song, additional)
    await client.send_message(message.channel, embed=embed)


def create_player(voice):
    ffmpeg_options = '-analyzeduration 0 ' \
                     '-loglevel 0 ' \
                     '-f s16le ' \
                     '-ar 44100 ' \
                     '-ac 2 ' \
                     '-acodec pcm_s16le'

    return voice.create_ffmpeg_player('/tmp/mpd.fifo', before_options=ffmpeg_options)
