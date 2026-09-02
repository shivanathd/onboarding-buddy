---
type: Concept
title: How the two bots interact — asymmetric by design, and the closer depends on it
description: "Agentforce can hand work to a bot; a bot cannot hand work back. The mechanism in each direction, the three guards it needs, and why the asymmetry is the governance thesis rather than a gap."
source: ["Railway worker logs MESSAGE handoff / DUPLICATE dropped 2026-08-31", "conversations.history on <your record channel> showing bot_message from <a bot id>", "Salesforce KB 005388402 on per-user Agentforce sessions in Slack"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [handoff, bots, governance, slack, agentforce]
---
# How the two bots interact

**Agentforce → worker works. Worker → Agentforce does not.** That asymmetry is not a bug or a
missing feature, and the demo is built to land on it.

## Direction one: Agentforce hands off to the worker

```
you   -> @Polly  "post the roster and ask @onboarding-buddy to start onboarding them"
Polly -> calls Query Records twice (Job, then Placements)
Polly -> calls Send Message to a Slack Channel
         => a REAL bot_message from <a bot id>, naming the four consultants
            and containing <@YOUR_WORKER_USER_ID>
Slack -> delivers that message event to the worker
worker-> "MESSAGE handoff from bot <a bot id>, turn 1"
worker-> replies in thread with the cohort status
```

Verified live in the record channel. The roster post is a genuine channel message — which is
the whole reason the handoff has to go through
`Slack__SendMessageToSlackChannel` rather than the agent's conversational reply.

### Three guards, all necessary

| Guard | Why |
|---|---|
| A plain `message` listener alongside `app_mention` | `app_mention` is unreliable for bot-authored channel mentions — it fired zero handlers once and both the next time |
| A dedupe on `(channel, event ts)` | when both paths fire you get two replies 0.6 s apart; it also absorbs Slack's event retries |
| Bot allow-list + per-thread turn cap | two bots that can each mention the other will ping-pong for as long as the room lets them, and a reply path usually has no rate limit of its own |

The debugging story is worth telling: [duplicate bot mentions](../gotchas/duplicate-bot-mentions.md).

## Direction two: the worker cannot call the agent

An Agentforce agent invoked from Slack opens **a new session per invocation, bound to the
invoking user's Salesforce identity, running every action in that user's security context**.

A bot has no Salesforce identity. There is no user for the platform to run as. So there is
nothing to bind the session to, and the invocation cannot happen — **not because a guard was
added, but because a required thing is absent.**

## Why that is the closer, not a gap

Act 5 is deliberately shaped around it. The worker finishes, posts completion, names the
agent — and then **you** type the Closed Won request.

> "Notice who did that last step. Not the worker. The worker *asked*, and it asked me.
>
> A bot cannot authorise a CRM write, because there's no user for the platform to run as.
> That's not a gap in my demo. That's the governance model. Two agents can do the work and
> still not be able to close the deal without a person."

A room that has spent an hour watching agents do things will remember the moment one of them
could not.

## What we deliberately did not build

A **bridge bot** — a second Socket Mode client that could relay worker → agent — is feasible
and was rejected. It would have manufactured a Salesforce identity for the bot to borrow,
which is exactly the property the closer depends on not existing. Building it would have made
the demo more impressive and less true.

Related: [the cast](../cast/cast-of-players.md), [the closer](../demo/the-closer.md),
[Slack and Agentforce](slack-and-agentforce.md).
