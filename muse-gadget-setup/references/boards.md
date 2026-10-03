# Boards

Source for every row unless noted: https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/devices/README.md and https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/README.md (commit b9008ab, 2026-10-02). "Battery" means the firmware reports battery status, per the official feature table.

## Official ESP32 boards

| Board | Chip | Display | Push-to-talk / audio | Buttons | Battery | Images from Muse | Tunnel (LAN access) | Build |
|---|---|---|---|---|---|---|---|---|
| ESP32-C5 DevKitC-1 (default, quickest start) | ESP32-C5, 8 MB / 8 MB PSRAM | None, RGB status light | No | BOOT | No | No | Yes | `idf.py build` |
| ideaspark ESP32 with 1.9" display | ESP32, 16 MB / no PSRAM | 1.9" 170x320 LCD, status screen | No | BOOT | No | Yes | No | `tools/board.sh ideaspark build` |
| Seeed SenseCAP Indicator | ESP32-S3, 8 MB / 8 MB | 4" 480x480 LCD, status screen | No | Top | No | Yes | Yes | `tools/board.sh sensecap-indicator build` |
| Seeed reTerminal E1001 | ESP32-S3, 32 MB / 8 MB | 7.5" 800x480 black and white e-paper | No | Green | No | Black and white | Yes | `tools/board.sh reterminal-e1001 build` |
| Home Assistant Voice Preview Edition | ESP32-S3, 16 MB / 8 MB | None, 12-LED ring | Yes, speaker and mic (replies show in the Muse app) | Centre (talk), dial (volume) | No | No | Yes | `tools/board.sh home-assistant-voice build` |
| Waveshare ESP32-S3-Touch-AMOLED-1.75C | ESP32-S3, 32 MB / 8 MB | 1.75" 466x466 round AMOLED, touch, full UI | Yes, speaker and mic | PWR (talk), BOOT | Yes | Yes | Yes | `tools/muse/board.sh build s3` |
| Waveshare ESP32-S3-Touch-AMOLED-1.75 | ESP32-S3, 16 MB / 8 MB | 1.75" 466x466 round AMOLED, touch, full UI | Yes, speaker and mic | BOOT (talk), PWR | Yes | Yes | Yes | `tools/muse/board.sh build s3n` |
| AIPI Lite | ESP32-S3, 16 MB / 8 MB | 128x128 LCD, full UI | Yes, speaker and mic | Two | Yes | Yes | Yes | `tools/muse/board.sh build aipi` |
| Waveshare ESP32-C6-Touch-AMOLED-1.8 | ESP32-C6, 16 MB / no PSRAM | 1.8" 368x448 AMOLED, touch, full UI | Text replies only, voice note goes over control session | BOOT (talk), PWR | Yes | No | No | `tools/muse/board.sh build c6` |
| Seeed SenseCAP Watcher | ESP32-S3, 32 MB / 8 MB | 1.45" 412x412 round LCD, touch, full UI | Yes, speaker and mic | Wheel (press to talk, turn to sleep) | Yes | Yes | Yes | `tools/muse/board.sh build watcher` (flash only via paced tool, see setup-esp32.md) |
| M5Stack StickS3 | ESP32-S3, 8 MB / 8 MB | 1.14" 135x240 LCD, full UI | Yes, speaker and mic | Front (talk), side (menu), PWR | Yes | Yes | Yes | `tools/muse/board.sh build sticks3` |
| M5Stack StickC Plus2 (end of life) | ESP32, 8 MB / 2 MB | 1.14" 135x240 LCD, full UI | Yes, buzzer and mic (quiet) | Front (talk), side (menu), PWR | Voltage only | Yes | Yes | `tools/muse/board.sh build plus2` |

Extra capabilities:
- **Air sensors**: SenseCAP Indicator D1S and D1Pro only (CO2, tVOC built in; temperature and humidity from the Grove AHT20 in the box, plug it in). Read with `sensors.read`. Needs Seeed's stock RP2040 firmware.
- **Camera**: SenseCAP Watcher only, off by default. Enable `CONFIG_MUSE_WATCHER_CAMERA=y` (menuconfig > Muse > "SenseCAP Watcher camera capture and live preview") and rebuild. `camera.capture` returns a base64 JPEG. Photo attachments to voice messages are not included.
- **Touch**: Waveshare S3 1.75C, S3 1.75, C6 1.8, SenseCAP Watcher.
- **OTA updates**: on for full-UI boards, off for the others.
- Not used yet on the M5 sticks: IMU, IR, Grove (and RTC on the Plus2).

Buy links and vendor docs for every board are in the "Supported devices" table of esp32/devices/README.md.

## Featured builds on gadgets.muse.ai vs repo support

Source: https://gadgets.muse.ai/ (fetched 2026-10-03)

| Featured project | Repo status |
|---|---|
| Raspberry Pi 5 (Home Assistant and Linux apps) | Supported via Linux SDK |
| Waveshare ESP32-S3-Touch-AMOLED-1.75C (round, battery) | Supported |
| Muse on your TV (HDMI stick) | "Coming soon", no code |
| Seeed reTerminal E1002 (color e-ink) | **Not supported.** Only the black and white E1001 is in the repo. Issue #13: building E1001 config for an E1002 flashes the monochrome UC8179 driver onto the color Spectra 6 panel, "which won't drive it". https://github.com/facebookincubator/muse-gadget-sdk/issues/13 |
| M5Stack StickS3 | Supported |
| AiPi Lite ("Muse answers out loud") | Supported, but replies are now text captions; spoken answers need your own TTS (PR #12) |
| ideaspark ESP32 1.9" | Supported |
| Home Assistant Voice Preview Edition | Supported |

## Linux

Source: https://github.com/facebookincubator/muse-gadget-sdk/blob/main/linux/README.md

- Raspberry Pi 3B+, 4, 5 or Zero 2 W, or any Linux computer with **Bluetooth LE**.
- Raspberry Pi OS Bullseye or later, Debian 11 or later, Ubuntu 22.04 or later. 32-bit and 64-bit.
- An account with sudo (for the install).
- No display, audio or button support in the SDK; it is a command runner. Add your own hardware via commands (see extend.md).

## Muse Home Link (not a dev board)

Source: https://gadgets.muse.ai/home-link. ESP32-C5, 8 MB PSRAM, 8 MB flash, Wi-Fi 6 (2.4 and 5 GHz), USB-C and USB-A, status LED, 35 x 42 x 10 mm. Runs official firmware only, cannot be reflashed.

## Community ports (UNVERIFIED, not in the official repo)

Seen on GitHub on 2026-10-03; not reviewed or tested. Treat as starting points only.

- M5Stack StopWatch: https://github.com/GOROman/muse-stopwatch
- M5Stack StackChan (CoreS3): https://github.com/Tjtelenda/musechan
- SMKTelec ESP32-S3 1.54" (Waveshare clone): https://github.com/ousiaresearch/smktec-154-muse-port
- Rabbit r1 on LineageOS (Android app, not ESP32): https://github.com/cameronapak/muse-r1
- Sonarr, Radarr, Jellyfin commands on a Pi: https://github.com/vocino/muse-arr
- Open PRs: ESP32-S3-BOX-3 (#16), M5Stack Cardputer ADV (#10)
- Reported broken: M5Stack Core2 port, touch buttons and mic dead (issue #9)
- Local ports mentioned in issue #6: Waveshare ESP32-S3-Touch-AMOLED-1.8 and 2.16
- Meta-free fork with a self-hosted server for any OpenAI-compatible model: https://github.com/mfiumara/mute-gadget-sdk (does not talk to Muse at all)
