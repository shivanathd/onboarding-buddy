---
type: Process
title: Seed the recruiting data — Opportunity, Job, Placements
description: "The only join path from a deal to the people being placed, the trigger-heavy objects to insert carefully, and the internal consistency the agent will notice if you get it wrong."
source: ["bpats package describe of bpats__Job__c and bpats__Placement__c in s5demo", "insert of 1 Job + 4 Placements 2026-08-31", "agent answer 'All 4 roles are filled' vs Openings_Filled__c = 0"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [salesforce, data, recruiting, bpats, setup]
---
# Seed the recruiting data

For a staffing story, a deal is a deal *for N people*. That has to be modelled, and the model
is not where you would guess.

## The only path

```
Opportunity
   │  bpats__Job__c.bpats__Opportunity__c        <- the ONLY Opportunity link in the package
   ▼
bpats__Job__c
   │  bpats__Number_of_Openings__c   = 4         <- "a deal for four people"
   │  bpats__Openings_Filled__c      = 4
   │  bpats__Status__c = Open,  bpats__Type__c = Consulting
   ▼
bpats__Placement__c  × 4
      bpats__ATS_Job__c        -> the Job         <- deal-scoped path
      bpats__ATS_Candidate__c  -> a Contact
      bpats__Account__c, start/end date, bill/pay rate
      bpats__Placement_Complete__c (bool)         <- there is no Status picklist
```

There is **no Opportunity lookup on `bpats__Placement__c`** and **no headcount field on
Opportunity**. Do not create either — the Job is the join, and teaching the agent that path is
what makes it answer correctly.

The deal-scoped query, used by both the agent and the preflight:

```sql
SELECT Id, Name, bpats__ATS_Candidate__r.Name
FROM   bpats__Placement__c
WHERE  bpats__ATS_Job__r.bpats__Opportunity__c = :oppId
```

If that count comes back right by a *shorter* path, the query is wrong — it is counting
placements that do not belong to this deal.

## Insert one of each first, then read the error

These are the trigger-heaviest objects in the package:

| Object | Carries |
|---|---|
| `bpats__Job__c` | 6 active Apex triggers, 2 record-triggered flows, 2 validation rules |
| `bpats__Placement__c` | 3 active Apex triggers, one reaching into `ASYMBL_Time` on **before insert**, one publishing `Placement_Sync__e` platform events |

Both inserted clean, but the order was the safe one: **one Job, read the result, then one
Placement, read the result, then the rest.** Leaving the posting fields blank avoids the
`Posting_End_Date_Must_Be_Future` validation rule.

`Opportunity` itself is wide open in this org — 0 active validation rules, 0 triggers, 0
record-triggered flows — so the stage writes are safe.

## Keep the data internally consistent, because the agent checks

Seeded with `Number_of_Openings__c = 4` and `Openings_Filled__c = 0`, the agent answered:

> "The Meridian deal is for 4 consultants. **All 4 roles are filled.**"

It was right and the data was wrong: four Placement records exist, and they *are* the roster,
so `filled = 0` contradicted them. Set it to 4.

Two lessons worth more than the fix:

- **An agent reading your data will notice incoherence you introduced.** That is a feature.
- The LLM grader **passed** that answer despite the test expectation saying "0 filled".
  Graders judge overall alignment, not each clause. See
  [test wording rots](../gotchas/test-wording-rots.md).

## A CLI gotcha

`sf data update record --where "Name like '...'"` fails with
`Malformed key=value pair for value: Name.` Query the Id and use `--record-id`.

Related: [Salesforce and Agentforce](../architecture/salesforce-and-agentforce.md),
[the worker and the List](the-worker-and-the-list.md).
