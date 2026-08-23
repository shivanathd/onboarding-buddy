---
type: Concept
title: Any fallback without a log line gets debugged twice
description: A fallback that fires correctly and says nothing is indistinguishable from the happy path, so every fallback in this worker announces itself.
source: ["docs/how-this-was-built.md", "agent.py", "tools/context.py brief()", "BUILD_DECISIONS.md ADR-B7 (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [logging, fallback, observability]
---
# Any fallback without a log line gets debugged twice

This is a rule extracted from a specific failure, and it generalises further than the failure
did.

The model call fell back to a template exactly as designed, and said nothing about it, because
the trigger was an empty success rather than an exception. Nothing was wrong from the code's
point of view. From a human's point of view, the worker was quietly using a template while
holding a valid key, and there was no way to tell by looking at the output. The same
investigation therefore happened twice.

A fallback path worth having is worth a log line. In this worker every one of them announces
itself:

| Fallback | What it says |
| --- | --- |
| the brief cannot be read from the canvas | `brief: repo fallback` plus the reason |
| no canvas identifier is set at all | `brief: repo fallback, no canvas file id is set` |
| the model call raised | `brain: <the error>. Falling back to a template.` |
| the model call succeeded with no text | `brain: a successful call carried no text, stop reason <reason>` |
| channel history or a thread is unavailable | one line naming which read failed |

Note the two separate model lines. An exception and an empty success are different failures with
the same visible outcome, and telling them apart in the log is the whole point.

Log lines here are treated as a teaching surface rather than as debug output: human sentences,
readable at projector font, one per shift for the clock job. That is also why the boot log
states the timezone and which clock is running instead of leaving it to be assumed.

Related: [thinking shares the token budget](thinking-shares-the-token-budget.md),
[canvas content has no read API](canvas-content-has-no-read-api.md).
