---
type: Decision
title: An Agent Script agent cannot be deployed to Slack, and a sandbox cannot register a new one
description: "Two stacked constraints that each look like the other: the authoring lane decides Slack eligibility, and only clone-inherited registrations are installable from a sandbox."
source: ["BotVersion / GenAiPlannerBundle comparison of DSL and non-DSL agents in s5demo", "<your-workspace>.slack.com/admin/agentforce queue showing only Asymbl-org clone agents", "four candidate metadata types checked incl. EmbeddedServiceConfig"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, slack, agent-script, sandbox, constraint]
---
# Agent Script cannot reach Slack

Two constraints stack, and during the build each was repeatedly mistaken for the other.

## One: the authoring lane decides eligibility

An agent authored in **Agent Script** (`aiAuthoringBundle`, a `.agent` file,
`agentDSLEnabled: true`) never appears in Slack's agent queue. Every agent Slack *did* offer
carried `agentTemplate = Slack__SlackEmployeeHelp` and `agentDSLEnabled = false`.

`AgentforceEmployeeAgent` as a type is **necessary but not sufficient** — the type matching is
what made this look like a permissions or connection problem for hours. There is no Slack
setting to find on an Agent Script agent, because it is not a candidate.

**There is a visible tell.** In Setup → Agentforce Agents, Agent Script agents carry an
external-link `↗` icon next to their name (they open in the new Agentforce Builder);
template-derived agents do not. You can read the lane off the list.

Also load-bearing: **the agent's label must contain the word "Agent"** or Slack hides it from
the queue regardless.

## Two: a sandbox cannot register a *new* agent

A correctly-shaped, non-DSL, activated agent built entirely from CLI metadata still never
reached the queue. The agents sitting at "Ready to install" are **inherited clone state** from
production. There is no UI affordance and no metadata type for creating a registration — four
candidate types were checked, including `EmbeddedServiceConfig`.

A control group settled it: a DSL agent and a non-DSL agent behaved identically, so the second
constraint is about **registration**, not authoring.

**The IDs prove it.** The inherited agent's copilot id starts `0XxUT…`; an agent created in
this sandbox starts `0XxcW…`. Different org key prefixes — the registration was minted
elsewhere.

## Consequence to plan around

Agent Script and Slack are **mutually exclusive lanes**. Anything needing both a Slack surface
and Agent Script tooling needs **two agents**, and they will drift — see
[two authoring lanes drift](two-authoring-lanes-drift.md).

The workaround that shipped:
[graft a topic onto an installed agent](../setup/graft-a-topic-onto-an-installed-agent.md).

Related: [Polly](../cast/polly-peopleops.md),
[Slack and Agentforce](../architecture/slack-and-agentforce.md).
