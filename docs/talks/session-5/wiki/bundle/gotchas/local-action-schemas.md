---
type: Decision
title: A localAction with no input and output schemas deploys, activates, and silently cannot resolve
description: "The agent answered 'I can't access the details' with no error anywhere; only a metadata retrieve named the cause."
source: ["sf project retrieve start -m GenAiPlannerBundle on s5demo 2026-08-31", "RESOURCE_NOT_FOUND on c__get_record_details because an input or output schema is missing"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, metadata, silent-failure, debugging]
---
# A localAction with no schemas fails silently

An agent built from CLI metadata deployed cleanly, activated cleanly, resolved its topic
correctly — and answered every question with *"I can't access the details."* Nothing in the
deploy output, the activation, or the Setup UI reported a problem.

The cause was visible only in a **metadata retrieve** of the deployed bundle:

```
RESOURCE_NOT_FOUND: ... "c__get_record_details" because an input or output schema is missing.
```

Each `localAction` inside a `genAiPlannerBundle` needs an `input/schema.json` and an
`output/schema.json` on disk under `localActions/<topic>/<action>/`. Without them the action is
accepted at deploy time and unresolvable at run time.

## The rule this establishes

**For Agentforce metadata, a successful deploy is not evidence the thing works.**

When an agent behaves as though an action does not exist, retrieve the bundle back out of the
org and read what the org actually stored. The deploy path and the Setup UI both stay silent;
the retrieve does not.

The fix was copying 14 `schema.json` files out of bundles retrieved from the same org —
retrieved bundles are the reference implementation for shape, since they are by definition what
the platform accepts.

Related: [build the agent](../setup/build-the-agent.md).
