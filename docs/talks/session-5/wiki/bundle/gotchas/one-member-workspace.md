---
type: Decision
title: A one-member workspace collapses every person column onto you
description: "Why the cohort reports '1 new hire' for four consultants, why the permissions beat cannot run through Slack, and how to say both without losing the room."
source: ["get_onboarding_summary output '1 new hires' 2026-08-31", "slack-ug member list: one human", "FieldPermissions showing the Slack-mapped user is the s5demo System Administrator"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [slack, demo-limitation, permissions, honesty]
---
# A one-member workspace collapses every person column

`slack-ug` has exactly one human member. Two demo beats bend around that, and both are better
handled by saying so than by hoping nobody notices.

## The cohort says "1 new hire" for four consultants

The List's `New hire` column is a Slack **person** column, so all twelve rows resolve to the
same single member. `get_onboarding_summary` answers *"1 new hires"*, and the report's
*By person* section shows one member with 12 open, 5 late.

**Fixed properly, in both readers.** Each step's *text* names its consultant
(`Sara Okonkwo — Access badge`), because a person column cannot hold someone with no Slack
account. So both code paths now key their aggregation on the name parsed out of that text,
falling back to the person column when a step carries no name:

| | Before | After |
|---|---|---|
| `jobs/report.py` — the *By person* card section | `@Shivanath 12 open, 5 late` | four consultants, 3 open each |
| `mcp_server/hires.py` — `get_onboarding_summary` | *"1 new hires"* | *"4 new hires"* |
| `mcp_server/hires.py` — `list_new_hires` | one row | four, with their own step counts |
| `mcp_server/hires.py` — `get_onboarding_status` | name not found | actually finds Priya Raman |

The report card was the visible one: it listed four named consultants line by line and then said
`@Shivanath Devinarayanan 12 open, 5 late` underneath them, which is the first thing anyone asks
about. Fixing both keeps the two doors reading the List the same way, which is the property
`tools/lists.py` exists to preserve.

**What is still true and worth saying:** the workspace has one human, so any *person* column
still resolves to that one account. The fix moves the aggregation off that column rather than
inventing members.

## The permissions beat cannot run through Slack

The single member maps to the s5demo **System Administrator**, who *can* read `Amount`. An
Agentforce agent runs every action in the invoking user's security context, so through Slack
the agent will always see everything. There is no way to stage the "Priya asks and gets no
Amount" contrast in this workspace.

**Tell it from Setup instead** — Profiles → Demo AE → Field-Level Security → Opportunity →
`Amount`, unchecked. Verified, static, and it cannot fail live. It is also more convincing than
a chat bubble.

Login-As Priya works into Classic but the Lightning domain dropped back to the admin session,
so treat Login-As as **unverified** and keep it out of the critical path.

## The general point worth making out loud

A demo workspace with one human is a demo workspace with one identity, and identity is what
every permission story is actually about. Naming that limitation costs thirty seconds and buys
the audience's trust for the parts that *are* real.

Related: [the worker and the List](../setup/the-worker-and-the-list.md),
[Salesforce and Agentforce](../architecture/salesforce-and-agentforce.md).
