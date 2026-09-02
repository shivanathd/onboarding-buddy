---
type: Decision
title: An agent's channel reply is private to the asker — and an absent agent fails just as silently
description: "Both of Agentforce-in-Slack's failure modes are invisible to the room, and neither is visible to the API. What to say, and what to check instead."
source: ["conversations.replies on <your record channel> 2026-08-31 showing only the stub, subtype agentforce_message", "Slack ephemeral 'they're not in this channel' notice with Add Them button"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, agentforce, ephemeral, silent-failure]
---
# The reply is private, and both failure modes are silent

## The reply itself is ephemeral

@-mention an installed Agentforce agent in a channel and the **channel** gets only a stub:

```
I've privately shared an answer with <@U…> in this thread.
They can share it here if they think it's helpful.
```

The real answer is an **ephemeral message visible to the invoking user alone**. The stub
carries subtype `agentforce_message`.

Consequences:

- To anyone but the asker the agent appears to have said nothing useful. On a screen share it
  works, but **say it out loud first** or it reads as a broken agent.
- **Ephemeral content is absent from the Slack API entirely.** `conversations.replies` returns
  only the stub. The answer cannot be asserted on programmatically, and it could not be read
  through the browser either — the thread flexpane stayed at *"Loading thread…"* under
  automation. Anything needing the answer's *content* verified must go through the agent
  runtime instead: Testing Center, or `sf agent preview`.

## An absent agent fails silently too

Mentioning an agent that is **not a member of the channel** produces no answer and no visible
error. Slack posts an ephemeral notice — *"You mentioned @X, but they're not in this
channel"* with an `Add Them` button — and **only the sender sees it**.

So proving a handoff works in one channel proves nothing about another. This was found the
hard way: the handoff had been verified in a scratch channel where the agent *had* been added,
and the record channel silently had not.

## So handoffs post explicitly

Because the conversational reply is private, an agent handing work to another bot cannot do it
by answering. It must call `Slack__SendMessageToSlackChannel`, which produces a **real**
channel message other bots can see. That action needs a channel **ID** — a name fails with
"channel ID might be invalid" — and Slack appends *"Action triggered by @user"* to the post.

## Two related API facts

- `conversations.history` returns **parent messages only**, never thread replies. An agent that
  replied in a thread looks silent through `history`. Use `conversations.replies`.
- Coordinate clicks on Slack's Block Kit buttons are unreliable under automation; clicking the
  same element by accessibility reference works. Drive Slack through the DOM, not pixels.

Related: [Slack and Agentforce](../architecture/slack-and-agentforce.md),
[install the agent in Slack](../setup/install-the-agent-in-slack.md).
