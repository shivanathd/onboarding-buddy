---
type: Decision
title: "ADR-B2: a dotted adapter over the Lists SDK"
description: A small adapter presents the dotted API shape over the SDK's underscored method names, because the eval and the SDK disagree.
source: ["BUILD_DECISIONS.md ADR-B2 (private build log)", "tools/lists.py", "spec evals/acceptance/test_lists_unit.py"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, slack-lists, sdk]
---
# ADR-B2: a dotted adapter over the Lists SDK

**Context.** The unit check fakes the Lists client with attribute chaining, the way the API
reference reads. The SDK actually exposes the same methods with underscores. The check and the
SDK disagree, and both are legitimate.

**Decision.** One small adapter presents the dotted shape over the SDK's underscored methods,
and every Lists call goes through it.

**Consequences.** The code reads like the API reference, which is a teaching win, and it honours
the contract that one file is the only crosser of the Lists boundary. If Slack renames a method,
one file changes.

This was reported to the human as a spec defect rather than silently weakening the check, which
is the behaviour the goal contract required.

**Rejected.** Calling the generic API method by name, which would work in production and fail
against the check's fake.

See [the module map](../worker/the-module-map.md).
