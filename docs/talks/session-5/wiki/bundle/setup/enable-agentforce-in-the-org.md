---
type: Process
title: Enable Agentforce in a Salesforce org — the two toggles and the licence
description: "The org-level enablement steps that gate everything else, including the second toggle that lives in a page header rather than the settings list."
source: ["Setup > Agentforce Agents page header toggle, s5demo 2026-08-31", "Setup > Einstein Generative AI 'Turn on Einstein'", "PermissionSetAssignment query for CopilotSalesforceUser in s5demo"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, salesforce, setup, enablement]
---
# Enable Agentforce in the org

Do these first. Every later step fails in a confusing way if one is missed.

## 1. Turn on Einstein

Setup → Quick Find **"Einstein"** → *Einstein Generative AI* → **Turn on Einstein**.

## 2. Turn on Agentforce Agents

Setup → Quick Find **"Agentforce Agents"** → the toggle is in the **page header**, top right,
labelled `Agentforce` with an `On`/`Off` state underneath.

This is the one people miss, because it is not in the settings list where the first toggle
was — it is on the object page itself. With it off, agents exist but do nothing.

## 3. Assign the agent-user permissions

The agent runs as a user, so that user needs Agentforce access. `CopilotSalesforceUser` grants
the Agentforce panel and does **not** grant field access — worth knowing, because it means
assigning it does not quietly break a field-level-security story.

```bash
sf org assign permset --name CopilotSalesforceUser --target-org <org> --json
```

## 4. Verify before moving on

```bash
export SF_AUTOUPDATE_DISABLE=true   # see the CLI-warning gotcha
sf data query --target-org <org> \
  -q "SELECT DeveloperName, Type FROM BotDefinition" --json | sed -n '/^{/,$p'
```

If that returns rows, the platform is on. A `BotVersion` with `Status = 'Active'` is what
"the agent is live" actually means:

```bash
sf data query --target-org <org> \
  -q "SELECT BotDefinition.DeveloperName, VersionNumber, Status FROM BotVersion WHERE Status='Active'" \
  --json | sed -n '/^{/,$p'
```

## What this does not do

Enabling Agentforce does **not** make an agent reachable from Slack. That is a separate
pipe with its own constraints —
[install the agent in Slack](install-the-agent-in-slack.md) and
[Agent Script cannot reach Slack](../gotchas/agent-script-cannot-reach-slack.md).

Related: [build the agent](build-the-agent.md).
