---
type: Concept
title: The four jobs
description: Answer, Advance, Chase and Report are four generic verbs any List-backed process can reuse.
source: ["README.md", "jobs/answer.py", "jobs/advance.py", "jobs/chase.py", "jobs/report.py", "spec REQUIREMENTS.md F2 to F6"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [architecture, jobs, slack]
---
# The four jobs

The worker does four things, and nothing else. Each job is one file, each file opens with the
same five line header (trigger, reads, writes, surface, whether it uses the model), and the
whole set is readable in one sitting.

| Job | Trigger | Reads | Writes | Model |
| --- | --- | --- | --- | --- |
| Answer | a mention in the one channel it knows | the List, the brief, recent conversation | nothing | yes, with a template fallback |
| Advance | a tick reaction in that channel | the List, matching the reacted message against the Thread cell | Status becomes Done | yes, for one sentence |
| Chase | a clock it owns | the List: Status, Due, Thread | the chase message id into the Thread cell | no for detection, yes only to draft an escalation |
| Report | Monday morning | the List | nothing | no, this is counting |

A fifth file, `jobs/approval.py`, is not a job. It is the escalation path Chase routes into
when a row is past the escalation threshold: the worker drafts a reason, posts two buttons, and
a human decides. See [why approval got its own file](../decisions/build-adr-b3-approval-gets-its-own-file.md).

The four verbs are the point, not onboarding. Swap the List and the job description and the
same body runs a deal desk, compliance renewals, a candidate pipeline, or contract expiries.

Detection being code and judgement being the model is a deliberate split; see
[the chase split](../decisions/spec-adr-3-chase-split.md).
