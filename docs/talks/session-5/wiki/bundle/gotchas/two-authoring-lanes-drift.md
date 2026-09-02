---
type: Decision
title: Two agents in two authoring lanes drift silently — assert shared behaviour in tests
description: "An instruction added to one agent's generator never reached the other agent. Nothing warned; only a new test case caught it."
source: ["sf agent test run S5_Deal_Desk_Suite case 12 failing on v4 2026-08-31", "make_deal_desk_agent.py vs S5_Deal_Desk.agent diff", "v5 published and passing 36/36"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [agentforce, testing, drift, agent-script]
---
# Two authoring lanes drift, and nothing warns you

Because [Agent Script and Slack are mutually exclusive
lanes](agent-script-cannot-reach-slack.md), a system needing both ends up with two agents meant
to behave the same. They will not.

A new capability was added by editing the **generator** that builds the Slack-side agent's
planner bundle. The Agent-Script agent is a **separate `aiAuthoringBundle`** and never received
it. It kept deploying, kept activating, kept passing every existing test, and answered the new
kind of question with a confident negative:

```
actions: ['identify_record', 'get_record_details']     # never queried the related object
answer : "does not show a specific field for the number of consultants.
          No consultant placements are listed in the available data."
```

Nothing in either lane reported a problem. The only thing that caught it was **adding a test
case for the new behaviour and running it against the other agent.**

## The rule

When two agents are supposed to share behaviour, the shared behaviour belongs in the **test
suite**, asserted against whichever agent the suite can reach. A capability added to one lane
is not done until the other lane's test passes.

Related: [test wording rots](test-wording-rots.md),
[build the agent](../setup/build-the-agent.md).
