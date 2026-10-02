---
name: chatgpt-in-browser
description: Ask ChatGPT in the user's own logged-in browser when the user asks for a second opinion from ChatGPT, wants a plan challenged, or wants a debate until both agree.
---

# ChatGPT in browser

Get a second opinion and keep a multi-round plan review in one chat, with the complete answer saved locally. Use an attached browser tool that controls the user's own logged-in browser, such as a browser extension bridge, browser MCP connector, or browser debugging connection to that existing session. A fresh automation browser is not the user's session.

## Configuration

Choose a message file, an answer file for each round, and a final agreed-version file in the user's workspace. Confirm any model, reasoning effort, or plan requirement from the user's request; there is no required paid tier or fixed model. Preserve the existing chat's settings unless the user requested a change. Set a debate round cap before starting, default five rounds. Keep all work in the foreground.

## Procedure

1. Check that the browser tool is connected to the intended user session. List tab metadata only to locate an existing `chatgpt.com` tab. Select one eligible tab and retain its tab identifier. Do not open another tab, window, or tab group. Do not read, navigate, switch, close, or otherwise touch the user's other tabs. If no eligible tab exists, tell the user to open ChatGPT in the connected browser, then stop.
2. For round one, use a new conversation within that same tab so earlier conversations are not mixed into the review. For later rounds, navigate only that tab to the saved chat URL. Validate that the URL belongs to `https://chatgpt.com/` before navigating. Confirm the user is logged in and any requested model or effort is available through the current visible controls. Do not infer a plan from an upgrade banner, change accounts, buy a plan, or silently substitute a model.
3. Read the complete, nonempty message file locally. Paste its exact contents into the composer as one message, preserving line breaks. Verify the composer contains the whole message before sending once. Do not upload the file as an attachment, split it across messages, or submit a partial paste. If delivery is uncertain, inspect the selected conversation before retrying to avoid a duplicate.
4. Wait for the assistant reply to finish. Poll only this conversation every 30 seconds, up to 25 minutes per round. Use the current page's generation state and completed message controls; an unchanged text snapshot alone does not prove completion. On the cap, stop waiting and report the saved chat URL and that the reply is still incomplete. Do not send another question or claim success.
5. Copy the latest assistant reply verbatim using its message copy control or complete rendered text. Confirm the beginning and ending match the visible completed message and that no tool output limit omitted the middle. If the tool truncates text, retrieve bounded sections of that same reply and assemble them in order without omissions or duplication. Preserve wording and formatting supplied by the copy operation; do not summarize or reconstruct missing text.
6. Write the answer file with `Chat URL: <actual-chat-url>` on line one, followed by the complete copied reply. Read the file back to verify it matches the captured reply and contains the actual conversation URL. Keep chat URLs and answers local; do not include them in public artifacts. Report the file location to the user. Later rounds read and reuse that URL in the same selected tab.

## Debate loop

Round one sends the question, proposed plan, constraints, and all relevant context in one message file. Read the saved answer and write the next round's file with concrete agree/disagree statements for each point and an amended version of the plan. Ask ChatGPT for agree/disagree plus an amended rule per point and a complete amended plan with changed lines marked `[changed]`.

Repeat in the same conversation until neither side has an open disagreement. Save the complete agreed version to the chosen final file and tell the user what was agreed. Agreement is not permission to execute the plan: follow the user's original execution scope. If the round cap is reached or progress stalls, save the latest proposal, report unresolved points, and do not label it agreed.

## Failure handling

Stop at the failed step and tell the user the observed problem and what is needed to continue. Never guess an answer or silently fall back to another browser or account.

| Problem | Tell the user |
| --- | --- |
| Browser not connected | "The browser tool is not connected to your browser. Connect the browser bridge, then I can continue in your existing ChatGPT tab." |
| Logged out | "ChatGPT is logged out in the selected tab. Sign in there yourself, then I can continue." Do not request or enter credentials. |
| Wrong plan or unavailable requested model | "This session does not show the requested plan or model capability. Confirm the intended session or choose an available option before I send." State only what the UI confirms. |
| Required selector missing | "I cannot locate the required control in the current page. I have stopped at this step." Name the control and whether a message was already sent. Inspect current accessible controls before declaring it missing; do not guess selectors. |
| Reply truncated or interrupted | "I cannot verify a complete reply. The result is incomplete, so I have not marked it as a full answer." Keep any partial capture separately labeled, report the chat URL, and ask the user to resolve an interrupted response in that tab. |
| Plan limit or service error | "ChatGPT reports a limit or service error. I have stopped; we can resume this same chat when it is available." Do not bypass the limit or repeatedly resubmit. |

## Example

A user asks: "Have ChatGPT challenge our two-week rollout plan for a search feature and debate until you agree." Write `review-round-1.md` with the plan: staff-only testing on days 1 to 3, a 10 percent rollout on days 4 to 7, then full rollout on day 8; include the error budget, support capacity, rollback criteria, and the remaining week for monitoring. Send it in one existing ChatGPT tab and save `review-answer-1.md`. If ChatGPT flags weak rollback criteria, the next message agrees on that point, proposes a measurable threshold, and disagrees with an unnecessary extra testing week, explaining the existing coverage. Include the complete amended plan. Reuse the saved URL for each round and save `agreed-plan.md` only after both sides have no open disagreements.

## Limits and terms

This drives the user's own account in the user's own browser at human pace for the user's own questions. Plan limits still apply. It is not an API replacement and must not be used for bulk or automated workloads. The user is responsible for the service's terms.

This skill has no measured effect yet. Static checks do not verify live browser compatibility or answer quality.
