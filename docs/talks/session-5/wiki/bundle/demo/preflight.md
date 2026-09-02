---
type: Process
title: Preflight — 28 automated checks, and the four that stay manual
description: "What a machine can assert before the talk, grouped by the act it protects, plus the checks that cannot be automated and why."
source: ["s5-preflight.sh run 2026-08-31, 28 passed 0 failed", "SF_AUTOUPDATE_DISABLE fix after every JSON parse broke", "Slack conversations.members returning missing_scope"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [preflight, demo, verification, automation]
---
# Preflight

```bash
set -a; . ~/.s5/slack-ug.env; set +a
bash <pack>/s5-preflight.sh
```

**28 passed, 0 failed.** Exit 0 means every automated check passed. Anything red is a
*decision*, not a repair job — map it to that act's fallback and keep moving. Do not start
fixing Salesforce config half an hour before a talk.

## What it checks, by act

| Act | Checks |
|---|---|
| 1 | stage parked at `Proposal/Price Quote`; Amount present; close date 2026-09-30; owned by the AE |
| 2 | all three agents Active at the right version, each labelled with its role; Testing Center suite present |
| 3 | 0 active Opportunity flows / validation rules / Apex triggers — nothing will surprise the stage write |
| 4 | exactly 1 Job on the deal; 4 openings; 4 filled; status Open; **4 Placements deal-scoped via the Job path**; 4 consultant Contacts; worker `/healthz` 200; `/mcp` refusing unsigned callers with 401 |
| 5 | the manager can read Amount; the AE has no Amount permission at all; no Amount-granting permission set on the AE |
| Slack | `CHANNEL_ID` includes the record channel; buddy reachable *in* it; List has 12 rows; List names 4 consultants; **Polly is in the record channel**; worker on shift |

## Two lessons baked into the script

**`sf` writes its update warning to STDOUT, ahead of the JSON.** Every `--json` parse broke at
once with `JSONDecodeError: Expecting value: line 1 column 2` the moment a newer CLI shipped.
`2>/dev/null` does not help and `--json` does not suppress it. Two defences, deliberately
belt-and-braces:

```bash
export SF_AUTOUPDATE_DISABLE=true          # stop it being emitted
sfq(){ sf data query ... --json 2>/dev/null | sed -n '/^{/,$p'; }   # strip it anyway
```

**A check that fails on healthy state is worse than no check.** `railway logs | tail -60 |
grep "worker on shift"` failed on a perfectly fine worker: the banner prints once at startup,
so it scrolls out of any fixed window as uptime grows. Now it greps the whole buffer, falls
back to `Bolt app is running`, and falls back again to "logs are flowing at all" — because
`healthz 200` two checks earlier is already the live liveness proof.

**Polly's channel membership needed a workaround.** `conversations.members` is the right call
but returns `missing_scope` — the app has `channels:history`, not `channels:read`. Membership
is derived from `channel_join` / `channel_leave` subtypes in history, newest-first, with an
explicit `unknown` outcome rather than a false pass.

## What stays manual, and why

| Manual check | Why a machine cannot do it |
|---|---|
| The record tab strip renders, and every tab is **synced** | Slack List sync is a UI action with no API; the tabs render empty until clicked |
| The agent resolves in the record channel | its answer is ephemeral and absent from the API |
| Slack admin shows Polly **installed**, not just "Updated" | no API for the Agentforce admin queue |
| Login-As Priya in **Lightning** | works into Classic; the Lightning domain dropped back to admin. Unverified — route around it via the FLS page |

Related: [the five acts](the-five-acts.md), [reset after the demo](reset-after-the-demo.md).
