# window.py
#
# Copyright 2024 Tanmay Patil <tanmaynpatil105@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import gi

gi.require_version("WebKit", "6.0")
from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

from .views.lyrics_view import LyricsView
from .api.spotify import get_now_playing_item
from .api.lyrics import get_lyrics, get_synced_lyrics
from .lib.utils import sanitize_lyrics

from threading import Thread


@Gtk.Template(resource_path="/io/github/TanmayPatil105/verse/window.ui")
class VerseWindow(Adw.ApplicationWindow):
    __gtype_name__ = "VerseWindow"

    box = Gtk.Template.Child()
    status = Gtk.Template.Child()
    search_button = Gtk.Template.Child()
    lyrics_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # song details
        self.song = None
        self.lyrics = None
        self.synced_lines = None
        self.fetching = False

        # set up widgets
        self.status.bind_property(
            "visible", self.lyrics_view, "visible", GObject.BindingFlags.INVERT_BOOLEAN
        )
        self.lyrics_view.bind_property(
            "visible", self.status, "visible", GObject.BindingFlags.INVERT_BOOLEAN
        )

        GLib.idle_add(self.fetch_details)
        GLib.timeout_add_seconds(3, self.poll_spotify)

    @Gtk.Template.Callback()
    def on_search_cb(self, button):
        # call this on a separate thread
        self.fetch_details()

    def zoom_lyrics(self, delta):
        self.lyrics_view.zoom_font(delta)

    def song_unchanged(self, song):
        if self.song and song:
            try:
                if self.song.get("id") and song.get("id"):
                    return self.song["id"] == song["id"]

                if self.song_key(self.song) == self.song_key(song):
                    return True
            except:
                return False

        return False

    def song_key(self, song):
        artists = ",".join([artist["name"] for artist in song["artists"]])
        return "{}::{}".format(song["title"], artists)

    def poll_spotify(self):
        if not self.fetching:
            self.fetch_details(show_status=False)

        return True

    # runs on a thread
    def fetch_song(self, show_status=True):
        song = get_now_playing_item()

        try:
            if "error" not in song:
                # if song is unchanged, keep the lyric page and only sync playback time
                if self.song_unchanged(song):
                    GLib.idle_add(
                        self.lyrics_view.update_playback,
                        song.get("progress_ms", 0),
                        song.get("is_playing", False),
                    )
                    GLib.idle_add(self.box.set_valign, Gtk.Align.FILL)
                    GLib.idle_add(self.lyrics_view.set_visible, True)
                    self.song = song
                    return

                if song["is_playing"]:

                    artist = ", ".join([_artist["name"] for _artist in song["artists"]])
                    GLib.idle_add(
                        self.status.set_title,
                        "Searching lyrics for {}..".format(song["title"], artist),
                    )
                    GLib.idle_add(
                        self.status.set_description,
                        "by {}".format(artist),
                    )
                else:
                    GLib.idle_add(self.status.set_title, "Song is Paused!")
                    GLib.idle_add(self.status.set_description, "Here's the lyrics anyway..")

                artist = ", ".join([_artist["name"] for _artist in song["artists"]])
                synced_lyrics = get_synced_lyrics(song["title"], artist)
                if "error" not in synced_lyrics:
                    self.song = song
                    self.lyrics = synced_lyrics["lyrics"]
                    self.synced_lines = synced_lyrics["synced"]
                    GLib.idle_add(self.display_lyrics)
                    return

                for artist in song["artists"]:
                    lyrics = get_lyrics (song["title"], artist["name"])
                    if "error" not in lyrics:
                        # we found a lyrics
                        self.song = song
                        self.lyrics = sanitize_lyrics(lyrics["lyrics"])
                        self.synced_lines = None
                        GLib.idle_add(self.display_lyrics)
                        return

                # we couldn't find any lyrics
                GLib.idle_add(self.status.set_title, lyrics["error"])
                GLib.idle_add(self.status.set_description, lyrics["description"])

            elif show_status:
                GLib.idle_add(self.status.set_title, song["error"])
                GLib.idle_add(self.status.set_description, song["description"])
        finally:
            self.fetching = False

    def display_lyrics(self):
        self.box.set_valign(Gtk.Align.FILL)
        self.search_button.set_visible(False)
        self.lyrics_view.append(self.lyrics, self.song, self.synced_lines)
        self.lyrics_view.set_visible(True)

    def fetch_details(self, show_status=True):
        if self.fetching:
            return False

        self.fetching = True
        self.search_button.set_visible(False)

        if show_status or not self.lyrics_view.get_visible():
            self.box.set_valign(Gtk.Align.CENTER)
            self.status.set_title("Fetching song...")
            self.status.set_description("Press Ctrl+O to open Preferences.")
            self.status.set_visible(True)

        # create separate thread
        thread = Thread(target=self.fetch_song, args=(show_status,), daemon=True)
        thread.start()
        return False
