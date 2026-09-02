---
type: Decision
title: app_mention is unreliable for bot-authored channel mentions — listen on both paths and dedupe
description: "The same setup fired zero handlers once and two the next time, producing duplicate replies. The fix is idempotency, not choosing a listener."
source: ["Railway worker logs: one MESSAGE handoff line, two ANSWER replied lines 2026-08-31", "conversations.replies reply_count 2 then 1 after the fix", "onboarding-buddy app.py at 375d1fc"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, bolt, events, bots, idempotency]
---
# app_mention for a bot's mention is intermittent

Slack documents a bot-to-bot event exclusion only for **DMs** and is silent on channels.
Channels turned out to be neither reliably included nor reliably excluded.

| Observation, same app and setup | Result |
|---|---|
| An Agentforce agent posted a `bot_message` with correct `<@bot>` markup | `app_mention` did **not** fire — no reply, no log line |
| The same handoff, different channel, days later | **Both** `app_mention` and the `message` listener fired |

The first observation motivated adding a `message.channels` subscription and a plain `message`
listener. The second then produced a visible defect: **two near-identical replies 0.6 s
apart** to a single handoff. On a stage that reads as the bot stuttering.

The logs made the double path visible — one `MESSAGE handoff … turn 1` line but two
`ANSWER replied in thread` lines, so the extra reply arrived via `app_mention`, which logs
nothing.

## The fix is idempotency, not listener selection

Dropping either listener is wrong under the other observation, and neither choice covers
Slack's own event retries. Dedupe on `(channel, event ts)` at the one choke point both
listeners pass through:

```python
key = "%s:%s" % (event.get("channel"), event.get("ts"))
if key in _seen:
    print("DUPLICATE dropped a second delivery of %s" % key, flush=True)
    return
_seen[key] = True
while len(_seen) > _SEEN_MAX:
    _seen.popitem(last=False)   # bounded, so a long shift cannot grow it forever
```

Verified after redeploy: one handoff, one `DUPLICATE dropped` line, one reply, and
`conversations.replies` reporting 1 instead of 2.

## Two Bolt specifics worth keeping

- Register the string **`"message"`**, never `"message.channels"` — Bolt's
  `_verify_message_event_type` raises on any type starting `message.`. The `message.channels`
  scope goes in the app manifest; the listener registers the bare event.
- A `message` listener sees **every** message in every channel, so everything `app_mention`
  gave for free must be re-done: require the bot's own user id in the text, drop the app's own
  `bot_id`, filter subtypes. Bolt's `IgnoringSelfEvents` middleware only covers `app_mention`.

Add a **per-thread turn cap** too. Two bots that can each mention the other will ping-pong for
as long as the room allows, and a reply path usually has no rate limit of its own.

## And a deployment gotcha found alongside it

**A git push does not deploy this worker.** `railway status` shows
`source = {"image": null, "repo": null}` — the service is not GitHub-linked, and every
deployment came from `railway up`. Push is source control; `railway up` is deployment. They are
two separate steps.

Related: [how the two bots interact](../architecture/how-the-two-bots-interact.md),
[onboarding-buddy](../cast/onboarding-buddy.md).
