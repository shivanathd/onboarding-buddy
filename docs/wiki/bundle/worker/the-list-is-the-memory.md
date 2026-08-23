---
type: Concept
title: The List is the memory
description: All durable state lives in one Slack List, so the process can be killed at any moment without losing anything.
source: ["README.md", "spec DECISIONS.md ADR-4", "spec SCENARIOS.md H2", "spec SYSTEM_MAP.yaml state block"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [architecture, state, slack-lists]
---
# The List is the memory

There is no database, no queue, no cache and no vector store. One Slack List holds every
durable fact the worker owns, across six columns:

| Column | Type | What it holds |
| --- | --- | --- |
| Step | text, primary | what has to happen |
| New hire | user | who it is for |
| Owner | user | who owes it |
| Due | date | when it was due |
| Status | select: Open, Done, Escalated | where it stands |
| Thread | text | the id of the message the worker opened about this row |

The Thread column is the load bearing one. It is how the loop closes: Chase writes the id of
the message it posted into that cell, and later a tick reaction on that same message finds its
way back to this row. It is also the only record that a row has already been chased, which is
why nothing needs to survive in process memory between shifts.

Two consequences follow. First, killing the worker mid shift and restarting it is a feature
rather than a risk, which is what holdout H2 proves. Second, a beginner can inspect everything
the worker knows in the ordinary Slack interface, with no admin tooling and no query language.

Exactly one column may be the primary column and it must be a text column. That is a Slack
constraint, not a choice, and it cannot be reassigned later.

Related: [the four jobs](the-four-jobs.md), [a List is a file](../gotchas/a-list-is-a-file.md),
[ADR-4](../decisions/spec-adr-4-the-list-is-the-state.md).
