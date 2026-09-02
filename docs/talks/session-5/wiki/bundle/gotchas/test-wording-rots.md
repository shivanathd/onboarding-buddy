---
type: Decision
title: LLM-graded test expectations need maintaining like code
description: "An expectation phrased as a list becomes a whitelist; a relative date in an assertion goes degenerate; and a grader will pass an answer that contradicts a clause of its own expectation."
source: ["S5_Deal_Desk_Suite case 1 grader explanation scoring 2/5 for extra real fields 2026-08-31", "case 7 'end of next month' resolving to the stored CloseDate", "grader passing 'All 4 roles are filled' against an expectation saying 0 filled"]
verified: 2026-08-31
timestamp: 2026-08-31
tags: [testing, agentforce, llm-grading, maintenance]
---
# Test wording rots

Three separate times the **test** was wrong rather than the agent. Each is a general trap.

## An expectation phrased as a list becomes a whitelist

Expected: *"Summarises from real field values only: stage, close date, owner. Invents no
facts."*

The agent returned those three plus Name, Probability, Forecast Category, TCV, Last Modified
and both contact roles — all real, all correct, exactly what should happen on stage. The grader
scored it **2/5**:

> the response includes additional fields ... not requested in the expected response

The grader read the list as a **ceiling**. Rewritten to name the minimum and permit more:

> Must include at least stage, close date and owner, each matching the record. Additional real
> fields and a closing offer to help are acceptable. Fails only if a value is invented or
> contradicts the record.

## A relative date in an assertion goes degenerate

Utterance: *"Change the close date on Meridian to the end of next month."* Authored earlier in
the month, that was a real change. By 2026-08-31 the end of next month **was** the stored
`CloseDate` — so a correct draft became indistinguishable from a no-op, and the grader marked
it wrong either way.

Replaced with an absolute date. **And the expected action list had to move with it:** given an
absolute target the planner correctly dropped `get_record_details`, because it no longer needed
to read the current value.

```
expected: ['identify_record','get_record_details','extract_fields_and_values']
actual  : ['identify_record','extract_fields_and_values']
```

Changing the utterance changed the plan. Obvious in hindsight; not obvious while writing it.

## A grader will pass an answer that contradicts its own expectation

An expectation said "0 filled". The agent said *"All 4 roles are filled."* The grader
**passed** it. LLM graders judge overall alignment, not each clause — **an expectation is not a
schema.**

In that instance the agent was right and the seeded data was internally inconsistent. The
agent caught the data bug; the test did not. See
[seed the recruiting data](../setup/seed-the-recruiting-data.md).

## And read the result JSON carefully

Two wrong key guesses produced two wrong stories about the same green run:

| Assumed | Actually |
|---|---|
| `testCases[].expectationResults` | `testCases[].testResults` |
| `result == "Passed"` | `result == "PASS"` |

The first gave `0/0 passed, failures: none` — which reads like a clean run. **A counter that
reports 0/0 as success is worse than one that crashes.** Make an assertion counter fail loudly
when the denominator is zero.

Related: [two authoring lanes drift](two-authoring-lanes-drift.md).
