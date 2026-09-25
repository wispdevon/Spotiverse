<a id="readme-top"></a>

<div align="center">
  <img src="data/icons/hicolor/scalable/apps/io.github.TanmayPatil105.verse.svg" alt="Spotiverse logo" width="160" height="160">

  <h1>Spotiverse</h1>

  <p>
    A GTK lyrics companion for Spotify with synced, Spotify-style lyrics.
    <br>
    <a href="https://github.com/wispdevon/Spotiverse/issues">Report Bug</a>
    ·
    <a href="https://github.com/wispdevon/Spotiverse/issues">Request Feature</a>
  </p>
</div>

## Table of Contents

1. [About The Project](#about-the-project)
   - [Built With](#built-with)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [API Keys](#api-keys)
3. [Usage](#usage)
4. [Roadmap](#roadmap)
5. [Contributing](#contributing)
6. [License](#license)
7. [Contact](#contact)
8. [Acknowledgments](#acknowledgments)

## About The Project

Spotiverse is a fork of [verse](https://github.com/TanmayPatil105/verse), a small Linux desktop app that fetches lyrics for the song currently playing on Spotify.

This fork reshapes the experience around a Spotify-like lyric display:

- Synced lyrics when timestamped LRC lyrics are available
- Automatic updates when the current Spotify track changes
- Playback-aware lyric highlighting and centered active lines
- Dark, full-window lyric presentation
- Keyboard zoom with `Ctrl++` and `Ctrl+-`
- Local `.env` support for Spotify and Genius credentials
- Configurable Spotify callback port with `SPOTIFY_REDIRECT_URI`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [Python](https://www.python.org/)
- [GTK 4](https://www.gtk.org/)
- [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- [WebKitGTK](https://webkitgtk.org/)
- [Meson](https://mesonbuild.com/)
- [Spotipy](https://spotipy.readthedocs.io/)
- [lyricsgenius](https://lyricsgenius.readthedocs.io/)
- [syncedlyrics](https://pypi.org/project/syncedlyrics/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

These instructions set up a local development build.

### Prerequisites

On Debian, Ubuntu, Mint, or similar:

```console
sudo apt install meson ninja-build python3-pip python3-setuptools libgtk-4-dev libadwaita-1-dev libwebkitgtk-6.0-dev libsecret-1-dev
```

Install Python dependencies:

```console
python3 -m pip install --user -r requirements.txt
```

Some distributions protect the system Python environment. If `pip` reports an externally managed environment, use a virtual environment or your distribution packages instead.

### Installation

Clone the fork:

```console
git clone https://github.com/wispdevon/Spotiverse.git
cd Spotiverse
```

Create your local environment file:

```console
cp .env.example .env
```

Build and install into a local prefix:

```console
meson setup _build --prefix "$PWD/_install"
meson compile -C _build
meson install -C _build
```

Run the local build:

```console
GSETTINGS_SCHEMA_DIR="$PWD/_install/share/glib-2.0/schemas" "$PWD/_install/bin/verse"
```

You can also build through GNOME Builder or install through Flatpak Builder:

```console
flatpak-builder --force-clean _flatpak/ io.github.TanmayPatil105.verse.json --user --install
flatpak run io.github.TanmayPatil105.verse
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### API Keys

Spotiverse needs Spotify API credentials and a Genius access token.

Add these values to `.env`:

```env
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=http://127.0.0.1:53682
GENIUS_TOKEN=
```

In the Spotify Developer Dashboard, add the exact redirect URI from `SPOTIFY_REDIRECT_URI`.

For more detail, see [wiki/README.md](wiki/README.md).

After the app starts, open Preferences with `Ctrl+O` and generate the Spotify refresh token.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

1. Start Spotify and play a track.
2. Launch Spotiverse.
3. If credentials are not configured yet, press `Ctrl+O` to open Preferences.
4. Generate the Spotify refresh token.
5. Return to the lyrics window.

Useful shortcuts:

- `Ctrl+O`: Open Preferences
- `Ctrl+R`: Refresh the current track
- `Ctrl++`: Increase lyric font size
- `Ctrl+-`: Decrease lyric font size
- `Ctrl+Q`: Quit

If synced lyrics are found, the active line follows the current Spotify playback position. If no synced lyrics are available, Spotiverse falls back to regular Genius lyrics.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- Improve synced lyric provider matching and fallbacks
- Add a small in-window control surface for refresh, preferences, and zoom
- Persist lyric zoom preferences
- Add screenshots for the synced lyrics view
- Package the fork under its own app ID

See the [open issues](https://github.com/wispdevon/Spotiverse/issues) for proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

Contributions are welcome.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the Apache-2.0 License. See [COPYING](COPYING) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Project Link: [https://github.com/wispdevon/Spotiverse](https://github.com/wispdevon/Spotiverse)

Upstream Project: [https://github.com/TanmayPatil105/verse](https://github.com/TanmayPatil105/verse)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

- [Tanmay Patil](https://github.com/TanmayPatil105) for the original verse project
- [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Genius API](https://docs.genius.com/)
- [LRCLIB](https://lrclib.net/)
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
