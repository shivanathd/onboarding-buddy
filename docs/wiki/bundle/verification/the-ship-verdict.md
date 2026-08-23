---
type: Event
title: The SHIP verdict
description: The convergence report of 2026-08-23 recorded fifteen results, thirteen passing and two skipped live gates, and a SHIP verdict.
source: ["spec evals/results/convergence-report.json", "PROGRESS.md holdout results (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [evals, verification, milestone]
---
# The SHIP verdict

The convergence report generated on 2026-08-23 recorded fifteen results and a verdict of SHIP.

| Layer | Result |
| --- | --- |
| task checks, offline | 5 PASS: layout, policy, manifest, README, branches |
| task checks, live | 2 SKIPPED, gated behind an explicit live flag |
| acceptance checks | 8 PASS, across the Lists module, context, the model gateway, and all five job files |

Every failure count in the report was zero.

The two skipped entries are the live gates: one creates a real List, one boots the real worker.
They are opt in because they cost a real workspace and real API calls, and both had already been
run and passed separately.

The holdout layer is recorded separately. Five of six scenarios ran, four passed outright, and
one was blocked by a defect in its own assertion rather than by the worker; see
[the H3 spec defect](spec-defect-h3-reads-the-wrong-surface.md). The sixth is the human timed
quickstart.

## What the verdict does not mean

The suite was fully green on 2026-08-23 and six real defects were found anyway, four before the
verdict and two after it, by running the worker and reading its output carefully. A green board
is not proof. It is the floor. See
[defects a green suite missed](defects-a-green-suite-missed.md).
