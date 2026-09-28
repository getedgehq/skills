# Plain-language setup walkthrough

Use whenever the user seems unsure, says they don't know where things are, gives an answer that doesn't parse, or asks what a word means. Use by default with anyone clearly not a developer.

The facts about what each host can read are in `setup.md` and are not repeated here. This file is only *how to say it*.

## Language rules

Ban these words from the conversation: config, root, directory, path, CLI, terminal, shell, launch, instance, runtime, machine, repo, environment variable, filesystem.

Say instead:

| Instead of | Say |
|---|---|
| config file | the settings file where your AI tools are listed |
| root / directory / path | folder |
| launch from X | start Claude while you're in the X folder |
| machine | this computer, or just "here" |
| repo / project | project folder, or the folder your work is in |
| the scan | me having a look at your setup |
| credential / token / API key | password or key |
| global | the settings that apply everywhere, not just one folder |

Never make someone feel behind for asking. The people whose agent setups are least governed are usually the ones least comfortable with this vocabulary — they are exactly who this assessment is for.

Say once, early, and mean it:

> If anything I say doesn't land, tell me and I'll say it a different way. There's no wrong question here.

## Establishing where they are

Ask one question at a time. Never stack three.

> First — where are you talking to me right now? Is this the Claude desktop app, or a window where you type commands?

Then, based on the answer:

**Claude desktop app / Cowork**

> Got it. In this app I can only look at folders you've specifically shared with me. Can you see a folder listed at the top of our chat, or somewhere in the sidebar?
>
> - **If yes:** that's the one folder I can see into. I can check what's in there, but not your computer's overall AI settings.
> - **If no folder is shared:** I can't look at anything yet. That's fine — we can do this as questions instead, and it still works.

If they want the fuller version, walk them through sharing their main user folder — the one with their name on it, containing Documents and Downloads — using whatever the app's folder-picker is called on their screen. Ask them to describe what they see rather than guessing at button names:

> Tell me what buttons or menus you can see around the chat box and I'll point you at the right one.

**A window where they type commands**

> That version can see more. The thing that matters is which folder you were in when you started it — I can look at that folder and anything inside it, plus your overall AI settings.
>
> If you want the fullest picture, close it, and start it again from your main user folder — the one with your name on it that contains Documents and Downloads. Then say hello again and we'll start from the top.

## When they're in the wrong place

Two situations, handled differently. Get this distinction right — it's the difference between a thirty-second fix and starting over.

**They just need to add a folder** (desktop app, folder not shared yet):

> No need to start over. Share the folder with me using the folder button in the app, and tell me when it's done — I'll pick up right where we left off.

Nothing is lost. Any answers already given still stand.

**They need to restart from a different folder** (command window, started somewhere too narrow):

> This one needs a restart, I'm afraid. Close that window, open it again from your main user folder, and start this assessment again. You'll lose the few answers we've done so far — sorry. It takes a minute and it's worth it, because otherwise I'd be reporting on one small corner and calling it your whole setup.

Then actually start from the welcome when they return. Do not resume half-way and assume the earlier answers still apply.

## The get-out

Always available, always offered without a hint of disappointment:

> We can also skip the looking-around entirely and just go through the questions. You'll still get a full score and a proper plan — I'll just be going on what you tell me rather than what I can see. Plenty of people prefer that, and for a whole-organisation view it's the only honest way anyway.

## Checking they actually followed

After any change, confirm what you can now see before continuing — and describe it in the same plain language:

> Right, I can now see your main folder and your overall AI settings. That means I can check which AI tools are connected and whether any passwords are sitting in plain text. What I still can't see is anyone else's computer, so anything about the wider company I'll have to ask you.

Never say a setup change worked without verifying it. A confident "great, all set" over a folder that is still unreadable produces a clean-looking result built on nothing.
