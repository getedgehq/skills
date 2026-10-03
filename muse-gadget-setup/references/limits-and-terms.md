# Limits and terms

## Region and accounts

- Muse "is rolling out in the US on iOS, Android, and muse.ai" (https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/). Muse subscriptions "aren't available in all locations yet"; you must be located where Muse is available and 18+ (https://www.meta.com/help/subscriptions/1021145227643680/).
- Plans: free with a usage limit; Power $20/month (500M Muse tokens per week); Maximum $100/month (3B per week) (same help page).
- Building an SDK gadget needs a Muse account and an SDK token. Whether a paid subscription is required for SDK gadgets: not stated anywhere checked (UNVERIFIED). Home Link explicitly needs an active subscription.

## Home Link

- US only, active subscription, one per subscriber, 5,000 made, ships in October, first come first served (https://gadgets.muse.ai/home-link, https://x.com/natfriedman/status/2106099384891158562).
- Cannot be reflashed (home-link page). Device Terms forbid modifying firmware except as permitted by law, and the device stops working if the subscription ends (https://muse.ai/deviceterms sections 6(c), 10.3).
- Meta may push firmware updates automatically and may remotely deactivate it (Device Terms 7, 9.3).
- Residential use only, on a network you are authorized to control (Device Terms 1).
- Local network discovery data (device names, types, identifiers, addresses, states) goes to Meta's cloud (Device Terms 4, 5).

## SDK token terms (https://gadgets.muse.ai/sdk-terms)

- Personal, non-commercial use with your own Muse account.
- Embed a token in at most 50 devices you make available to others; a token links to at most 50 devices total.
- No embedding in devices you sell, advertise, list publicly or in a marketplace, or use in promotions. Do not imply Meta made or endorses it.
- Others' devices must not access another person's Muse account; if you give a device to someone, tell them what it does with their data before they pair.
- Do not circumvent restrictions or "enable functionality that Meta has disabled".
- "Not a supported product and not a developer platform. They may change, stop working, or be withdrawn at any time."
- Meta can revoke; then remove the token from devices you gave away.
- The Apache 2.0 code license grants no right to tokens.

## Technical limits (repo docs)

- Replies to gadgets are text only (voice in, text out). Spoken output needs a third-party TTS (esp32/README.md, PR #12).
- No home-network tunnel on boards without PSRAM (ideaspark, Waveshare C6, classic ESP32) (esp32/README.md).
- Waveshare C6 cannot show images and cannot hold its own voice session (esp32/devices/README.md).
- reTerminal E1001 is black and white only, refresh takes 1 to 2 s; the color E1002 featured on the site is not supported (issue #13).
- Full-UI builds need 16 MB flash, except StickS3 and StickC Plus2 (8 MB layout) (esp32/devices/README.md).
- ESP-IDF v6.0.1 only; build docs cover macOS and Linux (esp32/README.md).
- Linux needs Bluetooth LE for pairing (linux/README.md).
- Linux message size: 256 KB per message to the VM, command output cut at 96 KB (linux/AGENTS.md).
- Streaming dictation input has no ASR backend per issue #14 (author's reading of the firmware; UNVERIFIED by Meta).
- HDMI "Muse on your TV" stick: coming soon, no code (https://gadgets.muse.ai/).

## Security

- Linux: Muse has the run-as account's permissions, sudo included (linux/README.md). Use `--run-as` a non-sudo account where possible.
- Community pairing has no manufacturer verification and "can't prevent an active man-in-the-middle attack". Pair on a trusted network (README.md, esp32/README.md, linux/README.md).
- The SDK token is inside the firmware: treat it as an identifier; revoke and rebuild if it leaks (esp32/README.md).
- Without NVS encryption, anyone with physical access can read Wi-Fi credentials and device tokens from flash; enable `CONFIG_HOMEHUB_NVS_ENCRYPTION` (esp32/README.md).
- Builds use the included development signing key and never enable Secure Boot (esp32/README.md).
- Community skills and gadgets are not for safety-critical use (home-link page).

## Not possible (as of 2026-10-03)

- Reflashing Home Link.
- Native spoken replies from Muse on a gadget.
- Color e-ink (E1002) with the official repo.
- Selling gadgets with your token embedded.
- Using Muse gadgets outside a Muse-available country without a Muse account (the Meta-free fork https://github.com/mfiumara/mute-gadget-sdk replaces Muse with your own server and model; it is not Muse).
