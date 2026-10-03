# Linux / Raspberry Pi setup

Sources:
- L = https://github.com/facebookincubator/muse-gadget-sdk/blob/main/linux/README.md
- LA = https://github.com/facebookincubator/muse-gadget-sdk/blob/main/linux/AGENTS.md

## What you need (L)

- Raspberry Pi 3B+, 4, 5 or Zero 2 W, or any Linux computer **with Bluetooth LE** (pairing runs over BLE).
- Raspberry Pi OS Bullseye or later, Debian 11+, or Ubuntu 22.04+, already online. 32-bit or 64-bit.
- An account with sudo.
- SDK token `mgst_...` from https://gadgets.muse.ai/settings/sdk-tokens.
- Muse app on the phone.

## Decide the account first

Muse runs commands "as the account you installed for, with exactly that account's permissions. If it can use sudo, so can Muse" (L). For anything beyond a throwaway Pi, create a non-sudo user and install with `--run-as` (below). Installing Home Assistant through Muse needs sudo, so that is a trade-off the user must choose.

## Install (L)

On the machine, as the account Muse should use:

```sh
curl -fsSL https://raw.githubusercontent.com/facebookincubator/muse-gadget-sdk/main/linux/install.sh -o install.sh
less install.sh     # read it first
bash install.sh --sdk-token mgst_…
```

Installs into `/opt/musegadget`, starts the `musegadget` systemd service, asks before giving Muse your account, tells you if it can sudo, then opens Bluetooth pairing. It also sets `[GATT] ExchangeMTU = 256` in `/etc/bluetooth/main.conf` (LA).

Flags (LA): `--run-as USER`, `--no-pair`, `--yes`, `--from SOURCE`, `--uninstall`, `--purge`, `--sdk-token`.

## Pair (L)

When the installer says pairing is open (open for 10 minutes):

1. Muse app: Settings > Devices > Developer mode on.
2. Settings > Devices > Add Device (+, top right). Pick `MuseGadgetXXXXXX` (no hyphen), the name the installer printed.
3. Accept the community device warning.
4. When asked for Wi-Fi, pick the network shown. No password needed; the machine is already online.

Pair again later: `sudo musegadget pair`.

## Manage (L)

```sh
musegadget info                          # name, node id and pairing state
sudo systemctl status musegadget         # is it running?
sudo journalctl -u musegadget -f         # follow the log
sudo musegadget pair                     # pair again
bash install.sh --uninstall              # remove it (add --purge to forget the pairing)
bash install.sh --run-as someone         # give Muse a different account
bash install.sh --sdk-token mgst_…       # replace the token (stored in /var/lib/musegadget/sdk_token, root only)
```

Verbose pairing: `sudo musegadget -v pair` (LA).

Healthy start in the log: `commands run as <user>`, `Noise session established`, `sent link.register`, `registered with the Muse` (LA).

## What Muse can do out of the box (L)

| Command | Does |
|---|---|
| `system.run` | Runs a shell command, returns output and exit code |
| `file.read` | Reads a file, 64 KB at a time |
| `file.write` | Writes a file, 64 KB at a time, replaces only when complete |
| `device.health` | Uptime, load, memory, disk, temperature |

Example prompts from the README: "What's using all the disk space on my Pi?", "Install Home Assistant on my Pi and tell me how to open it.", "Every morning at 7, check if my Pi's backups ran and tell me if they didn't."

Command output is cut at 96 KB per stream; the Muse VM accepts at most 256 KB per message from the device (LA).

## Develop and deploy changes (L, LA)

```sh
uv run --with pytest --with . pytest      # tests, no Bluetooth needed
bash install.sh --from .                  # on the device, from a copied checkout
```

Faster loop: `uv build --wheel`, then on the device `sudo /opt/musegadget/venv/bin/pip install --no-deps --force-reinstall musegadget-*.whl` and `sudo systemctl restart musegadget` (LA). Reinstalling restarts the service and kills any running command.
