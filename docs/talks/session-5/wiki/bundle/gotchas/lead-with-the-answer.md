---
type: Decision
title: An agent that opens with what it cannot do reads as broken — fix the prompt ordering, not the model
description: "The worker led every action request with a capability disclaimer. The cause was a stack of negative constraints appended last in the prompt, overriding a persona instruction that was already correct."
source: ["onboarding-buddy jobs/answer.py before and after commit 700b6ab", "observed reply in <your record channel> 2026-08-31 21:03 and the replacement 2026-09-01 00:34", "ANTHROPIC_MODEL=claude-sonnet-5 on Railway"]
verified: 2026-09-01
timestamp: 2026-09-01
tags: [prompting, agents, tone, teaching, slack]
---
# Lead with the answer

Asked *"please start onboarding these placements"*, the worker replied:

> "I'm not able to start onboarding, I only read the List and reply here. That said, all four
> names already have onboarding steps open, so it looks underway. Here's where things stand…"

Every word true. Useless as an opening. And to a room it reads as a broken bot — the useful
content is two clauses in, hedged with *"looks"*, and long enough that Slack folded the overdue
list behind a **Show more** link, hiding the only part anyone needed.

## It was not a model problem

`ANTHROPIC_MODEL=claude-sonnet-5` — a fully capable model. Checking that first mattered,
because the instinct is to reach for a bigger model when an agent feels dim.

It was also **not** a missing persona instruction. The job description already said:

> Warm and direct. You work here. You are not a support ticket.

## It was prompt ordering

The block appended **after** the job description was four *cannots* and two *nevers* in one
breath:

> "You can only read and answer. You cannot escalate, tick a box, change a date or post
> anything other than this reply, so never offer to do any of those and never say you will."

Specific, negative and last-in-context beats general and positive. So when the request *was*
an action, the most salient thing in the model's context was the list of things it could not
do — and it opened with them, exactly as instructed, to bad effect.

**The instruction was doing its job. Its job was badly specified.**

## The fix: express the constraint as ordering, not refusal

Substance unchanged. Shape rewritten, in three ordered blocks — surface, then shape, then
honesty:

1. **Lead with the answer.** The first line carries the most useful fact. Never open with what
   you cannot do, and never describe your own capabilities unless asked what you can do.
2. **When asked to do something, do not refuse and do not explain yourself.** Answer the real
   question behind the request from the state you have, then close with *at most one short
   clause* naming the thing that actually does it. Never say you will do it yourself.
3. **Be flat about facts.** The state is in front of you, so give the count and the date
   rather than saying it looks or seems that way.

Plus a tighter length ceiling — ten lines to six — because the folding was hiding the payload.

## The result, same question

> "Onboarding for the four Meridian placements is already underway, 12 steps tracked, 5
> overdue.
> • Sara Okonkwo, Access badge, 8 days overdue
> • Rahul Menon, Manager intro call, 5 days overdue
> • Rahul Menon, Email account, 2 days overdue
> • Priya Raman, Laptop delivery, 3 days overdue
> • Priya Raman, Security training, 1 day overdue
> Nudges on these go out via the tick, not from me."

The boundary is still there, still honest, and now subordinate — one closing clause that also
tells the human what *does* close a step, which is more useful than the refusal ever was.

## Two rules worth carrying off this

**A negative constraint appended last will dominate a positive persona set earlier.** If tone
and truthfulness are fighting, it is almost always because the truthfulness instruction was
written as a prohibition and put nearer the end. Rewrite it as ordering.

**"It can't do X" and "it should say it can't do X first" are different instructions.** The
prompt only ever needed the first. Conflating them is what produced a bot that talked about
itself instead of doing its job — and it is, in my experience, the single most common reason
an agent feels unhelpful while being perfectly correct.

This is also a good thing to say out loud during the demo: the read-only boundary did not
change, only where it appears in the sentence.

Related: [onboarding-buddy](../cast/onboarding-buddy.md),
[the five acts](../demo/the-five-acts.md).
