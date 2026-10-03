# Driving gotchas

Each of these broke a real take on a headless Mac mini (macOS 26) driven over VNC.

| Symptom | Cause | Fix |
|---|---|---|
| `screencapture: could not create image from display` | Headless Mac, no framebuffer | Keep a VNC client connected (`macvnc.py`) for the whole session |
| `osascript` fails with `-10810`, `open -a` does nothing | Command ran in the SSH session, not the GUI session | Run it through `scripts/gui.sh` (`launchctl asuser`) |
| App opens signed out, or asks to reset the keychain | Launched with the SSH user's HOME | Pass `HOME=/Users/<gui user>`, as `gui.sh` does; never click "Reset to defaults" on a keychain dialog |
| Scroll wheel does nothing on a web page | Safari ignores VNC wheel events on many pages | Use keys: `pgdn`, `space`, `home`, arrow keys |
| `/type` arrives empty | Spaces or `&` in the query string | URL-encode the text (`%20`) |
| Click lands on the wrong thing | Coordinates guessed, or the layout moved after a banner closed | `/shot` before every click that matters and read the coordinates off the image |
| Synthetic clicks via `cliclick` or AppleScript `click` fail | SSH processes have no Accessibility permission, and root cannot grant it | Click over VNC instead; that is a real input device to macOS |
| Minimizing a window from a script is refused | Needs Accessibility, or a guard blocks it | Hide the whole app (`set visible of process "<App>" to false`), or move the window behind with `set bounds` |
| Frame grabs over VNC look choppy | VNC refresh is about 0.3 to 4 fps | Record with the macOS recorder (60 fps); use `/grab_start` only as a fallback |
| The take is suddenly in dark mode | Appearance set to Auto switches at sunset | Set the app's own theme, or record in daylight, or accept it and keep the takes consistent |
| A connector or tool asks permission mid-take | First use per account | Do one dry run first and choose "Always allow" |
| Usage or upgrade banner covers the input | App banners return per session | Close it right before pressing Record |
| AI chat app in the wrong language | It follows the macOS language | Change the app's own language setting, not the system's, on a shared Mac |
| Takes stop halfway through overnight runs | The Mac slept or locked | `caffeinate -dimsu -t <seconds>` for the run; set the lock-screen delay longer than the run |
| Same-Mac connection refused | Screen Sharing is off, or the password is not the macOS login password | Turn on Screen Sharing; connect with your macOS account password |
