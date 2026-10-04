# Inside the claude.ai app (web, desktop, phone)

What works here: Layer A completely, and preparing everything for Layer B. What does not: training. Say it plainly:

> "I can't train a model inside this chat. I can set up Claude to write like you right now, and pack everything so that training on your computer is one step later."

## Flow

1. Consent line (SKILL.md section 1) before any example. Local-only mode is not available in the app: everything pasted here is read by Claude. If they want local-only, stop after the interview-only Layer A and point them to Claude Code.
2. Interview and Layer A (SKILL.md sections 2-3). Deliver `style-card.md` and `memory.md` as files they can download.
3. Show them how to keep Layer A: "Click Projects > New project, name it 'Writes like me', open 'Instructions' and paste the style card and memory. Start chats inside that project when you want drafts in your style."
4. Routing question: "Which computer do you use: a Mac, a Windows PC, or only a phone/tablet?" Mac: "Apple menu > About This Mac: what does it say next to Chip and Memory?"
   - Mac with an M chip and 16 GB+ memory, or a Windows/Linux PC: offer the training kit.
   - Phone/tablet only, Intel Mac, or under 16 GB: Layer A is the result. Say why ("your computer is too small to train a model; your Claude set-up already works").
5. Training kit (only if offered and wanted): collect examples as in SKILL.md section 4, write `examples.jsonl`, `style-card.md`, `memory.md`, `names.txt` and `state.json` (path, model choice, consent), zip them as `my-model-kit.zip` for download. The kit holds their writing: tell them to keep it private and delete it after training.
6. Handoff, exactly:
   > "Next step, on your Mac/PC: install Claude Code (claude.com/claude-code; it comes with paid Claude plans such as Pro and Max), open the Terminal, type `claude` and press Enter, then say: **continue my model from my-model-kit.zip in Downloads**. Claude will do the rest and tell you how long it takes."
   In Claude Code, the agent unzips the kit into `~/my-model/work/` and continues from SKILL.md section 4 (build) without repeating the interview.

The app's working files are temporary; `~/my-model/` only exists once the kit is opened in Claude Code.

## No skill support (skills switched off or blocked)

Give them `layer-a-prompt.md` to paste as their first message in a new chat.
