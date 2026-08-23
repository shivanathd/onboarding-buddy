---
type: Concept
title: GNU timeout is not on macOS
description: A boot eval calls timeout, which macOS does not ship, so the check fails on the developer machine for reasons unrelated to the code.
source: ["spec evals/tasks/t13_boot.sh line 15", "observed while running the eval suite on macOS, 2026-08-23"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [evals, macos, tooling]
---
# GNU timeout is not on macOS

The boot check starts the worker under a wall clock limit:

```bash
timeout 30s python3 "$repo/app.py" >"$log" 2>&1
```

`timeout` is GNU coreutils. macOS does not ship it, so on a developer machine that line fails
with a command not found and the check reports a failure that has nothing to do with the worker.

Three ways out, in the order worth trying:

1. Install coreutils and use the prefixed name it provides, or put its unprefixed binaries on
   the path for the run.
2. Have the script prefer whichever of the two names exists.
3. Replace the guard with a shell background job plus a sleep and a kill, which is portable but
   noisier to read.

The wider point is worth keeping. An eval suite is code, and it carries platform assumptions
exactly like the code under test does. A check that only runs on one operating system is a
check that will one day report a red board for the wrong reason, and the cost is measured in the
time spent believing it.

Related: [the three eval layers](../verification/the-three-eval-layers.md),
[keep the virtual environment out of the repository](keep-the-virtual-environment-out-of-the-repo.md).
