# Third-party notices

reel-machine is Copyright 2026 Floom, licensed under Apache-2.0 (see LICENSE).

## video-use (MIT)

Portions of scripts/build_reel.py, scripts/make_caps.py, scripts/fit_hook.py and the Scribe
call in scripts/transcribe.py are derived from video-use (https://github.com/browser-use/video-use),
used under the MIT License:

  MIT License

  Copyright (c) 2026 Browser Use

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

Fonts are not bundled. setup.sh downloads Funnel Display (SIL Open Font License 1.1) from the
Google Fonts repository. Logos rendered by logo_png.py come from Simple Icons (CC0); the marks
themselves remain their owners' trademarks.

Not bundled, installed by the user from PyPI (scripts/requirements.txt): faster-whisper (MIT), which
ships the Silero VAD model (MIT) used by pcut.py and vadgaps.py, and OpenCV (Apache-2.0), whose Haar
cascade files are used by facecheck.py. Photos fetched by commons.py stay under their own Wikimedia
Commons licences; commons.py records each author and licence so the post can credit them.
