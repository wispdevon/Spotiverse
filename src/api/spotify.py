# spotify.py
#
# Copyright 2024-2025 Tanmay Patil <tanmaynpatil105@gmail.com>
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

import base64
import logging
import requests
import os
from pathlib import Path
from urllib.parse import urlencode
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from ..lib.secrets import get_env_value, retrieve_secrets

# api endpoints
NOW_PLAYING_ENDPOINT = "https://api.spotify.com/v1/me/player/currently-playing"
TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
DEFAULT_REDIRECT_URI = "http://127.0.0.1:53682"
logger = logging.getLogger(__name__)


def get_access_token():

    try:
        secrets = retrieve_secrets()
        client_id = secrets["client-id"]
        client_secret = secrets["client-secret"]
        refresh_token = secrets["refresh-token"]

        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        response = requests.post(
            TOKEN_ENDPOINT,
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            ),
        )

        response.raise_for_status()

        return response.json()["access_token"]

    except Exception:
        logger.exception("Failed to obtain Spotify access token")
        # callee sets the error
        return None


def get_now_playing(access_token):
    try:
        response = requests.get(
            NOW_PLAYING_ENDPOINT,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return None

        return response.json()
    except Exception:
        logger.exception("Failed to fetch Spotify now-playing item")
        return None


def get_now_playing_item():
    access_token = get_access_token()

    if not access_token:
        return {
            "error": "Unable to obtain access token.",
            "description": "Please ensure that the Client ID and Client secret are valid in the Preferences.",
        }

    song = get_now_playing(access_token)
    if not song:
        return {
            "error": "You are currently not listening to anything!",
            "description": "Would you like to try again?",
        }

    try:
        artists = song["item"]["artists"]
        is_playing = song["is_playing"]
        title = song["item"]["name"]
        progress_ms = song.get("progress_ms", 0)
        duration_ms = song["item"].get("duration_ms", 0)
        item_id = song["item"].get("id")
        explicit = song["item"].get("explicit", False)

        return {
            "id": item_id,
            "title": title,
            "artists": artists,
            "is_playing": is_playing,
            "progress_ms": progress_ms,
            "duration_ms": duration_ms,
            "explicit": explicit,
        }
    except Exception:
        logger.exception("Failed to parse Spotify now-playing item")
        return {"error": "Uh-oh, smells like Ads", "description": "It'll pass.."}

def generate_refresh_token():
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    cache_home.mkdir(parents=True, exist_ok=True)
    CACHE_PATH = cache_home / "spotiverse-spotify-token-cache"

    try:
        secrets = retrieve_secrets()
        client_id = secrets["client-id"]
        client_secret = secrets["client-secret"]
        REDIRECT_URI = get_env_value("SPOTIFY_REDIRECT_URI", DEFAULT_REDIRECT_URI)

        cache_handler = CacheFileHandler(cache_path=str(CACHE_PATH))

        sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            scope="user-read-currently-playing",
            cache_handler=cache_handler,
        )

        _auth_code = sp_oauth.get_auth_response()

        _access_token = sp_oauth.get_access_token(_auth_code, as_dict=False)
        refresh_token = sp_oauth.cache_handler.get_cached_token().get("refresh_token")

        if CACHE_PATH.exists():
            CACHE_PATH.unlink()

        return {"refresh_token": refresh_token}
    except Exception as error:
        if CACHE_PATH.exists():
            CACHE_PATH.unlink()

        logger.exception("Failed to generate Spotify refresh token")
        return {
            "error": "Couldn't fetch",
            "description": f"{type(error).__name__}: {error}",
        }
