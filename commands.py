import discord

import mpd_utils


def get_playing(msg, args):
    song = mpd_utils.get_current_song()
    if len(song) == 0:
        embed = discord.Embed(title="Nothing playing.", color=0xff4444)
        return {'embed': embed}, None, None

    import utils
    return {'embed': utils.get_song_embed(song)}, None, None


def search(msg, query):
    results = mpd_utils.perform_search(query)

    import utils
    return {'embed': utils.get_results_embed(results)}, \
           {'wait_for_reactions': True, 'data': results}, utils.send_song_embed


def add(msg, query):
    results = mpd_utils.perform_search(query)

    import utils
    return {'embed': utils.get_results_embed(results)}, \
           {'wait_for_reactions': True, 'data': results}, mpd_utils.add_to_queue


def playlist(msg, args):
    results = mpd_utils.get_current_playlist()

    import utils
    return {'embed': utils.get_results_embed(results, title="Current Playlist", empty="Empty.")}, None, None


def join(msg, args):
    connected_channel = msg.author.voice.voice_channel

    action = None
    if connected_channel:
        message = "Joining **%s**..." % connected_channel.name
        action = {'join_voice': True, 'data': connected_channel}

    else:
        message = "You must be in a voice channel to do that."  # TODO Create decoration to handle voice channel requirement
    return {"message": message}, action, None


def pause(msg, args):
    connected_channel = msg.author.voice.voice_channel

    action = None
    if connected_channel:
        message = "Toggling playback..."
        action = {'toggle_playback': True, 'data': mpd_utils.is_paused()}
    else:
        message = "You must be in a voice channel to do that."

    return {"message": message}, action, None


def leave(msg, args):
    connected_channel = msg.author.voice.voice_channel

    action = None
    if connected_channel:
        message = "Leaving..."
        action = {'leave_voice': True, 'data': None}
    else:
        message = "You must be in a voice channel to do that."

    return {"message": message}, action, None