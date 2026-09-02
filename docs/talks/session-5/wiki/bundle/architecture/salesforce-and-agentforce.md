---
type: Concept
title: Salesforce and Agentforce — the agent is a Salesforce user, not a chatbot
description: "How an Agentforce agent is assembled (topic, instructions, actions), why it runs under the invoking user's permissions, and why the confirmation gate is platform-held rather than prompt-held."
source: ["Agentforce Builder subagent + actions for Slack_Employee_Help 2026-08-31", "sf agent test run S5_Deal_Desk_Suite 36/36 2026-08-31", "FieldPermissions query on Opportunity.Amount in s5demo"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, salesforce, permissions, architecture]
---
# Salesforce and Agentforce

The mental model that makes the rest of the demo make sense: **an Agentforce agent is not a
chatbot bolted onto a CRM. It is a caller inside the CRM, and it inherits a user's
permissions.**

## How one is assembled

Three layers, and only the middle one is prose:

```
Agent            identity, type, Slack registration, active version
  └─ Topic       "when should I be the one answering?" + instructions
       └─ Actions  the only things it can actually do
```

- **Topic** carries a *classification description* (how the planner decides this topic
  applies), a *scope*, and an ordered list of **instructions**.
- **Actions** are a hard allow-list. An agent with no delete action cannot be talked into
  deleting. This is the single most reassuring thing to show a sceptical room.

Our topic: 7 actions, 9 instructions. The full list is on
[Polly](../cast/polly-peopleops.md).

## Instructions are not suggestions, but they are not code either

Two beats in the demo come straight out of this distinction.

**Instruction 6 embeds all 29 valid Opportunity stage values.** Before that, the instruction
said "check the value against the valid stages" — and the agent cheerfully drafted
`Handshake Pending`, because nothing in its context contained the list. The fix was not
better prose. It was **giving it the data**. Say that out loud; it is the most useful thing
in the hour for anyone about to write agent instructions.

**Instruction 3 teaches a join path** the agent could not guess:
`Opportunity → bpats__Job__c → bpats__Placement__c`. Without it the agent answered "no
consultant placements are listed in the available data" — confidently, and wrongly. See
[the recruiting data model](../setup/seed-the-recruiting-data.md).

## The confirmation gate is held by the platform

`Update Record` is declared with `isConfirmationRequired = true`. The agent drafts, then
stops. It is not being polite — it *cannot* proceed. Actions executed stop at
`extract_fields_and_values`; `update_record` has not run.

> "That gate is not a sentence in a prompt asking it to be careful. I could not talk it into
> skipping that if I tried."

## Permissions belong to the invoker, not the agent

Every action runs in the **invoking user's** security context. Consequences, both of which
shape the demo:

- **The permissions beat is real but cannot be demoed through Slack.** The one human in
  `slack-ug` maps to the s5demo System Administrator, who can read `Amount`. Through Slack
  the agent always sees everything. Tell it from Setup → Profiles → Demo AE → Field-Level
  Security → Opportunity → `Amount`, unchecked. Verified and static.
- **A bot cannot invoke the agent at all** — it has no Salesforce identity to run as. That is
  the closer. See [how the two bots interact](how-the-two-bots-interact.md).

Related: [Salesforce and Slack](salesforce-and-slack.md),
[Slack and Agentforce](slack-and-agentforce.md),
[building the agent](../setup/build-the-agent.md).
