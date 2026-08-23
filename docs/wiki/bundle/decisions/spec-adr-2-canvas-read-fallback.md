---
type: Decision
title: "ADR-2: canvas read with a loud fallback"
description: The canvas brief is fetched through the unofficial download path, with a mandatory fallback to a file in the repository that logs itself.
source: ["spec DECISIONS.md ADR-2", "spec REQUIREMENTS.md", "spec EVIDENCE.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, spec, canvas, fallback]
---
# ADR-2: canvas read with a loud fallback

**Context.** There is no official method that returns canvas text. The canvas read scope
unlocks section lookup only, which returns identifiers rather than content.

**Decision.** The context module tries the file information call plus a private URL download with
the bot token. On any failure it falls back to the job description file in the repository and
logs a repo fallback line.

**Consequences.** The editable job description demo works when the unofficial path works, and
the worker never crashes when it does not. Whether the demo beat depending on it stayed in the
show was decided by one rehearsal check, which it passed.

**Alternatives rejected.**

- Depending on the download path silently: an unverified contract with no visible failure mode.
- Dropping the canvas story entirely: loses the point that a human can edit the brief.

See [canvas content has no read API](../gotchas/canvas-content-has-no-read-api.md) and
[ADR-B4](build-adr-b4-canvas-is-markup.md), which is what actually came back from that path.
