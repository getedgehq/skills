# Framing and pacing

## The frame

- **One window**, about 85% of the screen width, centred, wallpaper visible on every side. The
  wallpaper is what tells a viewer this is a real Mac; do not crop it away in the edit.
- A calm wallpaper with no text. Desktop icons hidden.
- Every other app hidden (`set visible of process "<App>" to false` in System Events works from
  `gui.sh` without Accessibility). Notifications off for the take (Focus mode).
- Close popups, update prompts, usage banners and cookie bars before pressing Record.
- Collapse sidebars that show private chat titles, account names or other customers' data.
- The app's language matches the audience. Change it per app, not system-wide, on a shared Mac.
- Fresh state where the demo is about first use: new chat, empty field, logged-in account with
  nothing personal visible.

## Pacing

- One action every 2 to 4 seconds; a viewer needs about a second to see where the cursor went.
- Move the cursor to a target before clicking it (`/move`, short pause, `/click`), so the eye can
  follow.
- Type at human speed: `/type` already spaces characters 20 ms apart; for a hero line, send it in
  chunks of a few words.
- Scroll in page steps with pauses, never a fling.
- Let results sit for 3 seconds before the next action. Long waits (an AI generating) are fine to
  record in full; speed them up in the edit and say so on screen.

## The action log is your caption track

`/act` writes `seconds<TAB>label` from the moment you call `/log`. Start the log right after the
Record click and the times line up with the video to within about a second. Write labels as the
caption a viewer should read ("Copy the setup link", "Edge picks the pitch-deck skill"), not as
code, and the edit needs no second pass.
