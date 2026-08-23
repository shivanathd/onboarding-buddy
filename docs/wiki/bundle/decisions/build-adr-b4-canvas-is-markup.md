---
type: Decision
title: "ADR-B4: the canvas brief is markup, not markdown"
description: The unofficial canvas read works but returns document markup, so tags are stripped with the standard library and the repository fallback stays.
source: ["BUILD_DECISIONS.md ADR-B4 (private build log)", "tools/context.py", "docs/how-this-was-built.md", "spec DECISIONS.md ADR-2", "spec EVIDENCE.md E11"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, canvas, undocumented]
---
# ADR-B4: the canvas brief is markup, not markdown

**Context.** Provisioning proved the unofficial canvas read works: the file information call
plus a private URL download returns the brief. But it comes back as document markup, opening
with a container element, not as the markdown that was written in.

**Decision.** The context module strips tags with the standard library, and falls back to the job
description file in the repository on any failure, exactly as the spec ADR requires.

**Consequences.** The rehearsal question about this path was answered ahead of the rehearsal, and
the demo beat that depends on it survived. The warning that the format varies by canvas
generation is now concrete rather than theoretical for this workspace, so the strip step has to
stay defensive: keep the text, drop the tags, newline at the end of a block.

See [canvas content has no read API](../gotchas/canvas-content-has-no-read-api.md).
