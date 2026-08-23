---
type: Concept
title: DEMO_MODE compresses the clock
description: A demo switch that changes exactly three things, and deliberately does not compress the escalation threshold.
source: ["README.md", "policy.py", "spec REQUIREMENTS.md OPS-6", "PROGRESS.md bugs the live runs found (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [configuration, demo, clock]
---
# DEMO_MODE compresses the clock

Nobody wants to wait until 9am to watch a clock fire. Setting `DEMO_MODE=true` does exactly
three things, all of them read from `policy.py`:

1. grace windows shrink from days to minutes
2. Chase runs every 60 seconds instead of on its daily cron
3. Report runs on demand when a mention contains "run report"

The real cron lines stay visible in `app.py`, directly above the compressed override, so a
reader can see both clocks at once.

## What it deliberately does not compress

The escalation threshold. This is the interesting part, and it was a real defect before it was
a rule: an early version compressed the escalation threshold and the extension days too. With
a short threshold, every row that was a day overdue jumped straight to escalation, so the
ordinary nudge never appeared at all. Every test still passed, because no test asserted that a
nudge and an escalation could both happen in the same run. See
[defects a green suite missed](../verification/defects-a-green-suite-missed.md).

The boot log prints which clock is running, in one line, on every start. Believe the log rather
than your assumption; the same applies to the timezone, which a container reports as UTC unless
`TZ` is set.
