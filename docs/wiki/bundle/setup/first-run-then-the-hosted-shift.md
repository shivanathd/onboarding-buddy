---
type: Process
title: First run, then the hosted shift
description: Start the worker locally, confirm the boot log, then move the shift to a hosted service with the same folder and no code change.
source: ["README.md quickstart step 5 and the deploy section", "app.py", "railway.json", "PROGRESS.md Railway section (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, deploy, operations]
---
# First run, then the hosted shift

About one minute locally.

```bash
python app.py
```

You should see two lines: one naming the timezone and the clock that is running, and one saying
`worker on shift`. Mention the worker in your channel and it answers in the thread.

If the worker refuses to start, it prints the settings that are still empty and exits. It never
starts half configured.

## The hosted path

Same folder, same code, no changes. The laptop is where you learn; when the worker earns a real
shift, host it, because a sleeping laptop is a sleeping worker.

Set the same settings in the hosting dashboard rather than in a file. The repository's
`railway.json` sets only the builder and the start command, and deliberately carries no
variables at all: configuration defined in code overrides the dashboard, and tokens do not
belong in git.

Socket Mode means there is no public URL, no request signing and no ingress to configure.

## Two operational rules

**Set the timezone or read the boot log.** A container runs in UTC. A 9am cron in the wrong
timezone is the first thing that surprises people, so set `TZ` to an IANA name. The worker
prints the timezone it is actually using on every boot.

**One worker on shift.** Stop the local worker before starting the hosted one. Slack load
balances events across connections rather than duplicating them, so two connected copies each
receive a random half of the events and the worker looks broken in a way that is very hard to
debug. See [events are load balanced](../gotchas/events-are-load-balanced-not-duplicated.md).

Boot log parity is the check worth running once: the hosted lines should be identical to the
laptop lines. In the recorded deploy they were.
