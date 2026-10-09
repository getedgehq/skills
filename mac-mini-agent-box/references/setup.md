# The setup as we run it

Do this once, at the box. Admin commands ask for the admin password in the terminal; it never goes
into chat. Placeholders: desktop user `owner`, SSH user `helper`, box `agent-box`.

## 1. Two users

| User | Kind | Who uses it | Why |
|---|---|---|---|
| `owner` | the owner's normal account (admin) | the owner, at the desktop or over Screen Sharing | logs in automatically; Chrome profiles, apps, the screen and screen permissions live here |
| `helper` | admin, SSH only | agents and teammates | own login and keys, so nobody shares the owner's password; reaches the desktop session through `sudo` |

Create `helper`: System Settings, Users & Groups, Add User, type **Administrator**. Pick a long random
password, store it in a password manager, and do not use it day to day (keys, step 3 of
`tailscale-and-ssh.md`).

Apple ID: `helper` signs in to no Apple ID. Keep iCloud on `owner` only if the owner wants it there.

### Acting inside the owner's desktop from SSH

macOS only lets a process use the screen, open apps or bind a browser debugging port inside a logged-in
desktop session. A plain SSH session has none. From `helper`, run desktop commands like this:

```bash
sudo launchctl asuser "$(id -u owner)" sudo -u owner -H env HOME=/Users/owner <command>
```

Examples: `... screencapture -x /tmp/probe.png`, `... open -a Safari`, `... osascript -e '...'`.
Always pass the owner's `HOME`: an app started with the wrong `HOME` opens signed out and can ask to
reset the keychain (never click "Reset to defaults").

### Passwordless sudo for `helper` (our setup; a trust decision)

Without it every `sudo` from an agent waits for a password, so nothing runs unattended. With it,
anyone holding a `helper` SSH key is in full control of the box. Do it only for people and agents the
owner trusts, and only with key-only SSH (password login off).

In Terminal as `owner` (asks for the owner's password once):

```bash
echo 'helper ALL=(ALL) NOPASSWD: ALL' | sudo tee /etc/sudoers.d/helper
sudo chmod 440 /etc/sudoers.d/helper
sudo visudo -cf /etc/sudoers.d/helper
```

The last line must say `parsed OK`. Check from the laptop: `ssh helper@agent-box sudo -n whoami`
prints `root`. Undo at any time: `sudo rm /etc/sudoers.d/helper`.

## 2. Auto-login (FileVault off) or FileVault

macOS turns automatic login off while FileVault is on. Check: `fdesetup status`.

| | Auto-login, FileVault OFF (our setup) | FileVault ON |
|---|---|---|
| After a power cut or crash | logs in by itself, apps and Chrome profiles come back, reachable again | stops at the unlock screen; Tailscale is not running yet, someone must unlock it in person |
| Planned restart | just restart | `sudo fdesetup authrestart` comes back unlocked once |
| Stolen box | thief gets the logged-in account | disk unreadable |

For auto-login:

1. System Settings, Privacy & Security, FileVault, Turn Off (decrypts in the background).
2. System Settings, Users & Groups, "Automatically log in as": `owner`.
3. System Settings, Lock Screen: "Require password after screen saver begins or display is turned
   off": immediately. A person at the keyboard still needs the password; SSH is not affected.
4. Restart once while at the box: it lands on the desktop and Tailscale shows connected.

Compensate: keep the box in a private room, keep secrets in the Keychain or a password manager, never
in plain files.

## 3. Never sleep, restart after a power failure

```bash
sudo pmset -a sleep 0 disksleep 0 displaysleep 10 powernap 0
sudo pmset -a womp 1 autorestart 1 tcpkeepalive 1
pmset -g | grep -E ' sleep|autorestart|womp'
```

`sleep 0`: the computer never sleeps (the screen may). `womp 1`: wake for network access.
`autorestart 1`: start again after a power failure. Also in System Settings, Energy: "Start up
automatically after a power failure" on, and "Prevent automatic sleeping when the display is off" on
if shown. Big macOS upgrades can reset these; re-check after updates.

### Keep-awake agent (what we run)

A LaunchAgent in the owner's session that holds the Mac awake whenever `owner` is logged in. As
`owner`:

```bash
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/local.agentbox.caffeinate.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>local.agentbox.caffeinate</string>
  <key>ProgramArguments</key>
  <array><string>/usr/bin/caffeinate</string><string>-dimsu</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict>
</plist>
EOF
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agentbox.caffeinate.plist
pgrep -fl caffeinate
```

To remove: `launchctl bootout gui/$(id -u)/local.agentbox.caffeinate` and delete the file.

## 4. Sharing settings

System Settings, General, Sharing:

- **Remote Login** on, "Allow access for: only these users": `owner`, `helper`.
- **Screen Sharing** on, same users.

## 5. A screen for a headless box

A Mac mini with no monitor only has a screen while a Screen Sharing client is connected. With no client,
`screencapture` fails with `could not create image from display`, and `caffeinate -u` does not help.
For recordings the recording skill connects its own VNC client (that connection is the screen). If
apps must draw while nobody is connected, plug in an HDMI dummy plug.

## 6. Tools

As `owner` (admin), install Homebrew and the tools agents use:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install tmux ffmpeg python
python3 -m pip install --user websocket-client
```

Follow the "Next steps" Homebrew prints. `helper` can run the same binaries from `/opt/homebrew/bin`
(add `eval "$(/opt/homebrew/bin/brew shellenv)"` to `helper`'s `~/.zprofile`).

`node` and `npm` are not on the PATH of non-interactive SSH commands; start a login shell
(`zsh -lc '...'`) when a command needs them.

## 7. Network

Wired Ethernet if possible. No router port forwarding: Tailscale works through the home router on its
own. Never open SSH or a browser debugging port to the internet.
