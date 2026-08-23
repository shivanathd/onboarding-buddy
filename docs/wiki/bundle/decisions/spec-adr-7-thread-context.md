---
type: Decision
title: "ADR-7: thread context from documented methods, live search quarantined"
description: Context assembly uses documented conversation reads only; live search stays behind one function until it is verified.
source: ["spec DECISIONS.md ADR-7", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, context, unverified]
---
# ADR-7: thread context from documented methods, live search quarantined

**Context.** Whether live search answers for a custom app token was unverified when the spec
was written, and still is.

**Decision.** Context assembly uses the documented channel history and thread replies methods,
under the channel history scope. Any live search usage waits for a rehearsal answer and would
swap in behind the same single function.

**Consequences.** The spec ships on documented scopes only, and there is no single point of
unverified failure in a live demo. The quarantine is one function in one file, so the blast
radius of swapping it in later is that file and nothing else.

**Alternatives rejected.** Building on live search now: betting a live demo on an unverified
contract.

See [live search stays quarantined](../rehearsal/live-search-stays-quarantined.md).
