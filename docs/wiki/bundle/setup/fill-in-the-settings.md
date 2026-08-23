---
type: Process
title: Fill in the settings
description: Clone, create a virtual environment outside the repository, install three dependencies, and copy the settings template.
source: ["README.md 15 minute quickstart step 3", ".env.example", "requirements.txt", "spec REQUIREMENTS.md OPS-5, G-4"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [setup, configuration, dependencies]
---
# Fill in the settings

About three minutes.

```bash
git clone <the repository>
cd onboarding-buddy
python3 -m venv ../obb-venv && . ../obb-venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Note the `../` in the virtual environment path. Keep it outside the repository. Nothing breaks
if you put it inside, but the project's own checks walk every file in the tree, and a virtual
environment drags several thousand unrelated dependency files into that walk. See
[keep the virtual environment out of the repository](../gotchas/keep-the-virtual-environment-out-of-the-repo.md).

There are exactly three dependencies: the Slack Bolt framework, a scheduler, and the model SDK.
One of the checks asserts that count, which is what keeps the tree readable.

## What to fill in now

| Setting | Value |
| --- | --- |
| `SLACK_BOT_TOKEN` | the bot user token from the install page |
| `SLACK_APP_TOKEN` | the app level token carrying `connections:write` |
| `ANTHROPIC_API_KEY` | leave it empty to run on templates only; the worker still starts |
| `ANTHROPIC_MODEL` | the model name, so swapping the model is one line |
| `CHANNEL_ID` | the one channel you invited the bot to |
| `MANAGER_ID` | your own user id: who gets escalations and unowned rows |
| `CANVAS_FILE_ID` | optional; unset means the brief in the repository |
| `TZ` | an IANA name such as `Europe/London` |
| `DEMO_MODE` | `true` compresses the clock |

Leave `LIST_ID` and the six `COL_` settings empty. The next step prints them; see
[bootstrap the List](bootstrap-the-list.md).

## Two details that matter more than they look

The settings file is loaded by the code itself, so `python app.py` works with no shell
ceremony. A real environment variable always wins over the file, which is the correct
precedence for a hosted deploy. See [ADR-B1](../decisions/build-adr-b1-policy-loads-env.md).

An empty value counts as unset. A half filled settings file therefore cannot mask a genuinely
missing setting, and the worker refuses to start half configured, naming the settings that are
still empty.
