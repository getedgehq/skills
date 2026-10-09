# Safety, backups and updates

Read this for step 7.

## 1. What an agent may and may not do on the box

The CLAUDE.md template (`claude-md-template.md`) carries these rules so the agent reads them every
time. The short list:

May, without asking:

- read, write and run things inside `~/work` and its own temp folders;
- install packages for a project inside the project (npm, pip in a virtualenv, uv);
- start and stop its own processes and tmux windows.

Must ask the owner first:

- deleting files outside `~/work`, or anything it did not create;
- sending a message or email, posting, publishing, pushing to a shared repo, spending money;
- installing system-wide software (Homebrew needs the admin account anyway);
- restarting the box, or stopping someone else's process.

Never:

- touch Tailscale, Remote Login, Screen Sharing, firewall, users, passwords or FileVault;
- read or print secrets, or write them into any file (see `secrets.md`);
- disable the safety settings in CLAUDE.md or `~/.claude/settings.json`.

On permission modes: with secrets on the box, keep Claude Code asking for permission on risky actions.
Do not run it with permission checks switched off as a default; if the owner wants that for a
specific project, do it in a separate macOS user or folder with no secrets.

## 2. Etiquette on a shared box

When more than one person (or a helper's agent) uses the box:

- **Look before you act:** `who` shows who is logged in; check for an open Screen Sharing session
  (`ps aux | grep -i screensharingd | grep -v grep`). If the owner is working, wait or ask.
- Never quit, close or move someone else's apps or windows. Hide or cover them if needed.
- Never reboot, log anyone out, change system settings or touch Tailscale without asking.
- Use your own user or your own tmux session name (`tmux new -A -s yourname`); never take over or kill `cc`.
- Clean up: delete your temp files, stop processes you started, restore anything you changed.

## 3. Backups

Pick one and test a restore.

**Time Machine** (simplest): plug in an external disk, System Settings, General, Time Machine, Add
Backup Disk. It backs up hourly. Check from Terminal:

```bash
tmutil latestbackup
tmutil listbackups | tail -3
```

**rsync to an external disk** (just the work folders, nightly): replace `Backup` with the disk name.

```bash
rsync -a ~/work/ "/Volumes/Backup/agent-box-work/"
```

To run it every night at 3:00, as `owner`:

```bash
(crontab -l 2>/dev/null; echo '0 3 * * * rsync -a "$HOME/work/" "/Volumes/Backup/agent-box-work/"') | crontab -
```

Check the next morning that the folder on the disk was updated. If it was not, macOS privacy settings
blocked it: System Settings, Privacy & Security, Full Disk Access, click +, press `Cmd-Shift-G`, type
`/usr/sbin/cron`, add it.

Leave out `--delete` until you are sure, so a mistake on the box does not also delete the backup.

Code also lives in git: push project repos to GitHub (private) regularly, never with secrets inside.

**Test a restore:** copy one file back from the backup to a temp folder and open it. A backup that
was never restored is a guess.

## 4. Updates

Monthly, or when something needs it. Tell anyone else using the box first.

```bash
softwareupdate -l              # list macOS updates (admin account)
brew update && brew upgrade    # tools (admin account)
claude update                  # Claude Code (as owner; it also updates itself)
```

Tailscale: the Mac app updates itself (or via the App Store). Updating Tailscale drops the connection
for a moment; do it from the local network or when someone can check the box.

Install macOS updates with a controlled restart:

```bash
sudo softwareupdate -i -a      # installs, does not restart by itself unless required
sudo fdesetup authrestart      # FileVault on: restart and come back online
sudo shutdown -r now           # FileVault off
```

After any restart, run the checklist in SKILL.md step 8 again (at least: reachable from phone, `cc` back,
Claude logged in, `pmset -g` still shows `sleep 0`). Big macOS upgrades sometimes reset energy
settings; re-run the `pmset` lines if needed.

Automatic updates: in System Settings, General, Software Update, Automatic updates, turn **off**
"Install macOS updates" so the box never restarts on its own in the middle of a job; keep "Install
Security Responses and system files" on.
