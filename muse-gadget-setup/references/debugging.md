# Debugging checklist

Work top to bottom. Each row: symptom, likely cause, fix, source.

Repo docs: R = esp32/README.md, A = esp32/AGENTS.md, D = esp32/devices/README.md, L = linux/README.md, LA = linux/AGENTS.md, all under https://github.com/facebookincubator/muse-gadget-sdk/blob/main/

## 0. Before anything

- Is the user in the US with a Muse account? Muse rolled out in the US only (https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/). An HN commenter in Australia said they cannot get Muse there (https://news.ycombinator.com/item?id=49937504).
- Is their hardware in the official list (boards.md)? If not, it is a port; expect pin, touch and audio issues (issue #9).
- Pull the latest repo. Fixes land daily (PR #12 changed every board's reply path on launch night).

## 1. Build

| Symptom | Cause | Fix | Source |
|---|---|---|---|
| Missing headers like `gcm.h` or `gpio_ll.h` | Wrong ESP-IDF tag | Use ESP-IDF v6.0.1 exactly, re-run `export.sh` | A |
| `idf.py not found` | IDF not activated in this terminal | `. ~/esp/esp-idf-v6/export.sh`, or set `IDF_EXPORT` | R, A |
| Config edit has no effect | Generated `sdkconfig` in the build dir overrides defaults and overlays | Delete the build dir (or its `sdkconfig`) and rebuild | R, A |
| Build stops on stale TCP buffer sizes or cJSON nesting limit | Stale config caught by `cmake/validate_config.cmake` | Delete the build dir, rebuild | A |
| Component manager fails after switching boards (often lvgl) | Shared `managed_components/` and `dependencies.lock` | Delete both and build again; build one board at a time | A |
| Build warns about missing token | `CONFIG_GADGET_SDK_TOKEN` empty in this build dir | Set it via `idf.py -B <dir> menuconfig` | A |
| Host test `test_link_discovery` fails | No `managed_components/` yet | Run one `idf.py build` first | A |

## 2. Flash

| Symptom | Cause | Fix | Source |
|---|---|---|---|
| No serial port appears | Charge-only USB cable | Use a data cable | R |
| Port not accessible on Linux | Permissions | Add user to `dialout` (or `uucp`) | A |
| esptool cannot connect | Chip not in bootloader | Hold BOOT, tap RESET, release BOOT, retry | R |
| Agent cannot flash | Sandbox blocks serial port | Run flash and monitor outside the sandbox (`muse --disable-sandbox` for Muse Code) | R, A |
| `tools/muse/board.sh` fails picking a port | Several boards attached | Pass the USB serial (MAC) or port; `tools/muse/ports.py --list` | A |
| SenseCAP Watcher: `0107: Checksum error` or `0105: The format of the received message is invalid` | CH342 bridge drops bytes; plain esptool fails. Bootloader may already be erased (still recoverable, ROM loader answers) | Only `tools/muse/board.sh flash watcher` (paced, 115200). Lower baud or other port does not help. Wait about 3 min, never interrupt | A, D |
| StickS3: esptool cannot find it | UiFlow2 disables USB serial, no BOOT button | REPL `machine.mem32` sequence from D, replug, `--after no-reset` until Muse is on | D |
| StickC Plus2 flaky above 230400 baud | CH9102 bridge | Use 230400 (board.sh does) | D |
| Watcher: two usbmodem ports | CH342 dual port | S3 console is the one ending in `3` | A |
| Wrong board flashed | Profile guessed | Identify first: `chat.py --status`, USB descriptor, `esptool chip-id` | A |
| Board unusable after enabling Secure Boot or flash encryption | eFuses burned | Never enable `CONFIG_SECURE_BOOT`, flash encryption or `CONFIG_HOMEHUB_PAIRING_EFUSE_AUTH` on a board you want to reflash | A |
| Want factory firmware back | Overwritten | Restore the backups taken before flashing (Watcher `nvsfactory.bin`, `sticks3.bin`, `plus2.bin`) | D |

## 3. Boot

| Symptom | Fix | Source |
|---|---|---|
| Unsure if it booted | Healthy boot logs `link.main: Muse Gadget starting`; full-UI boards log `muse: board: <name>` | A |
| Agent has no TTY for `idf.py monitor` | Use the read-only capture snippet in A, or `tools/muse/monitor.py PORT [secs]` | A |
| Status LED colours wrong on DevKitC-1 (green shows as red) | LED takes green first; turn off `CONFIG_HOMEHUB_LED_RGB_ORDER` and rebuild | A |
| Red blinking LED | Error: read the serial log | R |

## 4. Pairing

| Symptom | Cause | Fix | Source |
|---|---|---|---|
| Device not listed in the app | Developer mode off | Settings > Devices > Developer mode, then Add Device | README.md |
| Still not listed (Linux) | Pairing window closed (10 min) | `sudo musegadget pair` | L |
| Still not listed (ESP32) | Not in setup mode | Short press reopens setup; 5 s hold resets setup | A |
| Stuck on blue breathing | Waiting for physical confirm | Press the button (BOOT on dev boards; on Voice PE flip the mute switch on first) | R, A |
| Linux: pairing gets to Wi-Fi, then "Couldn't connect" (Android) | BlueZ MTU missing | `[GATT] ExchangeMTU = 256` in `/etc/bluetooth/main.conf` (installer sets it); restart bluetooth | LA |
| GATT status 133 on phone | Stale phone Bluetooth state | Toggle phone Bluetooth | LA |
| Linux: pairing aborts randomly | A nearby unrelated BLE device's disconnect aborted the session (bug reported in PR #15, closed unmerged, status of fix UNVERIFIED) | Retry pairing away from other BLE devices; check upstream | PR #15 |
| Phone app cannot pair at all | App must support community pairing v5 | Update the Muse app; or try `tools/muse/ble_setup.html` in Chrome | A |
| Pairing fails after token revoked | Revoked tokens cannot pair | New token, set it, rebuild (ESP32) or `install.sh --sdk-token` (Linux) | R, L, sdk-tokens page |
| Port: touch-strip buttons never register, cannot confirm pairing (M5 Core2) | Unofficial port maps buttons as off-screen touches | Port issue, not SDK; see issue #9 | issue #9 |

## 5. Talking to Muse

| Symptom | Cause | Fix | Source |
|---|---|---|---|
| Every push-to-talk reply is "Sorry, I ran into a problem while responding. Please try again." / log `done (0 chars)`, `0.00s of audio` | Firmware built before PR #12 asked for voice replies from a voice model no longer served | Pull latest, rebuild and reflash. Replies now come as text captions | issue #6, PR #12 |
| Answers on screen but no speech | By design since PR #12 | Add your own TTS in `start_tts` | R |
| Reply text ends with `[usage] context_tokens=... cost=unavailable` | Server-side debug footer reported on launch night | Reported in issue #6 comments; current status UNVERIFIED | issue #6 |
| Voice PE: no reply on device | Voice PE replies show in the Muse app, not on the ring | Check the app | R |
| Answers too long for a small screen | Muse is verbose | Ask in the message: "Answer in one sentence." | R |
| Mic records silence on a port | GPIO conflict in the port (e.g. Core2 GPIO 0) | Port issue | issue #9 |
| Waveshare C6: no images, slower voice | No PSRAM: no tunnel, voice note goes over the control session, text replies | Expected; use an S3 board | D |

## 6. Linux runtime

| Check | Command | Source |
|---|---|---|
| Service running | `sudo systemctl status musegadget` | L |
| Live log | `sudo journalctl -u musegadget -f`; healthy shows `registered with the Muse` | L, LA |
| Identity and pairing | `musegadget info` | L |
| Muse cannot do X | Probably permissions of the run-as account; check `commands run as <user>` in log | L, LA |
| Large output truncated | Output capped at 96 KB per stream | LA |
| New command not visible to Muse | Service must restart and re-register | LA |
| A running command died | Reinstall restarts the service and kills it; check recent `invoke` lines first | LA |

## 7. Avatar tool exit codes

2 = no board or unsupported (use `--board s3` or `--board aipi`, or manual recipe for C6 and Watcher); 3 = not on Wi-Fi or not paired; 1 = Muse output still failing after two fix rounds, or build or flash failed (A).

## Where to ask

Discord linked from README.md (https://discord.gg/3bhjCkZdd6); GitHub issues on facebookincubator/muse-gadget-sdk.
