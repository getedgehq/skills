# Adding behaviour and commands

Three layers, cheapest first:

1. **Prompt Muse** (no code). Linux: Muse already has a shell, so "Write a service that tells me when the Pi gets too hot" is a documented approach (linux/README.md). Display boards: Muse can send pictures (`display.draw_url`). Ask for shorter answers in the message itself ("Answer in one sentence.") (esp32/README.md).
2. **Give Muse a skill** (no code). For devices on the LAN via Home Link or a tunnel board, see home-link-and-skills.md.
3. **Add a command** (code). Muse discovers commands from what the device registers.

## Linux: add a command

Source: https://github.com/facebookincubator/muse-gadget-sdk/blob/main/linux/AGENTS.md ("Adding a command")

1. Add a spec to `COMMAND_SPECS` in `linux/src/musegadget/executor.py`: `description`, `required` and `optional` parameters (each with `type` and `description`), and `timeout_ms` if 30 s is too short.
2. Handle it in `Executor.run`. Return `ok(payload)` or `error(message)`.
3. Anything touching the machine runs in a child process with `self._child_options()`, so it runs as the chosen account, not root.
4. Add a test in `tests/test_executor.py`.
5. Deploy (`bash install.sh --from .` on the device). Muse sees the new command after the service restarts and re-registers.

Do not register with `device_family: "link"` or advertise `device.ota`: the server pushes ESP32 firmware updates to every `link` device (LA).

## Linux: push messages into Muse

```sh
musegadget send-user-msg "The garage door has been open for an hour."
musegadget send-user-msg --session-id 6f1c2d4e-0b7a-4c3e-9f5d-2a8b1e0c7d93 "Posted to a side chat"
```

Any program on the machine can do this with no credentials of its own. `--session-id` posts to a side chat; reuse the id to keep messages there. Full webhook example: `linux/examples/pebble_ring_bridge.py` (with `pebble-ring-bridge.service`) (linux/README.md). The reply appears in the Muse chat; the command only returns an ack (LA).

## ESP32: built-in commands

Registered in `esp32/main/noise_control.cpp` (read at commit b9008ab): `device.health`, `device.discover`, `display.draw_url` and `display.show_animation` (display boards), `voice.configure`, `sensors.read` (SenseCAP Indicator), `camera.capture` (Watcher, when enabled), `device.ota` (when OTA is on).

## ESP32: add a command or hardware

There is no step-by-step "add a command" recipe for ESP32 in the docs (as of b9008ab). What is documented:
- New board or peripheral: follow `esp32/devices/AGENTS.md` (gather chip, USB, buttons, display, audio, PMU facts from vendor sources; copy the closest overlay; set `CONFIG_IDF_TARGET`, `CONFIG_HOMEHUB_BUTTON_GPIO`, `CONFIG_HOMEHUB_LED_BACKEND_*`, flash size and mode; without PSRAM also `CONFIG_SPIRAM=n`, `CONFIG_HOMEHUB_TUNNEL=n` and mbedtls internal allocation). Classic ESP32 signed apps need chip revision 3.0+ (`CONFIG_ESP32_REV_MIN_3=y`).
- Read the vendor's own code before adding a board feature (IMU, camera, RTC, SD, power chip) (devices/AGENTS.md "Vendor sources").
- From reading the code (not a documented API): commands are declared with `add_command(...)` while building `link.register`, and dispatched on `link.invoke` in the same file. A new command needs both. Treat this as an inference and verify against the current source.
- Easiest path for a custom sensor: let a coding agent do it. The official README suggests prompts like "Add support for my board. It's an ESP32-S3 with 16 MB flash, a button on GPIO 0 and no PSRAM." (esp32/README.md).
- If the hardware can talk HTTP on the LAN, skip firmware work: put it behind a local HTTP API and let a tunnel board or Home Link reach it.

## Spoken replies (bring your own TTS)

Replies are text. On boards with PSRAM, `start_tts` in `esp32/components/muse/muse_chat_session.cpp` has the reply text, and the MP3 decoder, speaker and volume are already wired up: send the text to a TTS API of your choice and play the result (esp32/README.md, PR #12). Meta says a "robust voice pipeline for gadgets" is in progress, no date (issue #14 reply by a contributor: https://github.com/facebookincubator/muse-gadget-sdk/issues/14).

## Custom avatar

```sh
python3 tools/muse/avatar.py                    # draw their avatar
python3 tools/muse/avatar.py --edit "CHANGE"    # change the one they have
```

Run from `esp32/`, sandbox off, board plugged in and paired. Exit codes: 2 = no board or unsupported (C6 and Watcher need manual steps in `tools/muse/AVATAR_RECIPE.md`), 3 = not on Wi-Fi or not paired, 1 = generation, build or flash failed (previous avatar kept in `muse_pixel.c.prev`) (esp32/AGENTS.md).

## UI without a board

Desktop simulator in `esp32/simulator/` runs the production UI in a 412 x 412 SenseCAP Watcher window (esp32/README.md). Build per `esp32/simulator/README.md` (`brew install cmake ninja python`, then `cmake -S esp32/simulator -B esp32/simulator/build -G Ninja ...` and `cmake --build esp32/simulator/build --parallel`; read the README for the full flags).
