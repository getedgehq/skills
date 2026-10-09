# Tailscale, SSH keys, phone access and sharing

Read this for step 2. Tailscale gives every device you own a private address and a name, so the
laptop and phone can reach the box from anywhere without opening anything on the home router.

## 1. Install and name

1. Mac mini, laptop: download the Mac app from https://tailscale.com/download, open it, sign in.
   Phone: install "Tailscale" from the App Store or Play Store, sign in with the **same** account.
2. Admin console, Machines (https://login.tailscale.com/admin/machines):
   - rename the Mac mini to `agent-box` (menu, Edit machine name);
   - menu, **Disable key expiry**. Devices otherwise need a fresh login after about 180 days, and a
     box you cannot reach cannot be logged in remotely.
3. Admin console, DNS: **MagicDNS** on (default for new accounts). Now `agent-box` works as a name.
4. Tailscale Mac app settings on the box: "Launch at login" on. Optional: in the menu bar app,
   install the command line tool, so `tailscale status` works in Terminal.

Test from the laptop: `ping agent-box`. If the name does not resolve, use the full name shown in the
admin console (`agent-box.<your-tailnet>.ts.net`). Note: `nslookup` and `host` ignore MagicDNS on a
Mac; use `ping` to test.

## 2. Turn on Remote Login and Screen Sharing

On the box: System Settings, General, Sharing:

- **Remote Login** on. "Allow access for": only these users, add `owner` and `helper`.
- **Screen Sharing** on, same users.

First test from the laptop with the password: `ssh helper@agent-box`. Type `exit` to leave.

## 3. SSH keys instead of passwords

On the **laptop** (once):

```bash
ssh-keygen -t ed25519 -C "laptop"
ssh-copy-id helper@agent-box
ssh helper@agent-box
```

Pick a passphrase for the key when asked. On a Mac laptop, store the passphrase in its Keychain so you
do not retype it: `ssh-add --apple-use-keychain ~/.ssh/id_ed25519`.

Add a shortcut on the laptop so `ssh agent-box` is enough. Append to `~/.ssh/config`:

```
Host agent-box
  HostName agent-box
  User helper
```

The owner does the same for their own account: `ssh-copy-id owner@agent-box`.

### Phone

Use an SSH app: Termius (iPhone and Android) or Blink Shell (iPhone). In the app:

1. Generate a new key (type ED25519) inside the app. Copy its **public** key (one line starting with
   `ssh-ed25519`). A public key is safe to copy around; the private key never leaves the phone.
2. Add that line to the box. From the laptop:
   `ssh agent-box 'cat >> ~/.ssh/authorized_keys'`, paste the line, press Enter, then `Ctrl-d`.
3. In the app, add a host: address `agent-box`, user `helper`, the key from step 1.
4. With the Tailscale app on the phone connected, connect. Then attach to Claude (`claude-code-sessions.md`).

### Turn password login off

Only after key login works from the laptop **and** the phone. Keep one SSH session open the whole
time as your safety line.

```bash
sudo tee /etc/ssh/sshd_config.d/010-agentbox.conf >/dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
sudo sshd -t && echo "config OK"
sudo sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin)'
```

All three lines should say `no`. macOS starts a fresh SSH server for each new connection, so the
change applies to the next login without a restart. In a **second** window:

```bash
ssh agent-box                                       # must still work (key)
ssh -o PubkeyAuthentication=no helper@agent-box      # must be refused
```

If the first one fails, fix it from the safety session, or undo with
`sudo rm /etc/ssh/sshd_config.d/010-agentbox.conf`.

Folder permissions, if keys are ignored: `chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys`.

## 4. Tailscale SSH (alternative, for people comfortable with the terminal)

Tailscale SSH logs you in with your Tailscale identity, no SSH keys to manage. On a Mac it works only
with the open-source `tailscaled` variant, not the Mac app from the website or App Store. That
variant also starts at boot, before anyone logs in, which helps a box with FileVault on.

Switching means removing the Mac app and installing the other variant. **Do this only while sitting at
the box**, because the connection drops during the switch:

```bash
brew install tailscale
sudo brew services start tailscale
sudo tailscale up --ssh
```

Then sign in with the link it prints, rename the machine and disable key expiry again in the admin
console. Who may log in as which user is set in the `ssh` section of the tailnet policy file. Remote
Login plus keys (above) keeps working alongside it as a fallback.

## 5. Sharing the box with a teammate

Tailscale can share one machine with someone outside your account without giving them anything else.

1. Admin console, Machines, the box's menu, **Share**, copy the invite link, send it to them.
2. They accept with their own Tailscale account. Shared machines are reached by the full name
   (`agent-box.<your-tailnet>.ts.net`), not the short name.
3. They log in as `helper` with their **own** key: they send you their public key (one line starting
   with `ssh-ed25519`), you append it to `/Users/helper/.ssh/authorized_keys`. Never send them a
   password or a private key. Their agents then reach the box the same way.
4. Send them the etiquette in `safety-backups-updates.md` before they log in.

To end the access: remove the share in the admin console and delete their key line.

## 6. Never cut your own connection

When you are not at the box, do **not**:

- quit Tailscale, log out of it, run `tailscale down`, or switch Tailscale variants;
- change `tailscale up` flags or exit node settings on the box;
- turn off Remote Login or Screen Sharing, or turn on the macOS firewall's "Block all incoming";
- remove the last working SSH key or turn off passwords before keys work;
- restart with FileVault on unless you use `sudo fdesetup authrestart`.

If one of these is really needed, ask the owner to be at the box or reachable to fix it.
