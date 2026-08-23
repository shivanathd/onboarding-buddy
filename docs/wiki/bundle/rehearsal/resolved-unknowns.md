---
type: Concept
title: Resolved unknowns
description: Five of six behaviours the spec marked unverified were settled by running the worker against a live workspace.
source: ["docs/how-this-was-built.md rehearsal table", "spec EVIDENCE.md E5, E6, E11, E12, E15", "PROGRESS.md holdout results (private build log)", "git log e523259"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [rehearsal, unverified, live-testing]
---
# Resolved unknowns

Where no primary source answered a question, the spec marked the behaviour unverified and routed
it to a live rehearsal rather than guessing. Six behaviours were marked that way. Five are now
answered.

| Question | Answer |
| --- | --- |
| Does a reaction on the app's own message raise an event? | **Yes.** Proven end to end. |
| Can a background scheduler and a socket connection share one process? | **Yes**, on a laptop and hosted. |
| Can a canvas be read with a bot token? | **Yes**, as markup, with a fallback in place. |
| Does a mention inside a thread carry the thread id? | **Yes.** Follow up questions work in the same thread. |
| Is the native thinking status accepted on an ordinary channel thread? | **Yes**, not only in the private assistant pane. |
| Is live search available to a custom app token? | **Still open.** Quarantined behind one function. |

## The first one mattered most

The entire completion flow depends on a person reacting to a message the worker itself posted,
and no document says whether that raises an event. If it did not, the whole design would have
needed rebuilding around a different trigger. It does.

That is the shape of a genuinely load bearing unknown: not an inconvenience, but a fact the
architecture rests on, which no amount of documentation reading would settle. Naming it up front
and routing it to a live check is the only honest way through.

## The others

The scheduler and socket coexistence question was the difference between one process and two. It
coexists, so the worker is one process with two clock lines.

The canvas read works, but it returns markup rather than the markdown that went in, which is a
qualified yes rather than a clean one and is why the fallback stayed mandatory. See
[canvas content has no read API](../gotchas/canvas-content-has-no-read-api.md).

The threaded mention carrying a thread id means a follow up question inside an existing thread is
answered in that thread rather than starting a new one. Both paths were coded before the answer
arrived, so the answer removed a branch rather than requiring one.

The native thinking indicator turned out to be accepted on an ordinary channel thread, which is
what makes it a free upgrade behind an optional scope rather than a feature requiring a different
kind of app. See [ADR-B6](../decisions/build-adr-b6-working-status-then-edit.md).

One earlier rehearsal question, whether the original message can be reliably updated after a
button click over a socket connection, needed a human click and is answered in practice by the
holdout run that clicked it.

The remaining open one is [live search](live-search-stays-quarantined.md).
