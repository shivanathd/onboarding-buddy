---
type: Process
title: Build a Slack-capable Agentforce agent from the CLI, not the UI
description: "The metadata shape of a template-derived agent — Bot, BotVersion and a GenAiPlannerBundle with inline localTopics — and the four traps that make hand-authoring it fail silently."
source: ["make_deal_desk_agent.py", "retrieved GenAiPlannerBundle Content_Guardian from s5demo", "sf project deploy start / sf agent activate on s5demo 2026-08-31"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, metadata, cli, salesforce, setup]
---
# Build the agent from the CLI

The UI route (Agentforce Studio → New Agent → pick a Slack template) works and is faster to
explain. This is the metadata route, which is reproducible, diffable and reviewable — and
which is how the demo's agent was actually built.

## The three metadata types

```
Bot                      the agent identity
BotVersion               the version, its topics, its context variables
GenAiPlannerBundle       the planner: topic links + inline localTopics + localActions
```

A template agent's custom topic is **not** a separate `.genAiPlugin` file. It is an inline
`<localTopics>` block inside the `.genAiPlannerBundle`.

## Get a working reference first

Do not hand-author from the docs. Retrieve an agent that already works in the target org and
copy its shape — a retrieved bundle is by definition what the platform accepts:

```bash
sf project retrieve start -m "GenAiPlannerBundle:<WorkingAgent>" --target-org <org> --json
```

## The four traps

**1. Each action appears twice, under different tag names.** Inside a topic it is
`<localActionLinks><functionName>`; at planner level it is `<genAiFunctionName>`. Plus a full
`<localActions>` definition. `fullName` must equal `developerName`.

**2. `invocationTarget` is not `source`.** They differ per action and guessing fails:

| `source` | `invocationTarget` | type |
|---|---|---|
| `EmployeeCopilot__IdentifyRecordByName` | `identifyRecordByName` | standardInvocableAction |
| `EmployeeCopilot__GetRecordDetails` | `getDataForGrounding` | standardInvocableAction |
| `EmployeeCopilot__QueryRecords` | `queryRecords` | standardInvocableAction |
| `EmployeeCopilot__ExtractFieldsAndValuesFromUserInput` | `getRecordFieldsAndValues` | standardInvocableAction |
| `EmployeeCopilot__UpdateRecordFields` | `einsteinCopilotUpdateRecord` | standardInvocableAction |
| `Slack__SendMessageToSlackChannel` | `slackAgentDynamic__SendMessageToSlackChannel` | **slack** |
| `Slack__ReplyInThread` | `slackAgentDynamic__ReplyInThread` | **slack** |

**3. Metadata is schema-ordered** — alphabetical per level. Inside `localTopics`:
`fullName, aiPluginUtterances*, canEscalate, description, developerName,
genAiPluginInstructions*, language, localActionLinks*, localActions*, localDeveloperName,
masterLabel, pluginType, scope`. Out of order, it fails.

**4. Every `localAction` needs `input/schema.json` and `output/schema.json` on disk.**
Without them the agent deploys, activates, and silently cannot resolve the action. This one
cost the most time — see
[a localAction with no schemas fails silently](../gotchas/local-action-schemas.md).

## The label rule

**The agent's label must contain the word "Agent"** or Slack will not show it in the review
queue, no matter how correct the metadata is. `Deal Desk Agent`, not `Deal Desk`.

## The deploy loop

An **active** agent cannot be edited — Bot, BotVersion *and* the planner bundle are all
locked (`Cannot update record as Agent is Active`). So:

```bash
sf agent deactivate --api-name <Api_Name> --target-org <org> --json
sf project deploy start --source-dir force-app --target-org <org> --json
sf agent activate   --api-name <Api_Name> --target-org <org> --json
```

`sf agent activate` also requires the working directory to be a **DX project root**, or it
fails with `InvalidProjectWorkspaceError` naming a directory rather than the real problem.

## For an Agent Script agent instead

Different lane entirely: an `aiAuthoringBundle` with a `.agent` file, published with
`sf agent publish authoring-bundle --api-name <name> --target-org <org> --json`. Cleaner to
author — **and it can never reach Slack**. See
[Agent Script cannot reach Slack](../gotchas/agent-script-cannot-reach-slack.md).

Related: [graft a topic onto an installed agent](graft-a-topic-onto-an-installed-agent.md).
