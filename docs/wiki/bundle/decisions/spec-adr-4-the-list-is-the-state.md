---
type: Decision
title: "ADR-4: no vector memory, the List is the state"
description: All durable state lives in the Slack List; the process holds nothing that matters, so a restart is a feature.
source: ["spec DECISIONS.md ADR-4", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, state, architecture]
---
# ADR-4: no vector memory, the List is the state

**Context.** The thesis being tested is that ordinary Slack primitives are enough for this
class of worker.

**Decision.** All durable state lives in the List: rows, Status, and the message id in the Thread
cell. Threads carry conversational context. The process holds nothing that matters.

**Consequences.** Killing and restarting the worker is a demo feature rather than a risk, and a
beginner can inspect every piece of state in the ordinary Slack interface. It also means the
dedupe guard is a cell, not a variable, which is what makes it survive a restart.

**Alternatives rejected.**

- A local database: invisible state, which defeats the point.
- A vector store: it would break the three dependency limit, and nothing here needs similarity
  search.

See [the List is the memory](../worker/the-list-is-the-memory.md).
