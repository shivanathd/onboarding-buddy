---
type: Decision
title: "ADR-B6: a working status, edited into the answer"
description: The answer job posts a short status line immediately and replaces it with the answer, so the pause does not read as broken.
source: ["BUILD_DECISIONS.md ADR-B6 (private build log)", "jobs/answer.py", "tools/blocks.py thinking()", "README.md optional scope table"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, ux, scopes]
---
# ADR-B6: a working status, edited into the answer

**Context.** Answering takes a few seconds: a List read, a canvas read, a channel history read,
then one model call. On a projector that silence looks like a failure.

**Decision.** The answer job posts a short status line into the thread immediately, then replaces
it with the answer by updating the same message.

**Consequences.** A human can see the worker picked it up, with no new scope and no new
dependency.

This is deliberately not Slack's assistant thread feature. Doing that properly needs the
assistant scope and an assistant section in the manifest, which would change the exact scope set
one of the checks asserts, so it stays a decision for the spec owner rather than something the
build took unilaterally.

The optional native indicator is wired in behind a try, so if the workspace grants that scope the
worker uses the native indicator and skips the status message entirely, and if it does not, the
refusal costs nothing. The rehearsal confirmed the native indicator is accepted on an ordinary
channel thread, not only in the private assistant pane; see
[resolved unknowns](../rehearsal/resolved-unknowns.md).

See [the eight bot scopes](../setup/the-eight-bot-scopes.md).
