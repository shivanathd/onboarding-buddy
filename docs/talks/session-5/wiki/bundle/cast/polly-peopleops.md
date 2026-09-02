---
type: Service
title: Polly PeopleOps — who she is, and why she is the one on stage
description: "The Agentforce agent that answers deal questions in Slack: an inherited HR-facing agent carrying a grafted Deal Desk topic, used because a new agent could not be registered with Slack from a sandbox."
source: ["Setup > Agent Details for Slack_Employee_Help 2026-08-31", "Agentforce Builder subagent list showing Deal_Desk_sug", "<your-workspace>.slack.com/admin/agentforce Needs Review queue", "graft_topic_onto_installed_agent.py"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, slack, polly, workaround, teaching]
---
# Polly PeopleOps

**Polly is a nameplate.** The name, the avatar and the profile blurb belong to an HR-facing
agent somebody at Asymbl built in production in August 2025. The brain answering deal
questions is ours.

| Field | Value |
|---|---|
| Display name | Polly PeopleOps |
| API name | `Slack_Employee_Help` |
| Type | `AgentforceEmployeeAgent` |
| Version | 1, Active |
| Slack bot user | `YOUR_AGENT_USER_ID` · bot id `<a bot id>` |
| Copilot id | `<the installed agent id>` |
| Custom topic | `Deal Desk` / `Deal_Desk_sug` |
| Actions | 7 — see below |

## Why her and not an agent called "Deal Desk"

Because Slack would not take ours. A correctly-shaped, non-DSL, activated agent
(`Deal_Desk_Agent`) built entirely from CLI metadata **never appeared in Slack's review
queue**, and there is no UI affordance or metadata type in this sandbox to register one.
The agents Slack does offer all arrived as clone state from production.

The tell is in the IDs. Polly's copilot id starts `0XxUT…`; the agent built here starts
`0XxcW…`. Different org key prefixes — Polly's registration was minted in a different org.

Slack registration belongs to the **agent**, not to its topics. So the topic was grafted onto
an agent that was already registered. Full reasoning and the two traps it took in
[Agent Script cannot reach Slack](../gotchas/agent-script-cannot-reach-slack.md).

## What is actually hers versus ours

| Hers (inherited) | Ours (grafted) |
|---|---|
| Name, avatar, profile card | The `Deal Desk` subagent |
| Description: *"Help employees get answers to questions in Slack…"* | Classification: *"Answers questions about Salesforce opportunities, jobs, placements…"* |
| Role/Company text (Asymbl boilerplate) | 9 instructions, including the 29 valid stage values |
| `Last Modified By: Greg Symons` | 7 actions |

The Builder shows **exactly one subagent**: `Deal Desk`. That screenshot is the cleanest proof
that the behaviour on stage is ours —
[see it](../screenshots/index.md).

## Her seven actions

| Action | Does |
|---|---|
| Identify Record by Name | "Meridian" → a record id |
| Get Record Details | read the fields |
| Query Records | reach the Job and the Placements |
| Extract Fields and Values from User Input | turn "move it to Negotiation/Review" into a field/value pair |
| Update Record | the only one with `isConfirmationRequired = true` |
| **Send Message to a Slack Channel** | the handoff. Needs a channel **ID**, not a name |
| **Reply to a Slack thread** | threaded replies |

## Saying it out loud

The mismatch is visible — a PeopleOps agent answering deal-desk questions. Own it; it is a
better story than hiding it:

> "This agent is called Polly and she was built for HR. I'm borrowing her, because Slack
> won't let a sandbox register a brand-new agent — the install has to come from the
> production org. So I put my topic on an agent that was already allowed in. That's not a
> workaround I'm proud of, it's a constraint worth knowing before you promise someone a demo."

Do **not** rename her label to fix the cosmetics. The label is what Slack's review queue
matches on, and whether a rename survives an existing install is untested.

Related: [the cast](cast-of-players.md), [onboarding-buddy](onboarding-buddy.md),
[an agent's reply is private](../gotchas/agent-replies-are-ephemeral.md).
