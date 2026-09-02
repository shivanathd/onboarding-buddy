---
type: Process
title: Install an Agentforce agent into a Slack org
description: "The admin review queue route from a Salesforce agent to a Slack bot user, the label rule, the sidebar setting, and the only trustworthy way to confirm it worked."
source: ["<your-workspace>.slack.com/admin/agentforce Needs Review > Review > Install 2026-08-31", "Slack ephemeral 'they're not in this channel' notice with Add Them", "conversations.history channel_join for YOUR_AGENT_USER_ID"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, agentforce, install, admin, setup]
---
# Install the agent in Slack

## Steps

1. **Slack admin** → `<your-workspace>.slack.com/admin/agentforce` → **Needs Review**.
2. Find the agent. Confirm the **Salesforce Org** column names the org you expect.
3. **Review** → consent modal → **Install agent**. On Slack **Pro** there is no workspace
   picker; the install applies to the org.
4. Turn **automatic account mapping off** and map accounts manually for a sandbox.
5. If the agent is missing from the sidebar: workspace **Preferences → Navigation → Show app
   agents**.
6. **Add the agent to each channel it must answer in.** This is a separate step and it is
   easy to skip — see below.

Installed agents appear in the Slack sidebar under their own **Agentforce** heading, not under
Agents & apps.

## The prerequisites that fail silently

- The agent must be **non-DSL / template-derived**
  ([why](../gotchas/agent-script-cannot-reach-slack.md)).
- **Its label must contain the word "Agent"**, or it never enters the queue.
- In a sandbox, only agents whose registration arrived as **clone state from production** are
  installable. A brand-new sandbox agent cannot be registered by any route found.

## Channel membership is a separate, silent requirement

Mentioning an agent that is not in the channel produces **no answer and no visible error**.
Slack posts an ephemeral notice — *"You mentioned @X, but they're not in this channel"* with an
`Add Them` button — and **only the sender can see it**. To a room it is a mention followed by
nothing.

So proving a handoff works in one channel proves nothing about another. Click `Add Them`, or
invite the agent explicitly. Verify from the API by looking for its `channel_join`:

```bash
curl -s -H "Authorization: Bearer $BOT_TOKEN" \
  "https://slack.com/api/conversations.history?channel=$CHANNEL&limit=200" |
python3 -c "import json,sys
d=json.load(sys.stdin)
for m in d['messages']:
    if m.get('subtype') in ('channel_join','channel_leave') and m.get('user')=='$AGENT_USER':
        print(m['subtype']); break"
```

`conversations.members` would be the right call but needs `channels:read`, which a
`channels:history`-only app does not have.

## How to confirm the install actually worked

**@-mention the agent in a channel.** That is the only reliable test. Neither Salesforce's
`Connections` panel nor Slack's `Active Agents` tab reflects runtime state — see
[both status panels lie](../architecture/slack-and-agentforce.md).

Related: [graft a topic onto an installed agent](graft-a-topic-onto-an-installed-agent.md).
