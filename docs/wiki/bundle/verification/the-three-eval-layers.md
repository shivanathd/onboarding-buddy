---
type: Process
title: The three eval layers
description: Task checks on structure, acceptance checks on behaviour, and holdout scenarios the implementer never designed against.
source: ["spec evals/eval-manifest.json", "spec README.md", "spec SCENARIOS.md", "docs/how-this-was-built.md"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [evals, verification, method]
---
# The three eval layers

Nothing was committed until its check passed, and the checks existed before the implementation
did. There are three layers, and the separation between them is the part worth copying.

## Task checks, seven of them

Shell scripts asserting structure and configuration: the required file layout, exactly three
dependencies, no container file, the hosting config fields, the manifest's Socket Mode and
interactivity flags and its exact scope sets, the README's required topics and documented
settings, and the two branches. Two of them are live and only run when explicitly enabled: one
creates a real List, one boots the real worker.

One of these deserves singling out because it shapes everything else in the repository: the
README check walks every Python, markdown, text, JSON, shell and CSV file in the tree and fails
the build on a prohibited dash character. It is why
[the virtual environment stays outside the repository](../gotchas/keep-the-virtual-environment-out-of-the-repo.md),
and why this knowledge base is written the way it is.

## Acceptance checks, eight of them

Unit checks on behaviour with fake Slack data: the cell shapes and pagination, the canvas
fallback and the ordered context assembly, model selection and template behaviour when the model
raises, threaded answers and redirect behaviour, reaction filtering and List backed completion,
pure detection and thread cell deduplication, report counts and the empty state, and the
acknowledge first ordering with the single open approval guard.

## Holdout scenarios, six of them

Validation the implementer does not design against, run end to end against a throwaway app in a
real workspace after every implementation task passes. That role separation is the point: a check
you wrote to make your own code pass proves less than one written from the requirement.

| Scenario | What it proves | Result |
| --- | --- | --- |
| H1 full loop | bootstrap, chase, human tick, row flips, report | PASS |
| H2 amnesia | killed mid shift, restarted, no duplicate threads | PASS |
| H3 brain dark | the worker survives an invalid model key | blocked by a spec defect, behaviour verified by hand |
| H4 wrong inputs | redirect, silent stray reaction, null cell warnings | PASS |
| H5 canvas gone | the repository fallback works at boot and in an answer | PASS |
| H6 quickstart | a stranger gets to a live worker inside fifteen minutes | human only, not run |

H6 stays human on purpose. It cannot be scripted honestly, because the thing being measured is
whether a person can follow the README without outside knowledge.

Related: [the SHIP verdict](the-ship-verdict.md),
[defects a green suite missed](defects-a-green-suite-missed.md),
[GNU timeout is not on macOS](../gotchas/gnu-timeout-is-not-on-macos.md).
