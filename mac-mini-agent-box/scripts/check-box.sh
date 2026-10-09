#!/bin/bash
# Read-only health check for a Mac mini agent box. Changes nothing, needs no sudo.
# Run on the box as the user Claude Code runs as:  bash check-box.sh
# Prints PASS / WARN / FAIL per line. Secret scan prints file names only, never contents.

t() { perl -e 'alarm shift; exec @ARGV' "$@"; }   # run with a time limit (seconds first)
pass() { printf 'PASS  %s\n' "$1"; }
warn() { printf 'WARN  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1"; }

echo "== Power"
pm="$(pmset -g 2>/dev/null)"
if echo "$pm" | grep -qE '^ *sleep +0( |$)'; then pass "computer sleep is off (sleep 0)"; else fail "computer sleep is not 0; run the pmset lines in references/setup.md"; fi
if echo "$pm" | grep -qE '^ *autorestart +1'; then pass "restart after power failure is on"; else warn "autorestart not shown as 1 (check System Settings, Energy)"; fi

echo "== Login and encryption"
fv="$(fdesetup status 2>/dev/null)"
auto="$(defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>/dev/null)"
case "$fv" in
  *"is On"*)  pass "FileVault is on (power cut needs in-person unlock; use 'sudo fdesetup authrestart' for restarts)";;
  *"is Off"*) if [ -n "$auto" ]; then pass "FileVault off, auto-login as $auto"; else warn "FileVault off and no auto-login: after a power cut nobody is logged in"; fi;;
  *)          warn "could not read FileVault status";;
esac

echo "== Remote access"
if nc -z -G 2 127.0.0.1 22 >/dev/null 2>&1; then pass "Remote Login (SSH) is listening"; else fail "Remote Login (SSH) is not on"; fi
if nc -z -G 2 127.0.0.1 5900 >/dev/null 2>&1; then pass "Screen Sharing is listening"; else warn "Screen Sharing is not on"; fi
if grep -qsE '^ *PasswordAuthentication +no' /etc/ssh/sshd_config.d/*.conf /etc/ssh/sshd_config; then
  pass "SSH password login is switched off in config"
else
  warn "SSH password login not switched off yet (references/tailscale-and-ssh.md, section 3)"
fi
if [ -s "$HOME/.ssh/authorized_keys" ]; then
  pass "$(grep -cE '^(ssh|ecdsa|sk-)' "$HOME/.ssh/authorized_keys") SSH key(s) allowed for $USER"
else
  warn "no SSH keys in ~/.ssh/authorized_keys for $USER"
fi

echo "== Tailscale"
TS="$(command -v tailscale || true)"
[ -z "$TS" ] && [ -x /Applications/Tailscale.app/Contents/MacOS/Tailscale ] && TS=/Applications/Tailscale.app/Contents/MacOS/Tailscale
if [ -z "$TS" ]; then
  if pgrep -qi tailscale; then warn "Tailscale is running but its command line tool is not installed; check the menu bar icon"; else fail "Tailscale not found"; fi
else
  state="$(t 10 "$TS" status --json 2>/dev/null | grep -m1 '"BackendState"' | sed 's/.*: *"\([^"]*\)".*/\1/')"
  if [ "$state" = "Running" ]; then pass "Tailscale connected"; else fail "Tailscale state: ${state:-unknown}"; fi
fi
echo "      (check by hand: key expiry disabled for this machine in the Tailscale admin console)"

echo "== Claude Code"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:$PATH"
if command -v claude >/dev/null; then pass "claude installed: $(t 10 claude --version 2>/dev/null | head -1)"; else fail "claude not found for $USER"; fi
if command -v tmux >/dev/null; then
  if tmux has-session -t cc 2>/dev/null; then pass "tmux session cc is running"; else warn "no tmux session cc for $USER (it runs as the desktop user; see references/claude-code-sessions.md)"; fi
else
  fail "tmux not installed"
fi
for a in local.agentbox.caffeinate local.agentbox.cc-autostart; do
  if launchctl list 2>/dev/null | grep -q "$a"; then pass "LaunchAgent $a loaded"; else warn "LaunchAgent $a not loaded for $USER"; fi
done
if [ -s "$HOME/.claude/CLAUDE.md" ]; then pass "~/.claude/CLAUDE.md exists"; else warn "no ~/.claude/CLAUDE.md house rules yet"; fi

echo "== Backups"
tm="$(t 10 tmutil latestbackup 2>/dev/null)"
if [ -n "$tm" ]; then pass "Time Machine latest backup: $(basename "$tm")"; else warn "no Time Machine backup visible (fine if you use rsync; check that copy by hand)"; fi

echo "== Secret scan (file names only)"
# Written so this file does not itself look like a key to secret scanners.
PAT='(sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{30,}|github_pa[t]_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,}|-{5}BEGIN [A-Z ]*PRIVATE KEY-{5})'
hits=""
for f in "$HOME/.zsh_history" "$HOME/.bash_history" "$HOME/.claude/CLAUDE.md" "$HOME/.zshrc" "$HOME/.zprofile"; do
  [ -f "$f" ] && grep -qE "$PAT" "$f" 2>/dev/null && hits="$hits$f"$'\n'
done
if [ -d "$HOME/work" ]; then
  # small text-like files only, bounded depth and time, so a big work folder cannot hang the check
  more="$(t 60 find "$HOME/work" -maxdepth 5 \( -name node_modules -o -name .git -o -name .venv \) -prune -o \
          -type f -size -512k \( -name '*.env' -o -name '.env*' -o -name '*.md' -o -name '*.json' -o -name '*.sh' \
          -o -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.yaml' -o -name '*.yml' -o -name '*.txt' -o -name '*.toml' \) \
          -print0 2>/dev/null | xargs -0 grep -IlE "$PAT" 2>/dev/null | head -20)"
  [ -n "$more" ] && hits="$hits$more"$'\n'
fi
if [ -z "$hits" ]; then
  pass "no common key patterns in shell history, CLAUDE.md, shell config or ~/work"
else
  fail "possible secrets in these files (rotate them, then remove; see references/secrets.md):"
  printf '%s' "$hits" | sed '/^$/d; s/^/      /'
fi
