# verse_preferences.py
#
# Copyright 2024 Tanmay Patil <tanmaynpatil105@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from ..lib.secrets import retrieve_secrets, update_secrets
from ..api.spotify import generate_refresh_token
from ..api.mpris import list_players

AUTOMATIC_MPRIS_LABEL = "Automatic"


@Gtk.Template(
    resource_path="/io/github/wispdevon/Spotiverse/views/verse_preferences.ui"
)
class VersePreferences(Adw.PreferencesDialog):
    __gtype_name__ = "VersePreferences"

    mpris_enabled_row = Gtk.Template.Child()
    mpris_player_row = Gtk.Template.Child()
    explicit_lyrics_row = Gtk.Template.Child()
    client_id_row = Gtk.Template.Child()
    client_secret_row = Gtk.Template.Child()
    refresh_token_button = Gtk.Template.Child()
    genius_token_row = Gtk.Template.Child()

    wiki_spotify_url = "https://github.com/wispdevon/Spotiverse/tree/main/wiki#spotify"
    wiki_genius_url = "https://github.com/wispdevon/Spotiverse/tree/main/wiki#genius"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new("io.github.wispdevon.Spotiverse")
        self.mpris_players = []

        self.mpris_enabled_row.connect(
            "notify::active",
            self.mpris_enabled_row_active_cb,
        )
        self.mpris_player_row.connect(
            "notify::selected",
            self.mpris_player_row_selected_cb,
        )
        self.explicit_lyrics_row.connect(
            "notify::active",
            self.explicit_lyrics_row_active_cb,
        )

        self.client_id_row.add_suffix(self.wiki_get_token(self.wiki_spotify_url))
        self.client_secret_row.add_suffix(self.wiki_get_token(self.wiki_spotify_url))
        self.genius_token_row.add_suffix(self.wiki_get_token(self.wiki_genius_url))

        self.update_widgets()

    def mpris_enabled_row_active_cb(self, row, _pspec):
        playback_source = "mpris" if row.get_active() else "spotify"
        self.settings.set_string("playback-source", playback_source)
        self.mpris_player_row.set_sensitive(row.get_active())

    def mpris_player_row_selected_cb(self, row, _pspec):
        selected = row.get_selected()
        if selected == 0:
            self.settings.set_string("mpris-player", "")
            return

        player_index = selected - 1
        if player_index < len(self.mpris_players):
            self.settings.set_string("mpris-player", self.mpris_players[player_index])

    def explicit_lyrics_row_active_cb(self, row, _pspec):
        self.settings.set_boolean("show-explicit-lyrics", row.get_active())

    @Gtk.Template.Callback()
    def client_id_row_applied_cb(self, widget, *args):
        client_id = self.client_id_row.get_text()
        update_secrets(client_id=client_id)
        self.validate_refresh_button_activation()

    @Gtk.Template.Callback()
    def client_secret_row_applied_cb(self, widget, *args):
        client_secret = self.client_secret_row.get_text()
        update_secrets(client_secret=client_secret)
        self.validate_refresh_button_activation()

    def refresh_token_button_pressed_cb(self, widget, *args):
        self.refresh_token_button.set_label("Generating...")
        GLib.idle_add(self.update_refresh_token)

    @Gtk.Template.Callback()
    def genius_token_row_applied_cb(self, widget, *args):
        genius_token = self.genius_token_row.get_text()
        update_secrets(genius_token=genius_token)

    def token_generation_success(self):
        self.refresh_token_button.set_label("Success")
        self.refresh_token_button.remove_css_class("suggested-action")
        self.refresh_token_button.add_css_class("success")
        self.refresh_token_button.set_tooltip_text("Generated Succesfully!")

    def token_generation_failure(self, error):
        self.refresh_token_button.remove_css_class("suggested-action")
        self.refresh_token_button.add_css_class("error")
        self.refresh_token_button.set_label("Error")
        self.refresh_token_button.set_tooltip_text(error)

    def update_refresh_token(self):
        token = generate_refresh_token()

        if "error" not in token:
            self.token_generation_success()
            update_secrets(refresh_token=token["refresh_token"])
        else:
            self.token_generation_failure(token["description"])
            update_secrets(refresh_token=None)

        self.refresh_token_button.disconnect_by_func(self.refresh_token_button_pressed_cb)

    def validate_refresh_button_activation(self):
        secrets = retrieve_secrets()
        if secrets is None:
            return

        self.update_refresh_token_button(secrets, token_changed=True)

    def update_refresh_token_button(self, secrets, token_changed=False):
        if secrets["client-id"] and secrets["client-secret"]:
            self.refresh_token_button.set_sensitive(True)

            if not token_changed and secrets["refresh-token"]:
                self.token_generation_success()
                return
            else:
                self.refresh_token_button.connect("clicked", self.refresh_token_button_pressed_cb)
        else:
            self.refresh_token_button.set_sensitive(False)

        self.refresh_token_button.remove_css_class("success")
        self.refresh_token_button.remove_css_class("error")
        self.refresh_token_button.add_css_class("suggested-action")
        self.refresh_token_button.set_label("Generate")
        self.refresh_token_button.set_tooltip_text("Generate Spotify refresh token")

    def update_widgets(self):
        secrets = retrieve_secrets()
        playback_source = self.settings.get_string("playback-source")
        preferred_mpris_player = self.settings.get_string("mpris-player")
        mpris_enabled = playback_source == "mpris"
        show_explicit_lyrics = self.settings.get_boolean("show-explicit-lyrics")

        self.mpris_players = list_players()
        mpris_labels = [AUTOMATIC_MPRIS_LABEL]
        mpris_labels.extend([player.replace("org.mpris.MediaPlayer2.", "") for player in self.mpris_players])
        self.mpris_player_row.set_model(Gtk.StringList.new(mpris_labels))

        if preferred_mpris_player in self.mpris_players:
            self.mpris_player_row.set_selected(self.mpris_players.index(preferred_mpris_player) + 1)
        else:
            self.mpris_player_row.set_selected(0)

        self.mpris_enabled_row.set_active(mpris_enabled)
        self.mpris_player_row.set_sensitive(mpris_enabled)
        self.explicit_lyrics_row.set_active(show_explicit_lyrics)

        if secrets is None:
            self.update_refresh_token_button(
                {
                    "client-id": None,
                    "client-secret": None,
                    "refresh-token": None,
                }
            )
            return

        if secrets["client-id"]:
            self.client_id_row.set_text(secrets["client-id"])

        if secrets["client-secret"]:
            self.client_secret_row.set_text(secrets["client-secret"])

        if secrets["genius-token"]:
            self.genius_token_row.set_text(secrets["genius-token"])

        self.update_refresh_token_button(secrets)

    def open_wiki(self, button, url):
        GLib.spawn_command_line_async(f"xdg-open {url}")

    def wiki_get_token(self, url):
        info = Gtk.Button()
        info.set_icon_name("dialog-information-symbolic")
        info.set_tooltip_text(_("How to get a token"))
        info.add_css_class("flat")
        info.set_valign(Gtk.Align.CENTER)
        info.connect("clicked", self.open_wiki, url)
        return info
