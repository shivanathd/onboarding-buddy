---
type: Concept
title: Keep the virtual environment out of the repository
description: One check walks every file in the tree, so a virtual environment inside the repository drags thousands of dependency files into the scan.
source: ["README.md 15 minute quickstart step 3", "spec evals/tasks/t14_readme.sh", "PROGRESS.md workspace layout (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [tooling, evals, repo-hygiene]
---
# Keep the virtual environment out of the repository

Create the virtual environment beside the repository, not inside it:

```bash
python3 -m venv ../obb-venv && . ../obb-venv/bin/activate
```

Nothing breaks functionally if you put it inside. The problem is that one of the project's own
checks walks every file in the tree with a Python, markdown, text, JSON, shell or CSV extension
and asserts a prose rule on each one. A virtual environment pulls several thousand dependency
files into that walk, and every one of them is third party prose the rule was never meant to
police. The check becomes slow, then it fails on something you do not own, and the honest
signal is buried.

The same reasoning is why the build tracker for this project lives outside the repository
entirely, and why the test runner lives in a virtual environment one directory up. The repository
is the artefact a stranger reads; anything that is process rather than product stays out of it.

The general form: if your quality gate walks the whole tree, the tree has to contain only things
you are prepared to be judged on. That is a constraint on layout, not on the gate.

Related: [GNU timeout is not on macOS](gnu-timeout-is-not-on-macos.md),
[the three eval layers](../verification/the-three-eval-layers.md).
