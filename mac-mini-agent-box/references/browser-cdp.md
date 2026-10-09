# Always-on, logged-in Chrome profiles that agents drive over CDP

What we run: one dedicated Chrome profile per account (one per person or per tool login), each a
LaunchAgent in the **owner's desktop session**, each with its own Chrome DevTools Protocol (CDP)
port. A human logs each profile in once over Screen Sharing; after that agents drive it, and the
login survives relaunches and reboots. A real Chrome on a home connection passes bot checks that block
cloud servers and automation-launched browsers.

## Why it must run in the owner's desktop session

Chrome only opens its debugging port inside a logged-in desktop session. A Chrome started from a
plain SSH login, or with `open` from the `helper` user, does not bind. Run it as the owner, inside
the owner's session: as a LaunchAgent in `/Users/owner/Library/LaunchAgents` (below), or once by hand:

```bash
sudo launchctl asuser "$(id -u owner)" sudo -u owner -H "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --user-data-dir=/Users/owner/ChromeProfiles/Work --remote-debugging-port=9334 \
  --no-first-run --no-default-browser-check https://example.com &
```

## Ports and profiles

Pick one port per profile and write the map into the owner's notes, for example:

| Profile folder | Port | Account |
|---|---|---|
| `~/ChromeProfiles/Work` | 9334 | owner's work logins |
| `~/ChromeProfiles/Teammate` | 9335 | a teammate's logins |

Each profile needs its own `--user-data-dir`. Chrome refuses remote debugging on its default profile,
and separate folders keep accounts apart.

Keep CDP on `127.0.0.1` (Chrome's default). Anyone who can reach a CDP port controls that logged-in
browser, so never expose it on the network or the tailnet. Reach it from elsewhere through SSH.

## Always on: one LaunchAgent per profile (as `owner`)

```bash
P=Work; PORT=9334
mkdir -p ~/ChromeProfiles/$P ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/local.agentbox.chrome-$P.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>local.agentbox.chrome-$P</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Applications/Google Chrome.app/Contents/MacOS/Google Chrome</string>
    <string>--user-data-dir=$HOME/ChromeProfiles/$P</string>
    <string>--remote-debugging-port=$PORT</string>
    <string>--no-first-run</string>
    <string>--no-default-browser-check</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
EOF
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agentbox.chrome-$P.plist
curl -s http://127.0.0.1:$PORT/json/version | head -3
```

The agent runs the Chrome binary directly (not `open -na`), so KeepAlive can watch it.

**KeepAlive means `pkill` is useless**: Chrome comes back in about 30 seconds. To stop a profile:

```bash
launchctl bootout gui/$(id -u)/local.agentbox.chrome-Work
```

To switch it off for good, also move the plist to `~/Library/LaunchAgents.disabled/` (keep the profile
folder, so the logins survive if you turn it back on). From `helper`, wrap these in
`sudo launchctl asuser "$(id -u owner)" sudo -u owner -H ...`; reading the owner's LaunchAgents folder
as `helper` needs `sudo`, so check with `sudo ls` before concluding a plist is missing.

## Logging a profile in (human step)

Open Screen Sharing to the box as `owner`, find that profile's window, and the account holder types
their login and 2FA. Agents never type passwords or solve CAPTCHAs. Afterwards, check which account
sits on which port instead of assuming (open the site and read the signed-in name with
`scripts/cdp_tab.py shot <url>`).

## Logins that survive reboots

Chrome encrypts its cookies with a key stored in the owner's login keychain. With auto-login, that
keychain unlocks at login, so a Chrome started at boot reads its cookies. If profiles come back signed
out after a reboot, the login keychain is not the default one. Fix it as `owner`, in a desktop
Terminal (it asks for the owner's password; type it at the prompt, never on the command line):

```bash
security list-keychains -d user
security default-keychain -d user
security list-keychains -d user -s ~/Library/Keychains/login.keychain-db /Library/Keychains/System.keychain
security default-keychain -d user -s ~/Library/Keychains/login.keychain-db
```

The first two lines only show the current state; the last two make the login keychain the user's
search list and default. When running them from `helper`, wrap them in
`sudo launchctl asuser "$(id -u owner)" sudo -u owner -H ...` (`-H` is mandatory, or they change
`helper`'s keychain settings instead).

**The trap:** never test persistence by setting a cookie and killing Chrome right away. Chrome writes
cookies to disk on a timer (about 30 seconds) or on a graceful shutdown, so a hard kill loses them
whatever the keychain state, and you chase a problem that is not there. Test it properly, on the box:

```bash
CDP_URL=http://127.0.0.1:9334 python3 scripts/cdp_tab.py persist seed
CDP_URL=http://127.0.0.1:9334 python3 scripts/cdp_tab.py persist close   # graceful; KeepAlive relaunches
sleep 45
CDP_URL=http://127.0.0.1:9334 python3 scripts/cdp_tab.py persist check   # SURVIVED / LOST
```

Repeat the `check` after a full reboot.

## Driving it

- **Best: run the driver on the box** (over SSH as `owner`, or in your window of `cc`), talking to
  `127.0.0.1:<port>`. CDP websocket commands can stall through a double SSH hop.
- **From another machine:** tunnel the port and keep `CDP_URL` on localhost:
  `ssh -N -L 9334:127.0.0.1:9334 owner@agent-box` then `CDP_URL=http://127.0.0.1:9334`.
  `scripts/cdp_tab.py` rewrites the browser's websocket address to yours (needed through a tunnel)
  and sends no `Origin` header, so Chrome needs no `--remote-allow-origins` flag.
- Always work in **your own new tab** (`CdpTab()` creates one) and close it in a `finally` block. Never
  navigate, close or reload the account's existing tabs, and never quit Chrome.
- Many tabs at once are fine (one per worker); keep it to about six, and close every one.
