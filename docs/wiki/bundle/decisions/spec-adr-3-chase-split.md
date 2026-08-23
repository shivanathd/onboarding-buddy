---
type: Decision
title: "ADR-3: chase split, detection is code and escalation is judgement"
description: Past grace detection is a date comparison in plain Python; only the escalation paragraph calls the model, with a template fallback.
source: ["spec DECISIONS.md ADR-3", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, model-boundary, chase]
---
# ADR-3: chase split, detection is code and escalation is judgement

**Context.** A reader has to be able to see which parts of a worker genuinely need judgement
and which do not.

**Decision.** Past grace detection is a subtraction: Status is Open, Due is set, and now exceeds
Due plus the grace window. Zero model calls. Only the escalation paragraph borrows the model, and
it has a template fallback.

**Consequences.** The clock job runs identically with the model unavailable, which is what one
holdout scenario proves. The cost story stays honest, because model calls are countable on one
hand per day. And the audit story is simple: nobody has to trust a model with the question of
who gets chased.

**Alternatives rejected.** Letting the model decide who to chase: unauditable, more expensive,
and the wrong lesson for a beginner to take home.

See [the four jobs](../worker/the-four-jobs.md). Note that the demo clock deliberately does not
compress the escalation threshold, so a reader sees both a nudge and an escalation in one run;
see [DEMO_MODE compresses the clock](../worker/demo-mode-compresses-the-clock.md).
