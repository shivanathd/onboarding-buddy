---
type: Concept
title: The cast — every player on every surface, and which are real
description: "One table per surface naming every human, agent, app and record in the Session 5 demo, plus what each one actually is versus what the audience assumes."
source: ["s5demo org query of Opportunity/Contact/Job/Placement 2026-08-31", "slack-ug workspace member and app list", "Setup > Agentforce Agents screenshot 2026-08-31"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [cast, demo, teaching, slack, agentforce, salesforce]
---
# The cast

The demo has **four surfaces** and the same story runs across all of them. The single most
common way a talk like this loses a room is the audience not knowing who just spoke. This
page exists so every name on screen can be introduced in one sentence.

## The two things that actually do work

| On screen as | Really is | Runtime | Wrote it |
|---|---|---|---|
| **Polly PeopleOps** | An Agentforce agent, API name `Slack_Employee_Help`, carrying a grafted custom topic called `Deal_Desk_sug` | Salesforce, invoked from Slack | Configured, no code — see [Polly](polly-peopleops.md) |
| **onboarding-buddy** | A Python process on Railway: Socket Mode client + an MCP server | Railway container, `Asia/Dubai` | Hand-written, ~17 Python files |

That contrast **is the talk**. One agent was assembled from platform parts; one was built line
by line. They hand work to each other in a channel and neither knows what the other is made of.

## Every player, by surface

### Surface 1 — Salesforce (`s5demo` sandbox)

| Name | What it is | Role in the story |
|---|---|---|
| `Meridian Systems - Platform Expansion FY27` | Opportunity, 96,000, close 2026-09-30 | The deal. Everything hangs off this record. |
| `Meridian Systems` | Account | The client |
| **Priya Nair** | User, alias `s5ae`, profile *Demo AE* | Owns the deal. **Cannot read Amount** — the permissions story |
| **Anita Rao** | Contact, VP Engineering, Decision Maker, primary | Client-side decision maker |
| **David Mensah** | Contact, CFO, Economic Buyer | Client-side money |
| **Priya Raman, Rahul Menon, Sara Okonkwo, Tom Whelan** | Contacts, "Senior … Consultant" | The four consultants being placed |
| `Meridian Platform Expansion - Senior Consultants` | `bpats__Job__c`, 4 openings / 4 filled | "A deal for four people" |
| 4 × `Meridian FY27 - <name>` | `bpats__Placement__c` | The roster the agent posts in Act 4 |
| **Polly PeopleOps** | Agentforce agent, Active v1 | Answers, drafts, writes, hands off |
| **Deal Desk Agent** | Agentforce agent, Active v1 | The CLI-built twin. **Never on screen** |
| **S5 Deal Desk** | Agent Script agent, Active **v5** | The tested fallback, 36/36 |

Note two names that are *not* players: **Greg Symons** and other colleagues appear as
`Last Modified By` on the inherited agents. They are clone residue from production, not
participants. Do not read them out.

### Surface 2 — Slack workspace `slack-ug` (Pro, standalone)

| Name | What it is | Role |
|---|---|---|
`#Meridian Systems - Platform Expansion FY27` | Channel `<your record channel>`, badged **Opportunity** | The stage. All five acts happen here |
| `#onboarding` | Channel `<a channel id>` | The worker's home channel |
| `#agent-handoff-test` | Channel `<a channel id>` | Scratch. Never open it on stage |
| **Shivanath Devinarayanan** | `YOUR_USER_ID` — the *only* human member | You. Also, awkwardly, the whole cohort — see [the one-member workspace](../gotchas/one-member-workspace.md) |
| **@onboarding-buddy** | Bot user `YOUR_WORKER_USER_ID`, app `<an app id>`, bot id `<a bot id>` | The worker |
| **@Polly PeopleOps** | Bot user `YOUR_AGENT_USER_ID`, bot id `<a bot id>` | The Agentforce agent, as Slack sees it |
| **Slackbot** | Slack's own assistant | Door two — calls the worker's MCP server |
| `Onboarding` List | Slack List `YOUR_LIST_ID`, 12 rows | The worker's memory |

### Surface 3 — Slack admin (`<your-workspace>.slack.com/admin/agentforce`)

Five agents from Salesforce org **Asymbl** sit in *Needs Review*. This is the install pipe,
and it is the reason Polly is on stage rather than an agent named after the demo. See
[Slack and Agentforce](../architecture/slack-and-agentforce.md).

### Surface 4 — Railway

One project, `onboarding-buddy`, one service, `worker`. Socket Mode out, `/mcp` in,
`/healthz` for the preflight.

## Who says what, in order

```
Act 1   you           walk the record tabs                       (no agent involved)
Act 2   you -> Polly  "what's the latest on Meridian?"           Polly answers PRIVATELY
Act 3   you -> Polly  "move it to Negotiation/Review"            Polly drafts, you confirm
Act 4   you -> Polly  "post the roster and ask @onboarding-buddy"
        Polly         posts a REAL channel message               <- the handoff
        buddy         reports the cohort, escalates one step
        you           approve
Act 5   buddy         posts completion, names Polly
        you  -> Polly "move it to Closed Won"                    <- a HUMAN, deliberately
```

The one line to land: **the worker never speaks to Polly.** It cannot. See
[how the two bots interact](../architecture/how-the-two-bots-interact.md).
