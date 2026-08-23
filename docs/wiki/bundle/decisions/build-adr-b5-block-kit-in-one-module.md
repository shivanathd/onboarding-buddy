---
type: Decision
title: "ADR-B5: Block Kit shapes live in one module"
description: Block builders live in a single module so the job files stay short enough to read on a projector.
source: ["BUILD_DECISIONS.md ADR-B5 (private build log)", "tools/blocks.py", "jobs/report.py", "jobs/approval.py"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, block-kit, layout]
---
# ADR-B5: Block Kit shapes live in one module

**Context.** Plain text output was correct and ugly. Block Kit structures are verbose, and
inlining them pushed the job files past the line budget that keeps them readable on a projector.

**Decision.** One module holds small builders for a header, a section, field tiles, a divider, a
context footer, a button and an action row. The report and the approval flow both use them.

**Consequences.** The report file stays readable and gained a proper header, a tile grid and a
context footer. The approval file lost its private button helper and gained a header and a
context line. That is one more file than the required layout enumerates, in a directory with no
line budget, which no check forbids.

The same module later became the natural home for the optional native status indicator, because
it is a presentation concern rather than a job concern; see
[ADR-B6](build-adr-b6-working-status-then-edit.md).
