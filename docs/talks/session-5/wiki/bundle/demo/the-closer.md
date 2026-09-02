---
type: Concept
title: The closer — why a bot cannot close the deal, and why that is the point
description: "The governance argument the whole hour builds toward, the mechanism underneath it, and the more impressive thing we deliberately did not build."
source: ["Salesforce KB 005388402 on per-user Agentforce sessions bound to the invoking user's identity", "Act 5 design decision 2026-08-31", "rejected bridge-bot design"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [governance, closer, teaching, agentforce]
---
# The closer

Most agent demos end by showing that the agents can do more. This one ends by showing what
they cannot do, and why that is correct.

## The mechanism

An Agentforce agent invoked from Slack opens **a new session per invocation, bound to the
invoking user's Salesforce identity, running every action in that user's security context.**

A bot has no Salesforce identity. There is no user for the platform to run as. So a bot cannot
invoke the agent, and therefore cannot cause a CRM write — **not because a guard was added,
but because a required thing is absent.**

That is a much stronger claim than "we added a human-in-the-loop step". A guard can be removed.
An absence cannot.

## The lines

> "Notice who did that last step. Not the worker. The worker *asked*, and it asked me.
>
> An Agentforce agent in Slack runs every action in the invoking user's Salesforce identity.
> A bot doesn't have one. So a bot cannot authorise a CRM write — not because I put a guard
> in, but because there's no user for the platform to run as.
>
> That's not a gap in my demo. That's the governance model. Two agents can do the work and
> still not be able to close the deal without a person."

And the sweep back through the five sessions:

> "Five sessions. Session one was one message. Today: a CRM record living in a channel, an
> agent that reads it under your permissions and writes only with your consent, a Python
> worker that picks up where the agent stops, and the two of them handing work to each other
> in front of you. That's the fleet. And the only thing holding it together is the channel."

## The thing we did not build

A **bridge bot** — a second Socket Mode client that could relay worker → agent — is feasible.
It was rejected on purpose.

It would work by manufacturing a Salesforce identity for the bot to borrow, which is exactly
the property this closer depends on not existing. Building it would have made the demo more
impressive and less true. Worth one sentence if someone asks "why not just…":

> "I could have bridged it. But the only way to bridge it is to lend the bot a human's
> identity, and then the interesting thing about this whole hour stops being true."

## Two smaller honesty beats that land well

- **The permissions story is told from Setup, not acted out**, because through Slack the agent
  always runs as the admin. Saying so is more convincing than a chat bubble.
- **The invalid-stage refusal was a defect first.** The agent drafted a stage that did not
  exist until the instruction was given the actual list of values. "The fix wasn't a better
  prompt — it was giving it the data."

Related: [how the two bots interact](../architecture/how-the-two-bots-interact.md),
[the five acts](the-five-acts.md).
