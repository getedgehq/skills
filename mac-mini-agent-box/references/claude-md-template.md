# CLAUDE.md template for the agent box

Copy everything below the line into `~/.claude/CLAUDE.md` of the user Claude Code runs as (normally `owner`, where the `cc` session runs).
Fill in the parts in angle brackets. Keep the safety sections as they are. Never put a secret value in
this file; only say *how* a secret is fetched.

```bash
mkdir -p ~/.claude && nano ~/.claude/CLAUDE.md
```

---

# Agent box house rules

## About this machine

- This is an always-on Mac mini used as an agent box by <owner first name>.
- It is reached remotely over Tailscale (SSH and Screen Sharing). Nobody is usually sitting at it.
- It is used for: <what the box is for, e.g. "building my website, research, running scripts">.
- Work lives in `~/work/<project>`. Create new projects there.

## Never cut the connection

The owner reaches this box only through Tailscale and SSH. Never quit, log out of or reconfigure
Tailscale, never run `tailscale down`, never change Remote Login, Screen Sharing, the firewall, SSH
settings, users, passwords or FileVault, and never restart the machine. If a task seems to need one
of these, stop and ask.

## Ask before

- deleting anything outside `~/work`, or anything you did not create in this session;
- sending messages or emails, posting, publishing, opening pull requests, pushing to shared branches;
- spending money or signing up for paid services;
- installing system-wide software (ask the owner; Homebrew installs need the admin account);
- stopping processes you did not start.

## Secrets

- Never ask the owner to paste a key, token or password into chat. Never print, log or write a
  secret into any file, commit, message or screenshot.
- Fetch secrets only inside the command that needs them:
  `with-secret <NAME> <command>` (macOS Keychain) <or: `op run --env-file <file> -- <command>`>.
- Available secret names: <list names only, e.g. OPENAI_API_KEY, GITHUB_TOKEN>.
- If a needed secret is missing, say which name is missing and how the owner can add it:
  `security add-generic-password -a "$USER" -s <NAME> -w`.
- If you ever see a secret in plain text, stop and tell the owner it should be rotated.

## Shared machine etiquette

- Before acting, check whether someone is working (`who`, an open Screen Sharing session). If so, do
  not take over the screen.
- Never quit or close other people's apps or windows.
- Never kill the `cc` tmux session or the tmux server; use your own window or session.
- Logged-in Chrome profiles: work only in a new tab you opened and close it when done; never quit
  Chrome, never touch another account's tabs, never type passwords or solve CAPTCHAs (logins and 2FA
  are done by a human over Screen Sharing).
- Clean up temp files and processes you started.

## Working style

- Use skills: for specialist tasks, use Edge to find a fitting skill first.
- Run long jobs inside tmux so they survive disconnects.
- When done, say what you did, what you checked, and anything the owner must decide.
- Plain language; the owner is not an engineer.
