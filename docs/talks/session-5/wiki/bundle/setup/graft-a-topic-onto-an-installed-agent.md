---
type: Process
title: Graft a topic onto an already-installed agent
description: "The workaround used when a sandbox cannot register a new agent with Slack: move the topic to an agent that already has a Slack identity, and the two deploy errors it produces."
source: ["graft_topic_onto_installed_agent.py", "deploy errors: xsi prefix not bound; duplicate value found <unknown>", "Agentforce Builder showing Deal_Desk_sug on Slack_Employee_Help 2026-08-31"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, slack, workaround, metadata, setup]
---
# Graft a topic onto an installed agent

Use this when the agent you built cannot be registered with Slack but another agent already
is. Slack registration belongs to the **agent**, not to its topics — so move the topic, not
the registration.

**Reversible.** Keep the original retrieved bundle; redeploying it restores the target agent.

## Steps

1. **Retrieve the target's bundle** (the already-installed agent) and keep an untouched copy.
2. **Generate your own bundle**, then lift the `<localTopicLinks>` and `<localTopics>`
   elements out of it.
3. **Suffix every local name.** Local topic and action `developerName`s must be unique
   **org-wide**, not per bundle.
4. **Inject the `xsi` namespace** into the target's root element if it is absent.
5. **Splice in schema order** — `localTopicLinks` and `localTopics` sort after `genAiPlugins`
   and before `masterLabel`.
6. **Copy the action schemas** under the *target* bundle's `localActions/<topic>/` path.
7. Deactivate → deploy → activate.

## The two errors, and what they actually mean

**`The prefix "xsi" for attribute "xsi:nil" ... is not bound`**

Your topic uses `xsi:nil` on `<language>`; the target bundle's root never declared the
namespace. Fix:

```
<GenAiPlannerBundle xmlns="http://soap.sforce.com/2006/04/metadata"
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
```

**`duplicate value found: <unknown> duplicates value on record with id: <unknown>`**

Names nothing, means everything: a local topic or action `developerName` already exists
somewhere in the org. This is why bundles retrieved from an org carry generated suffixes on
every topic and action (`GetRecordDetails_179UT000000GE73`). Suffix yours —
`Deal_Desk` became `Deal_Desk_sug` — and alias the schema sources so the suffixed names still
resolve to the same files.

## Verify

Open the target in Agentforce Builder. The **Subagents** list should show your topic, and
`This Subagent's Actions` should list every action you attached. Then @-mention the agent in a
channel — the admin panels will not tell you the truth
([both status panels lie](../architecture/slack-and-agentforce.md)).

## The side effect to expect

Changing an installed agent's definition flips it back to **"Updated"** in Slack's
*Needs Review* queue, and `Active Agents` may drop to zero, while the agent keeps answering.
Re-approve it rather than trusting that it will keep working.

Related: [Polly](../cast/polly-peopleops.md), [build the agent](build-the-agent.md).
