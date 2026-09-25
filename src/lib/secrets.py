# secrets.py
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

gi.require_version("Secret", "1")
from gi.repository import Secret
import json
import os
from pathlib import Path

APP_ID = "io.github.wispdevon.Spotiverse"
LEGACY_APP_ID = "io.github.TanmayPatil105.verse"

attrs = {"api_keys": Secret.SchemaAttributeType.STRING}

SECRET_SCHEMA = None
SECRET_KEY = "Spotiverse-Login"

secrets_dict = {
    "client-id": None,
    "client-secret": None,
    "refresh-token": None,
    "genius-token": None,
}

ENV_TO_SECRET_KEYS = {
    "SPOTIFY_CLIENT_ID": "client-id",
    "SPOTIFY_CLIENT_SECRET": "client-secret",
    "GENIUS_TOKEN": "genius-token",
}


def setup_secrets():
    global SECRET_SCHEMA
    global attrs
    if SECRET_SCHEMA is None:
        SECRET_SCHEMA = Secret.Schema.new(APP_ID, Secret.SchemaFlags.NONE, attrs)
    migrate_legacy_secrets()
    import_env_secrets()


def lookup_secrets(schema):
    password = Secret.password_lookup_sync(schema, {}, None)

    try:
        if password:
            return json.loads(password)

    except Exception:
        return None

    return None


def migrate_legacy_secrets():
    if retrieve_secrets() is not None:
        return

    legacy_schema = Secret.Schema.new(LEGACY_APP_ID, Secret.SchemaFlags.NONE, attrs)
    legacy_secrets = lookup_secrets(legacy_schema)
    if not legacy_secrets:
        return

    Secret.password_store_sync(
        SECRET_SCHEMA,
        {},
        Secret.COLLECTION_DEFAULT,
        SECRET_KEY,
        json.dumps(legacy_secrets, indent=2),
        None,
    )


def find_env_file():
    current = Path.cwd()
    for directory in [current, *current.parents]:
        env_file = directory / ".env"
        if env_file.is_file():
            return env_file

    return None


def parse_env_file(env_file):
    values = {}

    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key:
            values[key] = value

    return values


def get_env_value(key, default=None):
    if os.environ.get(key):
        return os.environ[key]

    env_file = find_env_file()
    if not env_file:
        return default

    return parse_env_file(env_file).get(key, default)


def import_env_secrets():
    env_values = {}
    env_file = find_env_file()

    if env_file:
        env_values.update(parse_env_file(env_file))

    for key in ENV_TO_SECRET_KEYS:
        if os.environ.get(key):
            env_values[key] = os.environ[key]

    updates = {}
    for env_key, secret_key in ENV_TO_SECRET_KEYS.items():
        value = env_values.get(env_key)
        if value:
            updates[secret_key] = value

    if updates:
        update_secrets(
            client_id=updates.get("client-id"),
            client_secret=updates.get("client-secret"),
            genius_token=updates.get("genius-token"),
        )


def retrieve_secrets():
    global SECRET_SCHEMA
    return lookup_secrets(SECRET_SCHEMA)


def update_secrets(
    client_id=None, client_secret=None, refresh_token=None, genius_token=None
):
    global SECRET_SCHEMA
    secrets = retrieve_secrets()
    if secrets is None:
        secrets = secrets_dict

    if client_id is not None:
        secrets["client-id"] = client_id
    if client_secret is not None:
        secrets["client-secret"] = client_secret
    if refresh_token is not None:
        secrets["refresh-token"] = refresh_token
    if genius_token is not None:
        secrets["genius-token"] = genius_token

    json_data = json.dumps(secrets, indent=2)

    Secret.password_store_sync(
        SECRET_SCHEMA, {}, Secret.COLLECTION_DEFAULT, SECRET_KEY, json_data, None
    )
