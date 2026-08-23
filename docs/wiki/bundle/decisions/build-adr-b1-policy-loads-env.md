---
type: Decision
title: "ADR-B1: the settings file is loaded by the code"
description: The configuration module reads the settings file itself, because the dependency limit rules out a loader library and two live checks run the scripts bare.
source: ["BUILD_DECISIONS.md ADR-B1 (private build log)", "policy.py", "spec evals/tasks/t13_boot.sh", "spec evals/tasks/t6_bootstrap_live.sh"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, configuration, evals]
---
# ADR-B1: the settings file is loaded by the code

**Context.** The three dependency limit rules out a settings loader library. But the boot check
runs the app bare and the bootstrap check runs the bootstrap script bare, neither sourcing
anything first. With no loader, no token ever reaches the process and both live gates are
unpassable.

**Decision.** The configuration module reads a settings file sitting next to it and fills the
environment, using a set default so an existing value is never overwritten, and skipping empty
values.

**Consequences.** `python app.py` works with no shell ceremony, which protects the fifteen
minute quickstart for a beginner. Real environment variables win, so hosting dashboard values
override the file, which is the correct precedence.

Skipping empty values is not a detail. One live check runs with a specific setting unset on
purpose, and a loader that repopulated it from a filled file would trip the worker's own refusal
to start half configured and fail the check.

**Rejected.** Telling the reader to export the file in their shell first: adds a concept to the
quickstart, and cannot make the live checks pass.

See [fill in the settings](../setup/fill-in-the-settings.md).
