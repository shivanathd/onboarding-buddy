---
type: Decision
title: "ADR-B3: the approval flow gets its own file"
description: The escalation draft, the buttons and the click handlers live in their own file, one more than the required layout enumerates.
source: ["BUILD_DECISIONS.md ADR-B3 (private build log)", "jobs/approval.py", "spec SYSTEM_MAP.yaml approval_handlers", "spec REQUIREMENTS.md CHS-4, OPS-1"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, layout, approval]
---
# ADR-B3: the approval flow gets its own file

**Context.** The required layout enumerates four job files. But the system map lists the
approval handlers as their own component, the clock job is required to route to it rather than
duplicate posting logic, and the approval check scans the entry point plus every job file for the
approve and stand down vocabulary.

**Decision.** One file holds the escalation draft, the buttons, and the click handlers. The entry
point registers the listener and acknowledges first, then delegates.

**Consequences.** The clock job stays under its line budget and stays readable as a pure scan.
The file count grows by one beyond the enumerated layout, which no check forbids. Noted for the
spec owner as a small gap.

See [the four jobs](../worker/the-four-jobs.md).
