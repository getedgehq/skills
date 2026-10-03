# ESP32 setup

All commands are copied from the official docs. Sources:
- R = https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/README.md
- A = https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/AGENTS.md
- D = https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/devices/README.md

## What you need (R)

- A supported ESP32 board (see boards.md). Quickest start: ESP32-C5 DevKitC-1.
- A USB cable that carries data, not just power.
- A computer running macOS or Linux (Windows is not covered by the docs).
- An SDK token (`mgst_...`) from https://gadgets.muse.ai/settings/sdk-tokens.
- The Muse app on your phone.

## Option 1: let a coding agent do it (R)

Muse Code:

```sh
curl -fsSL https://dev.meta.ai/install.sh | sh
git clone https://github.com/facebookincubator/muse-gadget-sdk
cd muse-gadget-sdk/esp32
muse --disable-sandbox
```

Then ask: "Build this firmware for my ESP32-C5 DevKitC-1 and flash it." Any agent that reads `AGENTS.md` works; flash and monitor commands must run outside a sandbox (serial port access).

## Option 2: by hand

### 1. Install ESP-IDF v6.0.1 exactly (R)

Other versions are unsupported. Errors about missing IDF headers such as `gcm.h` or `gpio_ll.h` usually mean the wrong IDF tag (A).

macOS prerequisites: `brew install cmake ninja dfu-util python3`. Linux: Espressif's prerequisites page (https://docs.espressif.com/projects/esp-idf/en/v6.0.1/esp32c5/get-started/linux-macos-setup.html).

```sh
git clone -b v6.0.1 --recursive https://github.com/espressif/esp-idf.git ~/esp/esp-idf-v6
~/esp/esp-idf-v6/install.sh esp32c5,esp32s3,esp32c6,esp32
. ~/esp/esp-idf-v6/export.sh
```

Run the `export.sh` line in every new terminal. The `tools/muse/board.sh` helper looks for ESP-IDF in `~/.espressif/esp-idf-v6.0.1`, `$IDF_PATH`, `~/esp/esp-idf-v6.0.1`, `~/esp/esp-idf-v6`, `~/esp/esp-idf`; elsewhere, set `IDF_EXPORT=/path/to/esp-idf/export.sh` (A).

### 2. Set the SDK token (R, A)

The token lives in Kconfig as `CONFIG_GADGET_SDK_TOKEN` (menu "ESP32 Device SDK" > "Muse Gadgets SDK token"). Each build directory has its own `sdkconfig`, so set it for the build directory you use:

```sh
idf.py menuconfig            # default DevKitC-1 build, config in build/sdkconfig
idf.py -B <build-dir> menuconfig   # per-board build dirs (A: "Edit per-build settings")
```

Or set `CONFIG_GADGET_SDK_TOKEN="mgst_..."` in that build directory's `sdkconfig` (A). Without it the build warns and the gadget "will stop pairing once Muse requires tokens" (A). The token ships inside the firmware: treat it as an identifier; if it leaks, revoke it at gadgets.muse.ai, make a new one, rebuild (R).

Optional for fast iteration: set `CONFIG_HOMEHUB_WIFI_SSID` and `CONFIG_HOMEHUB_WIFI_PASSWORD` in menuconfig to skip BLE Wi-Fi provisioning; it still needs pairing once (A).

Recommended: enable NVS encryption, `CONFIG_HOMEHUB_NVS_ENCRYPTION` (R).

### 3. Build

| Board | Command (run from `esp32/`) |
|---|---|
| ESP32-C5 DevKitC-1 | `idf.py build` (output `build/muse-gadget.bin`) |
| ideaspark, SenseCAP Indicator, reTerminal E1001, HA Voice PE | `tools/board.sh <ideaspark\|sensecap-indicator\|reterminal-e1001\|home-assistant-voice> build` (build dir `build-<board>/`) |
| Full-UI boards | `tools/muse/board.sh build <s3\|s3n\|aipi\|c6\|watcher\|sticks3\|plus2>` (build dir `build-muse-<profile>/`, log `/tmp/muse_build_<board>.log`) |

Note the argument order differs: `tools/board.sh BOARD ACTION [PORT]` vs `tools/muse/board.sh ACTION BOARD [SERIAL|PORT]` (A).

Equivalent raw `idf.py` for a full-UI board (D), example AIPI Lite:

```sh
idf.py -B build-muse-aipi -DIDF_TARGET=esp32s3 \
  -DSDKCONFIG=build-muse-aipi/sdkconfig \
  -DSDKCONFIG_DEFAULTS="sdkconfig.defaults;devices/sdkconfig.muse;devices/sdkconfig.muse-aipi" build
```

Profile names: s3 = waveshare-s3-175c, s3n = waveshare-s3-175, aipi, c6 = waveshare-c6-18, watcher = sensecap-watcher, sticks3 = m5stack-sticks3, plus2 = m5stack-stickc-plus2 (tools/muse/board.sh).

