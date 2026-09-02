---
type: Service
title: onboarding-buddy — the hand-written half of the fleet
description: "The Python worker on Railway: two Slack doors, a Slack List for memory, a read-only MCP server, and the guards that let another bot wake it safely."
source: ["shivanathd/onboarding-buddy app.py at 375d1fc", "railway logs 2026-08-31", "slackLists.items.list on YOUR_LIST_ID"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [worker, slack, mcp, railway, bolt]
---
# onboarding-buddy

The half of the demo that is code. Built in Session 4, extended in Session 5 to be wakeable
by another bot.

| Field | Value |
|---|---|
| Slack app | `<an app id>` |
| Bot user | `YOUR_WORKER_USER_ID` (`@onboarding-buddy`) |
| Bot id | `<a bot id>` |
| Host | Railway project `onboarding-buddy`, service `worker` |
| Public URL | `<your-app>.up.railway.app` — `/healthz`, `/mcp` |
| Repo | `shivanathd/onboarding-buddy` (public) |
| Memory | Slack List `YOUR_LIST_ID`, 12 rows |
| Timezone | `Asia/Dubai` (a container is UTC unless `TZ` is set) |

## Two doors

**Door one — Socket Mode, dialling out.** Listens for `app_mention`, `reaction_added`,
`message`, and Block Kit button clicks. Answers in threads.

**Door two — an MCP server at `/mcp`.** Slack's own Slackbot is the client. Slack signs every
request with the app's signing secret, so there is no bearer token to paste anywhere. There is
**no write tool on that server** — the boundary is the shape of the module, not a promise in a
prompt.

## Its memory is a Slack List, not a database

12 rows, one per onboarding step, four consultants × three steps. Every number the worker
reports is countable by eye in the List — which is the point, and worth saying: *"if it says
five are overdue, you can go and count five."*

The step text carries the consultant's name (`Sara Okonkwo — Access badge`) because the
`New hire` column is a Slack **person** column and this workspace has one human. See
[the one-member workspace](../gotchas/one-member-workspace.md).

## What lets another bot wake it

Three guards, added in Session 5 and all load-bearing:

1. **A `message` listener as well as `app_mention`** — because `app_mention` is unreliable for
   bot-authored channel mentions.
2. **A bot allow-list** (`HANDOFF_BOT_IDS`) so only the deal desk agent can wake it, not any
   bot that happens to type its name.
3. **A dedupe on `(channel, event ts)`** and a per-thread turn cap. Two bots that can each
   mention the other will ping-pong until the room stops them.

Why all three, and the duplicate-reply defect that proved it:
[duplicate bot mentions](../gotchas/duplicate-bot-mentions.md).

## What it will not do, and how it says so

It reads the List and replies. It does not tick boxes, move dates, escalate, or post anything
else. Asked to *start* onboarding it does not refuse — it answers the real question and puts
the boundary last:

> "Onboarding for the four Meridian placements is already underway, 12 steps tracked, 5
> overdue. • Sara Okonkwo, Access badge, 8 days overdue … Nudges on these go out via the
> tick, not from me."

It used to open with *"I'm not able to start onboarding, I only read the List and reply
here"*, which is true, useless as an opening, and read as a broken bot. That was prompt
ordering, not a capability limit. See
[lead with the answer](../gotchas/lead-with-the-answer.md).

Related: [the cast](cast-of-players.md), [Polly](polly-peopleops.md),
[how the two bots interact](../architecture/how-the-two-bots-interact.md).
