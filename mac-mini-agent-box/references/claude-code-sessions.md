# Claude Code on the box: the `cc` session

What we run: Claude Code inside a tmux session named `cc`, started from **Terminal.app in the owner's
desktop session**, plus a keeper LaunchAgent that restarts it when it is missing.

Why from Terminal and not from SSH: macOS gives screen and automation permissions (Screen Recording,
Automation, Accessibility) to apps, not to SSH logins. A tmux server started by Terminal inherits
Terminal's permissions, so `screencapture`, `osascript` and similar commands sent into `cc` work, while
the same command over plain SSH fails (`could not create image from display`, `-10810`). The owner's
login keychain is also unlocked in the desktop session, so Claude stays logged in.

## 1. Install Claude Code (as `owner`)

```bash
curl -fsSL https://claude.ai/install.sh | bash
exec zsh -l
claude --version
```

## 2. The launcher and the keeper (as `owner`)

The launcher starts a detached tmux session `cc` running `claude`, then waits as long as `cc` exists
(that keeps the Terminal window, and with it the permissions, alive):

```bash
cat > ~/start-cc.sh <<'EOF'
#!/bin/zsh
eval "$(/opt/homebrew/bin/brew shellenv)"
if ! /opt/homebrew/bin/tmux has-session -t cc 2>/dev/null; then
  /opt/homebrew/bin/tmux new-session -d -s cc -x 220 -y 50
  sleep 1
  /opt/homebrew/bin/tmux send-keys -t cc "claude" Enter
  echo "started $(date)" > /tmp/cc-started.log
fi
while /opt/homebrew/bin/tmux has-session -t cc 2>/dev/null; do sleep 30; done
EOF
chmod +x ~/start-cc.sh
```

The keeper runs at login and every 2 minutes, and opens the launcher in Terminal only when `cc` is gone:

```bash
cat > ~/cc-keeper.sh <<'EOF'
#!/bin/zsh
# Ensure the cc tmux session (started from Terminal, so it has Terminal's permissions) is up.
if ! /opt/homebrew/bin/tmux has-session -t cc 2>/dev/null; then
  /usr/bin/open -a Terminal "$HOME/start-cc.sh"
fi
EOF
chmod +x ~/cc-keeper.sh
mkdir -p ~/Library/LaunchAgents
cat > ~/Library/LaunchAgents/local.agentbox.cc-autostart.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>local.agentbox.cc-autostart</string>
  <key>ProgramArguments</key>
  <array><string>$HOME/cc-keeper.sh</string></array>
  <key>RunAtLoad</key><true/>
  <key>StartInterval</key><integer>120</integer>
  <key>StandardErrorPath</key><string>/tmp/cc-keeper.err</string>
  <key>StandardOutPath</key><string>/tmp/cc-keeper.out</string>
</dict>
</plist>
EOF
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agentbox.cc-autostart.plist
```

Within 2 minutes a Terminal window opens and `tmux ls` shows `cc`. To pause the keeper (for example
while changing the setup): `launchctl bootout gui/$(id -u)/local.agentbox.cc-autostart`; start it
again with the `bootstrap` line above.

## 3. One-time human steps (owner, at the desktop or over Screen Sharing)

1. Attach once (`tmux attach -t cc`) and log Claude in: it shows a link; open it on the laptop or phone,
   approve, paste back the code if asked. Nothing else gets pasted.
2. Give Terminal the permissions the flows need: System Settings, Privacy & Security, **Screen &
   System Audio Recording**: add Terminal. Accept the Automation prompts the first time a script
   controls Safari or System Events.
3. Test from inside `cc`: `screencapture -x /tmp/probe.png && echo OK`, then delete the file.

## 4. Using it from laptop and phone

| You want to | Type |
|---|---|
| owner: attach to Claude | `ssh owner@agent-box` then `tmux attach -t cc` |
| helper: attach to the owner's Claude | `ssh helper@agent-box` then `sudo -u owner -H /opt/homebrew/bin/tmux attach -t cc` |
| leave it running | `Ctrl-b` then `d` |
| your own session, not touching `cc` | `tmux new -A -s yourname` |
| run one command in the `cc` context from SSH (screen permissions) | `tmux new-window -t cc -n yourname` once, then `tmux send-keys -t cc:yourname '<command>' Enter` |
| read what a window shows | `tmux capture-pane -t cc:yourname -p \| tail -20` |

Phone: Tailscale app on, SSH app (Termius or Blink Shell) to `agent-box`, then the attach line. Turn
the phone sideways; most SSH apps have a Ctrl key above the keyboard for `Ctrl-b d`.

Mouse and finger scrolling in tmux: `printf 'set -g mouse on\nset -g history-limit 50000\n' >> ~/.tmux.conf`.

Rules: never kill `cc` or its tmux server (`tmux kill-server` kills everyone's sessions). Close windows
you added to `cc` when done (`tmux kill-window -t cc:yourname`).

## 5. Screen Sharing for logins

From the laptop: Finder, Go, Connect to Server, `vnc://agent-box`, sign in as `owner`. From the phone: a
VNC app to `agent-box`. Use it for website logins, 2FA and first-run dialogs; close the window when done
(it takes your laptop's mouse focus while open). Agents should not drive the desktop through your
laptop's Screen Sharing window; the recording skill has its own headless VNC controller.
