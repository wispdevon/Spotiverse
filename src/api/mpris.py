# mpris.py
#
# Copyright 2026 wispdevon
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

import logging

from gi.repository import Gio
from gi.repository import GLib


MPRIS_PREFIX = "org.mpris.MediaPlayer2."
MPRIS_OBJECT_PATH = "/org/mpris/MediaPlayer2"
MPRIS_PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
DBUS_TIMEOUT_MS = 1000

logger = logging.getLogger(__name__)


def get_session_bus():
    return Gio.bus_get_sync(Gio.BusType.SESSION, None)


def list_players():
    try:
        bus = get_session_bus()
        result = bus.call_sync(
            "org.freedesktop.DBus",
            "/org/freedesktop/DBus",
            "org.freedesktop.DBus",
            "ListNames",
            None,
            None,
            Gio.DBusCallFlags.NONE,
            DBUS_TIMEOUT_MS,
            None,
        )
        names = result.unpack()[0]
        return sorted([name for name in names if name.startswith(MPRIS_PREFIX)])
    except Exception:
        logger.exception("Failed to list MPRIS players")
        return []


def get_player_properties(player_name):
    bus = get_session_bus()
    result = bus.call_sync(
        player_name,
        MPRIS_OBJECT_PATH,
        "org.freedesktop.DBus.Properties",
        "GetAll",
        GLib.Variant("(s)", (MPRIS_PLAYER_IFACE,)),
        None,
        Gio.DBusCallFlags.NONE,
        DBUS_TIMEOUT_MS,
        None,
    )
    return result.unpack()[0]


def select_player(preferred_player=None):
    players = list_players()
    if not players:
        return None

    if preferred_player and preferred_player in players:
        return preferred_player

    player_states = []
    for player in players:
        try:
            player_states.append((player, get_player_properties(player)))
        except Exception:
            logger.exception("Failed to inspect MPRIS player %s", player)

    for player, properties in player_states:
        if properties.get("PlaybackStatus") == "Playing":
            return player

    for player, _properties in player_states:
        if "spotify" in player.lower():
            return player

    if player_states:
        return player_states[0][0]

    return players[0]


def get_now_playing_item(preferred_player=None):
    player = select_player(preferred_player)
    if not player:
        return {
            "error": "No MPRIS player found.",
            "description": "Start an MPRIS-enabled music player and try again.",
        }

    try:
        properties = get_player_properties(player)
        metadata = properties.get("Metadata", {})
        title = metadata.get("xesam:title")
        artists = metadata.get("xesam:artist") or metadata.get("xesam:albumArtist") or []

        if not title:
            return {
                "error": "No MPRIS track found.",
                "description": "The selected player is not reporting a track.",
            }

        if isinstance(artists, str):
            artists = [artists]

        track_id = str(metadata.get("mpris:trackid") or "")
        duration_us = int(metadata.get("mpris:length") or 0)
        position_us = int(properties.get("Position") or 0)
        playback_status = properties.get("PlaybackStatus")

        return {
            "id": "{}:{}".format(player, track_id or title),
            "title": title,
            "artists": [{"name": artist} for artist in artists],
            "is_playing": playback_status == "Playing",
            "progress_ms": position_us // 1000,
            "duration_ms": duration_us // 1000,
            "source": player,
        }
    except Exception:
        logger.exception("Failed to fetch MPRIS now-playing item from %s", player)
        return {
            "error": "Unable to read MPRIS player.",
            "description": "The selected player did not provide track metadata.",
        }
