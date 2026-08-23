---
type: Concept
title: Defects a green suite missed
description: Seven real defects that a fully passing test suite did not catch, and what each one says about the limits of a check.
source: ["docs/how-this-was-built.md what the checks could not catch", "PROGRESS.md bugs the live runs found (private build log)", "git log 46b3d9e", "git log 157db7d", "git log b5db0bc"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [verification, defects, honesty]
---
# Defects a green suite missed

This is worth stating plainly, because a green board is not proof. Seven real defects survived a
passing suite. Four were found before the ship verdict and three after it, all seven by running
the thing and reading the output carefully.

## A clock that compressed too much

The demo switch was supposed to shrink one thing, the grace window. It also shrank the escalation
threshold and the extension days. With a short threshold, every step that was a day overdue
jumped straight to escalation, so the ordinary nudge never appeared at all and one act of the
demo would have vanished. Every test still passed, because no test asserted that both behaviours
could occur in the same run.

**The lesson.** A test per behaviour does not test the interaction between behaviours.

## A duplicate that only appears on the second pass

The clock job writes a message id back into the row so it knows not to chase the same thing
twice. That guard was applied to the nudge path but not to the escalation path, and the
escalation guard separately refused only when Status was already Escalated, which happens after a
stand down click rather than before. So every scan opened another approval on the same row. One
run looks perfect. Three consecutive runs is what exposed it, and three consecutive runs is what
proved the fix.

**The lesson.** Idempotence is not observable in a single execution.

## A wrong argument type that no test exercised

One module passed the plain Slack client where the Lists adapter was expected. Every call through
that path would have raised at runtime. No check covered it, and reading the code found it.

**The lesson.** Coverage of the paths you thought of says nothing about the path you did not.

## Output that was correct and still useless

The escalation text was accurate and three paragraphs long, so Slack folded it behind a show more
link. On a projector that is the same as not writing it.

**The lesson.** Correct is not the same as usable, and no assertion about content catches a
presentation failure. The fix for this one then caused
[the silent empty answer](../gotchas/thinking-shares-the-token-budget.md), which is its own
lesson about fixing a defect by constraining a resource.

## The model could not see the Status column

Found after the ship verdict. Status was read with the text reader, but Status is a select column,
so it always came back empty and defaulted to Open. The model had never once seen a Done or an
Escalated row. The human readable view of the same state used the correct reader all along, so
the two views disagreed and only the model saw the wrong one.

**The lesson.** Two readers over one source will drift, and the one no human looks at is the one
that drifts silently. See
[a select column needs value, label and colour](../gotchas/select-column-needs-value-label-and-colour.md).

## The model was not told today's date

Found in the same pass. Nothing in the state told the model what day it was, so when asked what
was overdue it said, correctly, that it could not tell. The state now leads with today's date and
every row carries how late it is, worked out in Python. Dates are arithmetic. The model is there
for judgement, not for counting days.

**The lesson.** Grounding is not just the facts. It is the facts plus whatever the reader needs
to interpret them, and a model brings no context you did not hand it.

## The same presentation failure, in a second path

Found later still, and it is the fourth defect above happening again somewhere else. The answer
prompt asked for two or three sentences. The model read that as permission for two paragraphs,
and Slack collapsed the second behind a show more link. The escalation path had already been
fixed for exactly this; the answer path had not, because the fix had been written as a change to
one prompt rather than as a rule about output shape.

**The lesson.** A defect fixed in one place is not fixed. Ask which other paths share the shape
of the mistake, because the second occurrence will not announce itself either. The prompt now
asks for one paragraph explicitly; see
[ADR-B7](../decisions/build-adr-b7-generous-token-ceiling.md).

## What the seven have in common

Not one of them was a wrong calculation. They were an interaction between two settings, a state
transition only visible across runs, an argument type on an untested path, two presentation
failures where the output was correct and unreadable, a reader mismatch that only the
non human audience saw, and a missing piece of context. Assertions catch wrong answers. These
were all right answers in the wrong shape, at the wrong time, or seen by the wrong reader.

Related: [the three eval layers](the-three-eval-layers.md),
[the SHIP verdict](the-ship-verdict.md).
