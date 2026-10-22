# Sensitivity rules

Written rules every reel passes before it is scheduled. They come from a creator who posts
daily street and founder-life footage and reviewed every escaped mistake. Run them on the
transcript, the captions, the hook, the post caption and the frames. `sensitivity_scan.py`
flags candidate lines in text; it is a pre-screen, not the judgment. The agent decides, and
anything on the "show the owner first" list goes to the owner before scheduling.

## Always cut

1. **Raise talk.** Investors, investor meetings, your round, terms, valuation. Talking about
   your own fundraise in public posts can count as general solicitation. Other people's public
   raises ("founders here raised $5M") are fine.
2. **Speculation that labels identifiable people.** Show what happened, never guess a crime
   about a real person ("they're hiding drugs in the trash").
3. **People in distress or vulnerable.** Street fights, drug use, unhoused people's faces.
   Choose not to film them; if they are in the shot, cut or reframe.
4. **Private data on screen.** Emails, phone numbers, keys and tokens, customer names,
   unannounced plans, notifications, addresses.
5. **Dated promises that are now false.** "Next week I'm interviewing 20 founders" filmed a
   month ago. Check every time word (tomorrow, next week, this Friday) against the post date.

## Cut by default (the owner can overrule)

- **Swearing**, unless it carries the joke.
- **Clearly identifiable people** need their consent. Keep a short list of people who have
  given standing consent; everyone else is asked or cut.

## Keep

- Strangers passing in public. The owner's own opinions and absolutes. Logos and implied
  signals. The owner's own struggles and failures.

## Show the owner before scheduling

- Private-looking settings (bedroom, home).
- Anything naming a real person negatively.
- Screen recordings with readable content (an inbox, a chat, a dashboard).

## Frame pass

Text rules miss what is only visible. Before scheduling, grab one frame per second
(`ffmpeg -i reel.mp4 -vf fps=1,scale=360:-2 frames/%03d.jpg`) and look at every one for: faces
of people without consent, screens with readable content, distress, private settings, and an
ending on glare or a blurred frame.
