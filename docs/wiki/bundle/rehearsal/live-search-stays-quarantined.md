---
type: Concept
title: Live search stays quarantined
description: Whether live search answers for a custom app token is still unverified, so it lives behind one function that returns nothing.
source: ["tools/context.py search()", "spec DECISIONS.md ADR-7", "spec EVIDENCE.md E15"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [rehearsal, unverified, quarantine, architecture]
---
# Live search stays quarantined

The one unknown that running the worker did not settle: whether Slack's real time search answers
for a custom app token. It is still open.

Rather than guess, the code contains a single function that would be the search call, returns
nothing, and is called by nobody. Context assembly uses the documented channel history and thread
replies methods instead, under a scope the worker already holds.

## Why a stub is better than an absence

Three reasons, and they are the reusable part of this concept.

**The blast radius is written down.** The system map records that swapping search in touches
exactly one module. That claim is only credible because the seam already exists as a named
function; without it, the honest answer would be "we do not know yet".

**The decision is visible to the next reader.** A function with a comment saying which rehearsal
question would unblock it tells a reader that this was considered and deferred. An absence tells
them nothing, and the question gets rediscovered.

**Nothing depends on it.** A live demo has no single point of unverified failure. If the answer
had come back yes, the change would have been additive.

## The general pattern

An unverified capability gets a named seam, no callers, and a comment naming what would settle
it. That is cheaper than building on it and far cheaper than pretending the question was never
asked.

Related: [ADR-7](../decisions/spec-adr-7-thread-context.md),
[resolved unknowns](resolved-unknowns.md).