### 4. Identify the board and port before flashing (A)

- Already running Muse firmware: `python3 tools/muse/chat.py --status`.
- USB descriptor: `ioreg -p IOUSB -l -w 0` (macOS), `lsusb -v` or `udevadm info /dev/ttyACM0` (Linux). Espressif `303a:1001` = chip's own USB (C5, C6, S3 boards). CH340 `1a86:7523` = ideaspark, SenseCAP Indicator, reTerminal E1001. CH9102 = StickC Plus2. CH342 with two usbmodem ports = SenseCAP Watcher (S3 console is the port ending in `3`).
- Chip: `python -m esptool -p PORT chip-id`.
- Ports: macOS `ls /dev/cu.usb*`; Linux `/dev/ttyACM*` or `/dev/ttyUSB*`. On Linux add yourself to `dialout` (or `uucp`).
- Full-UI boards: `tools/muse/ports.py --list`.

### 5. Back up vendor firmware first where needed (D)

- **SenseCAP Watcher**: back up the per-device `nvsfactory` partition:
  `tools/muse/paced_esptool.py --chip esp32s3 -p PORT read-flash 0x9000 0x32000 nvsfactory.bin`
- **M5Stack StickS3** (ships with UiFlow2, USB serial disabled, no BOOT button): put UiFlow2 in USB mode, open its REPL (e.g. `mpremote repl`), paste the four `machine.mem32` lines from D, unplug and replug, then
  `python -m esptool --chip esp32s3 -p PORT --after no-reset read-flash 0 0x800000 sticks3.bin`
  then `tools/muse/board.sh flash sticks3 PORT`. Pass `--after no-reset` to esptool until Muse is on.
- **M5Stack StickC Plus2**: `python -m esptool --chip esp32 -p PORT -b 230400 read-flash 0 0x800000 plus2.bin`
- **HA Voice PE**: flashing replaces the S3 firmware only; never reflash the XMOS audio chip (A).

### 6. Flash and monitor

```sh
idf.py -p /dev/cu.usbmodem1101 flash monitor      # DevKitC-1 (R); replace the port
tools/board.sh ideaspark flash-monitor /dev/cu.usbserial-110   # helper boards (A)
tools/muse/board.sh flash <board> [SERIAL|PORT]     # full-UI boards (A)
```

For full-UI boards, monitor with `idf.py -B <same dir> ... -p PORT monitor` or `tools/muse/monitor.py PORT [secs]` (resets the board, needs pyserial). `Ctrl-]` quits the IDF monitor. A healthy boot logs `link.main: Muse Gadget starting` (A).

SenseCAP Watcher: never `idf.py flash`. Use `tools/muse/board.sh flash watcher` (paced, 115200 baud). It prints nothing for about three minutes. Do not interrupt it (A).

If flashing cannot connect: hold BOOT, tap RESET, release BOOT, retry (R).

Reflashing keeps pairing and Wi-Fi. To start fresh: `idf.py -p PORT erase-flash` (R).

### 7. Pair (R)

1. Status light breathes **orange**: ready for setup.
2. Muse app: Settings > Devices > Developer mode on.
3. Settings > Devices > Add Device (+, top right). Pick `MuseGadget-XXXXXX` (`MuseGadget-Disp-XXXXXX` on ideaspark, SenseCAP Indicator, reTerminal E1001; `MuseGadget-ha-voice-XXXXXX` on Voice PE) (A). Full-UI boards show the name on screen until paired (AIPI Lite's 128 px screen leaves it out) (A).
4. Choose Wi-Fi in the app.
5. Light breathes **blue**: press the button (BOOT on dev boards) to confirm.
6. **Green** = connected.

| Light | Meaning |
|---|---|
| Orange, breathing | Ready for setup |
| Blue, breathing | Press the button to confirm pairing |
| Blue | Joining Wi-Fi and connecting to Muse |
| Green | Connected |
| Yellow, blinking | Reconnecting |
| Purple | Not paired |
| Red, blinking | Error, check the log |

Hold the button 5 s to reset setup (unpair and forget Wi-Fi). Short press reopens the setup window if setup is not complete (A). On the HA Voice PE, turn the mute switch on to get the setup role of the centre button back (A).

Alternative pairing without the phone app: `tools/muse/ble_setup.html` uses Web Bluetooth; serve it over https or localhost and open in Chrome (desktop or Android). iOS Safari lacks Web Bluetooth (file header).

### 8. Verify

- `python3 tools/muse/chat.py --status` shows the board.
- `python3 tools/muse/chat.py "question"` asks your Muse through the board (A).
- Host tests: `python3 -m unittest discover -s tests -p 'test_*.py'` (after one `idf.py build`) (R).
