#!/usr/bin/env python

# MPD Album Art
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
:copyright: 2013 Jamie Macdonald
:license: GNU General Public License (GPL) version 3

.. testsetup::

    from mpd_album_art import Grabber

"""

from pylast import LastFMNetwork, AlbumSearch

import os
import sys
import shutil

from urllib.request import urlretrieve
from urllib.error import HTTPError


_image_extensions = (".jpg", ".jpeg", ".png")
"""Extensions to qualify a file as an image"""

_last_fm_api_key = "6b6d8768f0c41f7e82da0de44e1db76a"
"""LastFM API key for the application"""


class Grabber:
    """An object to grab artwork for MPD songs

    :param str save_dir:
        Directory into which Grabber should download new images.
    :param str library_dir:
        Directory MPD is currently playing from.
    :param str link_path:
        Path to symlink to current image file. By default,
        ``os.path.join(save_dir, "current.png")``

    Construct a Grabber with ``save_dir = ~/.covers``:

    >>> import os
    >>> home_dir = os.environ['HOME']
    >>> cover_path = os.path.join(home_dir, '.covers')
    >>> grabber = Grabber(cover_path)

    specify more stuff:

    >>> music_path = os.path.join(home_dir, 'Music/Library')
    >>> current_cover_link = os.path.join(home_dir, '.current_cover')
    >>> grabber = Grabber(save_dir=cover_path, library_dir=music_path,
    ...                   link_path=current_cover_link)
    """
    def __init__(self, save_dir, library_dir=None, link_path=None, quiet=False):
        super().__init__()

        self.save_dir = save_dir

        if library_dir is None:
            library_dir = os.path.join(os.environ['HOME'], 'Music')
        self.library_dir = library_dir

        if link_path is None:
            link_path = os.path.join(save_dir, "current.png")
        self.link_path = os.path.join(save_dir, link_path)

        self._quiet = quiet

    def get_art(self, song):
        """Get artwork from LastFM.

        Before connecting to network, if there exists a file whose name begins
        with ``_sanitize(song['artist'] + ' ' + song['album'])``, return that
        file path.
        Do not overwrite existing files.
        Set ``os.path.join(save_dir, 'current')`` as symlink to image file.

        :param dict song:
            A dictionary with keys ``'album'`` and ``'artist'`` to correspond
            with string representations of the album and artist (resp.) of
            interest. Use ``MPDClient.currentsong()`` to return uch a dictionary
            .
        :return:
            A string representation of the local file path to the image file for
            ``song`` or ``None`` if no results found
        """
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        l = [n for n in os.listdir(self.save_dir)
             if n.startswith(song['artist'] + "_" + song['album'])]
        if l != []:
            self._log("Already have this album\n")
            file_path = os.path.join(self.save_dir, l[0])

            # We have album art - check if it's linked
            if os.path.realpath(self.link_path) != file_path:
                self._log("Linking...\n")
                self.remove_current_link()
                self.set_current_link(file_path)
            self._log("Exiting.\n")
            return file_path

        # Define the search network compatible with LastFM API
        network = LastFMNetwork(api_key=_last_fm_api_key)

        album_search = AlbumSearch(song['artist'] + ' ' + song['album'], network)

        if album_search.get_total_result_count() == 0:
            # Remove current album link, and return, since no art was found for
            # given query.
            self._log("No results from Last.FM\n")
            self.remove_current_link()
            return None

        # Get the first hit, since there is at least one result -
        # the "I'm feeling lucky" approach.
        album = album_search.get_next_page()[0]

        # Get url of album art from ``pylast.AlbumSearch`` object
        img_url = album.get_cover_image()

        file_path = os.path.join(self.save_dir,
                                 self._get_save_name(song, img_url))

        # Check if this file exists in filesystem already and is linked
        if os.path.isfile(file_path):
            if os.path.realpath(self.link_path) == file_path:
                return file_path
        else:
            try:
                # Download the image
                urlretrieve(img_url, file_path)
                self.remove_current_link()
            except HTTPError as e:
                self._log(e + "\n")
                self.remove_current_link()
                return None

        self.set_current_link(file_path)
        return file_path

    def get_local_art(self, song):
        """Get artwork from ``song`` folder.

        :param dict song:
            A dictionary with keys ``'album'`` and ``'artist'`` to correspond
            with string representations of the album and artist (resp.) of
            interest. Such a dictionary returns from
            ``MPDClient.currentsong()``
        :return:
            A string representation of the local file path to the largest image
            file for ``song`` found in ``song_folder``, or ``None`` if no results
            found
        """
        song_folder = os.path.dirname(os.path.join(self.library_dir,
                                                   song['file']))
        images = self._get_images_from_folder(song_folder)

        if images == []:
            self._log("No local results from {}\n".format(song_folder))
            raise Exception
            # return None

        # Pick the largest file
        images = [os.path.join(song_folder, i) for i in images]
        file_path = max(images, key=os.path.getsize)

        if os.path.realpath(self.link_path) != file_path:
            # Set the link to point to the file_path
            self.remove_current_link()
            self.set_current_link(file_path)
        return file_path

    def remove_current_link(self):
        """Delete current artwork symlink.
        """
        try:
            os.unlink(self.link_path)
        except FileNotFoundError:
            pass

    def set_current_link(self, file_path):
        """Set current artwork symlink.
        :param file_path:
            Path to artwork to be set as current.
        """
        # os.symlink(file_path, self.link_path)
        shutil.copyfile(file_path, self.link_path)

    def _get_save_name(self, song, img_url=None):
        """Return file name of album art at img_url

        :param dict song:
            A dictionary with keys ``'album'`` and ``'artist'`` to correspond
            with string representations of the album and artist (resp.) of
            interest. Such a dictionary returns from
            ``MPDClient.currentsong()``
        :param str img_url:
            A string representation of an external url points to the album
            artwork image file
        :return:
            ``str`` of the form 'Artist_Name_Album_Name_h45h.png', or if
            ``img_url`` is ``None``, simply 'Artist_Name_Album_Name'. In this
            example, ``'h45h.png'`` extracts from the original filename in
            ``img_url``.
        """
        save_name = song['artist'] + ' ' + song['album']
        if img_url:
            save_name = save_name + ' ' + img_url.split("/")[-1]
        return _sanitize(save_name)

    def _get_images_from_folder(self, folder):
        """Get a list of image files from ``folder``.

        :return list:
            A list of file names from within ``folder`` that end with an extension
            defined in the ``image_extensions`` tuple.
        """
        return [f for f in os.listdir(folder) if f.endswith(_image_extensions)]

    def _log(self, msg):
        if not self._quiet:
            sys.stderr.write(msg)


def _sanitize(name):
    """Replace occurences of ``disallowed_characters`` in name with
    underscores and double quotation marks with single quotation marks.
    """
    disallowed_characters = r"\/:<>?*| "

    for character in disallowed_characters:
        name = name.replace(character, '_')
    # Replace " with '
    return name.replace('"', "'")
