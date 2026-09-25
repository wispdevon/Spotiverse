# lyrics.py
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

import os
import re
import lyricsgenius
import syncedlyrics
from ..lib.secrets import retrieve_secrets
from ..lib.utils import sanitize_title


LRC_TIMESTAMP_PATTERN = re.compile(r"\[(\d{1,2}):(\d{2})(?:[.:](\d{1,3}))?\]")


def parse_lrc(lrc):
    lines = []

    for raw_line in lrc.splitlines():
        timestamps = LRC_TIMESTAMP_PATTERN.findall(raw_line)
        text = LRC_TIMESTAMP_PATTERN.sub("", raw_line).strip()
        if not timestamps or not text:
            continue

        for minutes, seconds, fraction in timestamps:
            fraction = (fraction or "0").ljust(3, "0")[:3]
            time_ms = (
                int(minutes) * 60 * 1000
                + int(seconds) * 1000
                + int(fraction)
            )
            lines.append({"time_ms": time_ms, "text": text})

    return sorted(lines, key=lambda line: line["time_ms"])


def get_synced_lyrics(song_title, artist_name):
    try:
        title = sanitize_title(song_title)
        lrc = syncedlyrics.search(
            f"{title} {artist_name}",
            synced_only=True,
            providers=["Lrclib", "NetEase", "Megalobiz"],
        )

        if not lrc:
            return {
                "error": "No synced lyrics found",
                "description": f"Couldn't find timed lyrics for {title}",
            }

        lines = parse_lrc(lrc)
        if not lines:
            return {
                "error": "No synced lyrics found",
                "description": f"Couldn't parse timed lyrics for {title}",
            }

        return {"lyrics": "\n".join([line["text"] for line in lines]), "synced": lines}
    except Exception:
        return {
            "error": "Unable to fetch synced lyrics",
            "description": "Timed lyrics search failed.",
        }


def get_lyrics(song_title, artist_name):
    try:
        secrets = retrieve_secrets()
        genius_token = secrets["genius-token"]
        genius = lyricsgenius.Genius(genius_token, verbose=False)

        title = sanitize_title(song_title)
        song = genius.search_song(title, artist_name)

        if not song:
            return {
                "error": "No Lyrics found",
                "description": f"Couldn't find the lyrics for {title}",
            }

        return {"lyrics": song.lyrics}
    except:
        return {
            "error": "Unable to fetch lyrics",
            "description": "Please ensure that the Genius token is valid in the Preferences.",
        }
