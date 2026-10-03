# Muse Home Link and community device skills

## Home Link

Source: https://gadgets.muse.ai/home-link (fetched 2026-10-03)

- What it is: a USB-C gadget on the ESP32-C5 chip that keeps Muse connected to your home Wi-Fi so it can reach compatible devices you own, or anything with a local HTTP API.
- Firmware is based on the open source ESP32 Device SDK, but Home Link "only runs official firmware and can't be reflashed".
- Availability: "Free with an active Muse subscription in the United States only, limit one per subscriber. Ships in October, first come, first served." Meta made 5,000 (Nat Friedman, https://x.com/natfriedman/status/2106099384891158562). Claiming holds a place in line, it is not an order (per https://cellcog.ai/blog/muse-gadgets/, quoting the claim page; the claim page itself was not fetched).
- Device Terms (https://muse.ai/deviceterms) section 10.3: if the subscription ends, the device's capabilities are unavailable until it is restored. Section 6(c): no tampering, reverse engineering or modifying hardware or firmware except as permitted by law. Section 3: when Muse browses via the device, sites see your home IP.

### Setup (official, 4 steps)

1. Plug into any USB-C or USB-A power source near the router.
2. Add the device in the Muse app. Setup runs over Bluetooth LE; choose the Wi-Fi network.
3. Ask Muse. Home Link stays on the network so Muse can reach your devices.
4. Add community skills.

No SDK token or Developer mode is mentioned for Home Link on its page. Whether Home Link needs Developer mode is UNVERIFIED.

Hardware: ESP32-C5 at 240 MHz, 8 MB PSRAM, 8 MB flash, Wi-Fi 6 2.4 and 5 GHz, USB-C and USB-A, status LED, 35 x 42 x 10 mm.

### No Home Link? Build the equivalent

Home Link uses the same chip as the ESP32-C5 DevKitC-1, which runs the SDK with the home-network tunnel (https://github.com/facebookincubator/muse-gadget-sdk/blob/main/esp32/devices/README.md). Every PSRAM board in boards.md with "Tunnel: Yes" lets Muse "reach the devices you already own and anything you build with a local HTTP API" (esp32/README.md). This still needs a Muse account (US) and an SDK token, but not a subscription as far as the docs say (UNVERIFIED whether the free Muse tier is enough). That the community skills behave the same through a DIY tunnel board as through Home Link is an inference from the shared firmware, not a documented claim.

## Community device skills

Source: https://github.com/facebookincubator/muse-gadget-sdk/tree/main/skills (README.md and CATALOG.md)

- 43 Markdown-only skills (42 device or family skills plus a shared Google Cast skill). "Community-sourced ... not official integrations."
- How to install, two documented ways:
  1. "give your muse a link to this GitHub repo in its chat and let it find the skills it needs", or
  2. find the device in `skills/CATALOG.md`, copy its `SKILL.md` into the Muse chat, plus any shared skill it references (e.g. Google Cast).
- Categories: lights and plugs (Hue, Lutron, Shelly Gen 4, Elgato Key Light, Meross, Kasa EP10 and EP25), speakers and TVs (Google Cast family, HomePod mini, Apple TV 4K, Sonos, LG webOS, Samsung Tizen, VIZIO, Google TV Streamer, Freebox, Squeezebox), printers and appliances (Brother, HP M254dw, Epson, Dyson HP04, Miele G 7566, Moonraker 3D printers), vacuums (Roomba and Braava, Roborock, eufy Tuya models), gateways (ratgdo v32, Zigbee2MQTT, ESPSomfy-RTS, Sonoff RF Bridge R2, VELUX KLF200, ESPHome, Tuya), read-only (UniFi Network, Wyze RTSP, yi-hack cameras).
- Skills are local-protocol recipes. Many need something the user must supply: Hue needs the physical bridge-button press for a key, Meross needs supplied keys, Tuya needs local keys and a datapoint map, Wyze and yi-hack need specific firmware already installed. Read the device's skill before promising it works.
- Not for safety-critical use: "don't rely on them for anything safety-critical like home security, emergencies, or medical needs" (home-link page).
- Write your own: `skills/gadget-<device-name>/SKILL.md` with matching YAML `name`, a `description`, instructions, limits and source links. Markdown only (skills/README.md).
