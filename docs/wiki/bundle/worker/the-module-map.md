---
type: Reference
title: The module map
description: Every file in the repository and the one thing it is responsible for.
source: ["README.md", "spec REQUIREMENTS.md OPS-1", "spec SYSTEM_MAP.yaml"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [architecture, layout, reference]
---
# The module map

The repository is small on purpose. The selling point is that a stranger can read the whole
tree in one sitting, so every file has exactly one responsibility.

| Path | Responsibility |
| --- | --- |
| `app.py` | three listeners, two clock lines, one socket. No logic. |
| `policy.py` | every number the worker uses to decide something, plus every setting it reads |
| `agent.py` | the model, behind one function. The smallest file here. |
| `bootstrap.py` | create the List, seed it, print the column mapping. Run once. |
| `jobs/answer.py` | reply in a thread, grounded in the List |
| `jobs/advance.py` | a tick reaction flips a row to Done |
| `jobs/chase.py` | the clock owning scan for rows past their grace window |
| `jobs/report.py` | Monday cohort counts |
| `jobs/approval.py` | the escalation draft, the two buttons, and the click handlers |
| `tools/lists.py` | the only crosser of the Lists boundary |
| `tools/context.py` | the List, then the brief, then the conversation |
| `tools/blocks.py` | Block Kit shapes and the status indicator |
| `seed/onboarding.csv` | a generic starter cohort, no real names |
| `seed/job-description.md` | the brief used when the canvas cannot be read |
| `manifest.json` | the app definition and its bot scopes |
| `railway.json` | builder and start command for the hosted path |

Three boundaries are worth naming, because they are where a change stops:

- **The Lists boundary.** No job file calls a Lists method directly. If Slack changes a
  shape, one file changes. See [the dotted adapter](../decisions/build-adr-b2-dotted-lists-adapter.md).
- **The model boundary.** One function, `agent.ask`, is the only place a model is called.
  Swapping the model is one line in the settings file.
- **The configuration boundary.** Nothing outside `policy.py` reads the environment.

Two prose companions to this knowledge base live in the same repository:
`docs/how-this-was-built.md` covers the method, and
`docs/provisioning-without-a-browser.md` covers the headless setup path.
