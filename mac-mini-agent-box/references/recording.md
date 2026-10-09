# Recording real demos on the box

The recording flow is its own published skill. Install it on the box (and on any helper machine that
drives recordings):

```bash
npx skills add getedgehq/skills --skill record-mac-demo
```

Read its `SKILL.md`, `references/framing.md` and `references/gotchas.md` before the first take. This
file only adds how it fits this box, plus the notes from our own takes on a shared, headless Mac mini.

## Which setup of record-mac-demo to use

| Who records | Run the controller (`scripts/macvnc.py`) | `MACVNC_HOST` | `MACVNC_USER` |
|---|---|---|---|
| Claude on the box itself (in `cc` or your own tmux window) | on the box | `127.0.0.1` | `owner` |
| A helper's agent on another machine | on the helper's machine, over Tailscale | `agent-box` (or the full `.ts.net` name) | `owner` |

In both cases the target is the **owner's desktop session** (that is where the apps and the screen
are). The VNC password is the owner's macOS password: save it once in the controller machine's
keychain, or inject it into the controller's environment only. Never on a command line, in a prompt
or in a file. For `scripts/gui.sh` from a helper machine: `MAC_SSH="ssh helper@agent-box"
GUI_USER=owner`.

## Pre-flight gate (every time)

The box is headless: no screen exists until a VNC client connects. Start the controller first, then:

```bash
curl -s 'http://127.0.0.1:8765/shot?out=/tmp/probe.png'
```

Look at the image. A real desktop at full size: go. Black, login window or lock screen: stop and
report; logging in at the console is a human step. Never fake footage.

## Notes from our takes (not in the published skill)

- **Do not drive the box through the Screen Sharing window on your laptop.** It steals your mouse and
  focus while you work, and stops updating when minimized. Use the headless controller.
- **Stale screen:** after a while the controller's screenshots can stop updating while clicks still
  land. If two shots after an action are identical, restart the controller before concluding
  anything. If another session already holds port 8765, use `MACVNC_PORT=8766`.
- **App language:** a Mac set to another language makes the Claude app default to it, and that cannot
  be fixed in the edit. For the Claude desktop app, back up
  `~/Library/Application Support/Claude/config.json` (in the owner's home), set `"locale": "en-US"`,
  quit and relaunch it with the owner's `HOME` (see `setup.md`). Check a screenshot shows English
  before recording. macOS's own dialogs (file picker, recorder toolbar) stay in the system language,
  so approve folders and connectors in a dry run, outside the take.
- **Never restart the Claude app casually.** A relaunch with the wrong `HOME` signed the account out.
- **Web inputs:** for text fields in Safari, setting the value through AppleScript `do JavaScript`
  (native value setter plus an `input` event) is more reliable than synthetic keystrokes.
- **Edge demos only count if the agent really uses Edge.** Watch the first two or three minutes: if
  the agent never calls `find_skill`, or skips `use_skill`, stop the run and report instead of letting
  a 30 to 50 minute run finish.
- **Pulling files:** recordings belong to `owner`. From a helper machine:
  `ssh helper@agent-box 'sudo -n cat "/Users/owner/Recordings/<file>.mov"' > take.mov`, then delete
  the file on the box. `ffmpeg` on the box (`/opt/homebrew/bin/ffmpeg`) can cut check frames there.

## Leave it as you found it

Delete every recording and temp file you made, restore windows, dock and menu bar, stop the
controller and any `caffeinate` or `screencapture` you started. Leftovers on a shared machine are the
owner's problem; do not create them.
