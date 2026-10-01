---
name: buffer-api-scheduling
description: Schedule, inspect, and edit social posts through Buffer GraphQL while preserving media, thread structure, and publishing state.
---

# Buffer API scheduling

Use this when an agent has an authorized Buffer connection and must create, reschedule, or inspect posts. Read the current channel list first. Require an exact channel ID when several channels share a service. Treat an accepted API mutation as a pending result until a read back confirms it.

## Configuration

Supply the Buffer bearer token through a secret manager or process environment. Set your own approval policy, daily cadence, timezone, and media URL host. If another scheduler controls the same channel, include its queue in any collision check; an unavailable queue is an unknown state, not an empty one. Keep these choices outside this skill.

## API procedure

1. Use Buffer's current GraphQL API with the bearer token. The legacy REST API rejects current OIDC tokens. Read the organization ID from `account.organizations[0].id`, then query root `channels(input:{organizationId})`; nested organization channels may return `FORBIDDEN`.
2. Before scheduling, resolve the exact channel, inspect scheduled posts and drafts, and validate the desired slot against the configured cadence. A queue read error must stop the schedule. Keep pagination at or below 100 items per page; a request above 100 may produce `PAGINATION_LIMIT_EXCEEDED`.
3. For `createPost(input: CreatePostInput!)`, supply `channelId`, `text`, `assets` (an empty array is valid), `schedulingType` (`automatic` or `notification`), and a `mode` such as `customScheduled` with `dueAt`. Select the `PostActionSuccess` and error union fragments in the response. A public media URL must remain reachable until publish time.
4. For a line below the post, use `metadata.linkedin.firstComment` on LinkedIn or an X `metadata.twitter.thread` containing the **main post first**, with its assets, then the self reply. Buffer cannot use that thread to reply to somebody else's post. Other networks have different support: inspect the current schema before promising a first comment.
5. Read the created post back. Compare channel, due time, draft or scheduled state, text, assets, and thread or comment metadata. For a comment that must appear, inspect the live network post after publish. A stored first comment or a sent record with `error: null` does not prove the comment appeared.

## Editing without losing content

In the source workflow, edits that omitted text or media failed validation or lost media. Current API behavior can vary by field and version, so read the post and explicitly preserve its text, assets, metadata, due time, and draft state when editing. The asset read field is `source`; the write field is `url`. Do not send a returned video `thumbnail` as `thumbnailUrl`: some networks reject custom thumbnails. Read back and compare every field that matters. On YouTube and Instagram, preserve required network metadata when changing video assets.

Buffer may return `429 RATE_LIMIT_EXCEEDED` for a 24 hour window. Stop polling when that happens. If your workflow stores a retry job, label it **queued, not scheduled**, retain idempotency data, and revalidate time and channel before replay. Never turn an uncertain create result into a second create without checking the queue.

## Example

A team needs an X video post at 10:00 with a link in a self reply. Resolve the X channel ID, confirm its slot, create a draft with the video in `thread[0]` and the link in `thread[1]`, then read it back and verify `thread[0].assets` is populated. After approval, arm the exact draft and inspect the live thread shortly after publish.
