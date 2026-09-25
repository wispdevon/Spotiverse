# html.py
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


import json
from html import escape


def lyrics_to_html(lyrics, song, synced_lines=None, font_scale=1.0):
    progress_ms = song.get("progress_ms", 0) or 0
    is_playing = "true" if song.get("is_playing") else "false"
    synced_lines = synced_lines or []

    styles = """
    <style>
        :root {
          color-scheme: dark;
          background: #2f2f2f;
          --bg: #2f2f2f;
          --text: rgba(255, 255, 255, 0.96);
          --past: rgba(255, 255, 255, 0.36);
          --future: rgba(255, 255, 255, 0.28);
          --meta: rgba(255, 255, 255, 0.42);
          --font-scale: FONT_SCALE;
        }

        * {
          box-sizing: border-box;
        }

        html {
          min-height: 100%;
          background: var(--bg);
          scroll-behavior: smooth;
        }

        body {
          min-height: 100%;
          margin: 0;
          background: var(--bg);
          color: var(--text);
          font-family: Inter, "SF Pro Display", "Noto Sans", Cantarell, system-ui, sans-serif;
          letter-spacing: 0;
          overflow-x: hidden;
        }

        main {
          width: 100%;
          min-height: 100vh;
          padding: 42vh clamp(28px, 6vw, 96px);
        }

        header {
          margin: 0 auto clamp(42px, 9vh, 96px);
          text-align: center;
        }

        h1 {
          max-width: 18ch;
          margin: 0;
          color: var(--meta);
          font-size: calc(clamp(26px, 4vw, 52px) * var(--font-scale));
          font-weight: 800;
          line-height: 1.12;
        }

        .artist {
          margin: 12px 0 0;
          color: var(--meta);
          font-size: calc(clamp(16px, 2vw, 24px) * var(--font-scale));
          font-weight: 750;
          line-height: 1.25;
        }

        .lyrics {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: clamp(36px, 6vh, 72px);
          padding-bottom: 45vh;
        }

        .line,
        .section {
          max-width: min(16ch, 92vw);
          margin: 0;
          text-align: center;
          text-wrap: balance;
          transition:
            color 160ms ease,
            opacity 160ms ease,
            transform 160ms ease;
        }

        .line {
          color: var(--future);
          font-size: calc(clamp(44px, 8vw, 92px) * var(--font-scale));
          font-weight: 800;
          line-height: 1.08;
        }

        .line.is-past {
          color: var(--past);
        }

        .line.is-active {
          color: var(--text);
          transform: scale(1.02);
        }

        .section {
          color: var(--meta);
          font-size: calc(clamp(28px, 4.8vw, 56px) * var(--font-scale));
          font-weight: 800;
          line-height: 1.12;
        }

        .spacer {
          height: 0.25rem;
        }

        @media (max-width: 560px) {
          main {
            padding-inline: 24px;
          }

          h1,
          .line,
          .section {
            max-width: 11ch;
          }
        }
    </style>
    """.replace("FONT_SCALE", f"{font_scale:.2f}")

    script = """
    <script>
      const syncedLines = %s;
      let playback = {
        progressMs: %d,
        isPlaying: %s,
        updatedAt: Date.now(),
      };

      function currentProgressMs() {
        if (!playback.isPlaying) {
          return playback.progressMs;
        }
        return playback.progressMs + Date.now() - playback.updatedAt;
      }

      function activeIndex(progressMs) {
        if (!syncedLines.length) {
          return -1;
        }

        let low = 0;
        let high = syncedLines.length - 1;
        let result = 0;

        while (low <= high) {
          const mid = Math.floor((low + high) / 2);
          if (syncedLines[mid].time_ms <= progressMs) {
            result = mid;
            low = mid + 1;
          } else {
            high = mid - 1;
          }
        }

        return result;
      }

      function renderActiveLine() {
        const index = activeIndex(currentProgressMs());
        const lines = document.querySelectorAll("[data-lyric-index]");

        lines.forEach((line, lineIndex) => {
          line.classList.toggle("is-active", lineIndex === index);
          line.classList.toggle("is-past", lineIndex < index);
        });

        const active = lines[index];
        if (active) {
          const top = active.offsetTop - (window.innerHeight / 2) + (active.offsetHeight / 2);
          window.scrollTo({ top, behavior: "smooth" });
        }
      }

      window.updatePlayback = (progressMs, isPlaying) => {
        playback = {
          progressMs,
          isPlaying,
          updatedAt: Date.now(),
        };
        renderActiveLine();
      };

      window.setFontScale = (scale) => {
        document.documentElement.style.setProperty("--font-scale", scale);
        renderActiveLine();
      };

      window.addEventListener("load", () => {
        renderActiveLine();
        if (syncedLines.length) {
          setInterval(renderActiveLine, 500);
        }
      });
    </script>
    """ % (
        json.dumps(synced_lines),
        progress_ms,
        is_playing,
    )

    html = "<!DOCTYPE html>\n<html>\n<head>{}{}</head>\n<body>\n<main>".format(
        styles,
        script,
    )

    lines = lyrics.split("\n")

    html += "<header>\n"
    html += "<h1>{}</h1>\n".format(escape(song["title"]))
    artist = ", ".join([_artist["name"] for _artist in song["artists"]])
    html += '<p class="artist">by {}</p>\n'.format(escape(artist))
    html += "</header>\n<section class=\"lyrics\">\n"

    if synced_lines:
        for index, line in enumerate(synced_lines):
            html += '\t<p class="line" data-lyric-index="{}">{}</p>\n'.format(
                index,
                escape(line["text"]),
            )
    else:
        for line in lines:
            line = line.strip()
            if not line:
                html += "\t<div class=\"spacer\"></div>\n"
                continue

            line = escape(line)
            if line.startswith("["):
                html += "\t<p class=\"section\">{}</p>\n".format(line)
            else:
                html += "\t<p class=\"line\">{}</p>\n".format(line)

    html += "\t</section>\n</main>\n</body>\n</html>"

    return html
