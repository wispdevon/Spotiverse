# lyrics_view.py
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

import gi
from gi.repository import Adw
from gi.repository import Gtk

gi.require_version("WebKit", "6.0")
from gi.repository import WebKit

from ..lib.html import lyrics_to_html


@Gtk.Template(resource_path="/io/github/TanmayPatil105/verse/views/lyrics_view.ui")
class LyricsView(Adw.Bin):
    __gtype_name__ = "LyricsView"

    carousel = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pending_view = None
        self.current_view = None
        self.font_scale = 1.0

        # Optimize page loading
        self.settings = WebKit.Settings()
        self.settings.set_enable_javascript(True)
        self.settings.set_enable_page_cache(False)

    def append_view(self, view):
        self.carousel.append(view)
        self.current_view = view
        if self.pending_view is None:
            view.connect("load-changed", self.on_view_load_changed)
            self.pending_view = view

    def on_view_load_changed(self, web_view, load_event):
        if load_event == WebKit.LoadEvent.FINISHED:
            web_view.disconnect_by_func(self.on_view_load_changed)
            # instantly scroll
            self.carousel.scroll_to(web_view, True)
            self.pending_view = None

    def append(self, lyrics, song, synced_lines=None):
        view = WebKit.WebView()
        view.set_settings(self.settings)
        html = lyrics_to_html(lyrics, song, synced_lines, self.font_scale)
        view.load_html(html)
        view.set_vexpand(True)
        view.set_hexpand(True)
        self.append_view(view)

    def update_playback(self, progress_ms, is_playing):
        if not self.current_view:
            return

        is_playing_value = "true" if is_playing else "false"
        script = f"window.updatePlayback({int(progress_ms or 0)}, {is_playing_value});"
        self.current_view.evaluate_javascript(script, -1)

    def zoom_font(self, delta):
        self.font_scale = min(1.8, max(0.65, self.font_scale + delta))

        if not self.current_view:
            return

        script = f"window.setFontScale({self.font_scale:.2f});"
        self.current_view.evaluate_javascript(script, -1)
