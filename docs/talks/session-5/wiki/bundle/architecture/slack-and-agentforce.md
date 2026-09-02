---
type: Concept
title: Slack and Agentforce — the install pipe, and the reply that nobody else can see
description: "How a Salesforce agent becomes a Slack bot user via the admin review queue, why its channel answers are ephemeral to the asker, and why both status panels lie about runtime state."
source: ["<your-workspace>.slack.com/admin/agentforce Needs Review and Active Agents tabs 2026-08-31", "conversations.replies on <your record channel> showing subtype agentforce_message", "Setup > Agent Details > Connections for Slack_Employee_Help"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, agentforce, install, ephemeral, architecture]
---
# Slack and Agentforce

The third pairing, and the one with the most surprises per square inch.

## The install pipe

```
Salesforce org          Slack org admin                     Slack workspace
agent, Active      ->   Admin > Manage Agentforce      ->   a real bot user
                        Needs Review > Review > Install     @-mentionable in channels
```

Requirements that are each individually fatal if missed:

- The agent must be **non-DSL** and template-derived. See
  [Agent Script cannot reach Slack](../gotchas/agent-script-cannot-reach-slack.md).
- **The agent's label must contain the word "Agent"** or Slack hides it from the queue.
- On Slack **Pro** there is no workspace picker — install applies to the org.
- If the installed agent does not appear in the sidebar: workspace **Preferences →
  Navigation → Show app agents**.
- Turn **automatic account mapping off and map manually** in a sandbox — sandbox emails carry
  an `.invalid` suffix and will not match.

The queue also shows the agent's **Salesforce Org** column, which is how you confirm the
agent you are looking at came from the org you think it did.

## The reply is ephemeral, and that changes the architecture

@-mention an installed agent in a channel and the **channel** gets only a stub:

```
I've privately shared an answer with <@U…> in this thread.
They can share it here if they think it's helpful.
```

The real answer is an **ephemeral message visible to the invoking user alone**, with subtype
`agentforce_message` on the stub. Two hard consequences:

1. On a screen share it works — but to anyone else it looks like the agent said nothing. Say
   so before you demo it.
2. **Ephemeral content is absent from the Slack API entirely.** It cannot be asserted on in a
   test, and it cannot be scraped. Anything that needs the answer's *content* verified must be
   checked through the agent runtime instead.

So a handoff cannot be done by *answering*. It needs an explicit
`Slack__SendMessageToSlackChannel` call, which produces a real message other bots can see.
Full detail: [an agent's reply is private](../gotchas/agent-replies-are-ephemeral.md).

## Both status panels lie

Two surfaces claim to tell you whether the Slack connection is live. Neither does.

| Panel | Says | Reality |
|---|---|---|
| Salesforce → Agent Details → **Connections** | `Messaging — Needs Setup` | Polly was installed and answering |
| Slack admin → **Active Agents** | `0 active agents` | same |

Slack *does* live under the **Messaging** connection — that part of the hunch is right, and
the legacy docs agree. But "Needs Setup" is not evidence of anything. Treat both panels as
decoration and **verify by @-mentioning the agent in a channel**. That is the only
trustworthy check, and it is why the preflight cannot automate this one.

A live caveat: grafting a topic onto Polly flipped her to **"Updated"** in *Needs Review*, and
`Active Agents` went to zero, while she kept working. Whether Slack eventually enforces that
pending re-review is unknown — so re-approving her before the talk is cheap insurance.

Related: [Salesforce and Agentforce](salesforce-and-agentforce.md),
[installing the agent](../setup/install-the-agent-in-slack.md).
