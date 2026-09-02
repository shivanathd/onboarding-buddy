---
type: Decision
title: Neither status panel reflects whether the agent actually works
description: "Salesforce says the Slack connection Needs Setup; Slack says 0 active agents. The agent was answering in a channel at the time. Verify by mentioning it."
source: ["Setup > Agent Details > Connections for Slack_Employee_Help showing Messaging / Needs Setup 2026-08-31", "slack-ug admin Agentforce > Active Agents showing 0 active agents", "same agent answering in <your record channel> minutes earlier"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, slack, admin, misleading-ui]
---
# Both status panels lie

Two surfaces claim to tell you whether an agent's Slack connection is live. Measured against a
working agent, both were wrong at the same moment.

| Panel | Said | Reality |
|---|---|---|
| Salesforce → Agent Details → **Connections** | `Messaging — Needs Setup` | installed and answering |
| Slack admin → Agentforce → **Active Agents** | `0 active agents` | same |

Slack genuinely *does* live under the **Messaging** connection — that part is right, and the
legacy docs agree. But `Needs Setup` is not evidence of anything, and chasing it is what sent
the early investigation down the wrong path entirely.

## The only trustworthy check

**@-mention the agent in a channel.** That is why the preflight cannot automate this one and
lists it as a manual check.

## A live risk this exposed

Grafting a topic onto the installed agent changed its definition, which flipped it to
**"Updated"** in Slack's *Needs Review* queue and dropped `Active Agents` to zero — while it
kept answering normally.

Whether Slack eventually enforces that pending re-review is **unknown**. The cheap insurance
is to re-approve the agent in the admin queue before relying on it. Treat "it worked an hour
ago" as weak evidence when the definition has changed since.

## The general rule

For Agentforce-in-Slack, **status UI is decoration and behaviour is truth**. This is the same
lesson as
[a localAction with no schemas](local-action-schemas.md) — a green deploy and a green panel
both mean less than one real invocation.

Related: [Slack and Agentforce](../architecture/slack-and-agentforce.md),
[install the agent in Slack](../setup/install-the-agent-in-slack.md).
