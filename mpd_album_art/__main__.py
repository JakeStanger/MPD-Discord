from mpd_album_art import Grabber

from mpd import MPDClient

import argparse
import os
import socket
import sys


def main():
    home_dir = os.environ['HOME']
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--hostname', type=str, default='localhost')
    parser.add_argument('-p', '--port', type=int, default=6600)
    parser.add_argument('-m', '--music_dir', type=str,
                        default=os.path.join(home_dir, 'Music'))
    parser.add_argument('-a', '--art_dir', type=str,
                        default=os.path.join(home_dir, '.covers'))
    parser.add_argument('-l', '--link_name', type=str, default='current')
    parser.add_argument('-q', '--quiet', action='store_true')
    args = parser.parse_args()

    def log(msg):
        if not args.quiet:
            sys.stderr.write(msg)

    # initialize MPD client
    mpd_client = MPDClient()

    grabber = Grabber(save_dir=args.art_dir, library_dir=args.music_dir,
                      link_path=os.path.join(args.art_dir, args.link_name),
                      quiet=args.quiet)

    try:
        # connect client to MPD server
        mpd_client.connect(args.hostname, args.port)
    except socket.error:
        # Cannot connect
        log('MPD not running?\n')
        grabber.remove_current_link()
        sys.exit(1)

    current_song = mpd_client.currentsong()

    if current_song == {}:
        # No song is playing
        grabber.remove_current_link()

    # try local pics
    elif grabber.get_local_art(current_song) is not None:
        log('Found local image, not querying LastFM.\n')

    # try lastFM pics
    elif grabber.get_art(current_song) is not None:
        log('Found lastFM image.\n')

    # Potentially link to a default image here (link has been destroyed at this
    # point)

    # done
    log('Exiting.\n')
    mpd_client.disconnect()


if __name__ == "__main__":
    main()
