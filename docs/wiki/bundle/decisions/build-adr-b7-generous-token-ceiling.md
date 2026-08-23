---
type: Decision
title: "ADR-B7: a generous token ceiling, brevity in the prompt"
description: The ceiling goes up to 1200 and length is requested in the prompt, because truncation removed the answer entirely.
source: ["BUILD_DECISIONS.md ADR-B7 (private build log)", "agent.py", "docs/how-this-was-built.md measured block", "jobs/answer.py", "git log b5db0bc"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [adr, build, model, tokens]
---
# ADR-B7: a generous token ceiling, brevity in the prompt

**Context.** An earlier fix cut the ceiling to 220 tokens, to stop an escalation running to
three paragraphs. That produced a worse failure: the model spends its budget thinking before it
writes, so the call succeeded and carried no text at all, and the worker used a template while
holding a valid key. It logged nothing, because an empty success is not an exception.

**Decision.** The ceiling goes to 1200. Length is requested in the prompt instead, and the empty
text path now logs the stop reason.

The system prompt also asks the model not to join clauses with a dash, and any that slip through
are replaced in code, because the house style for this series forbids them and the same rule is
enforced by a check across the whole tree.

**Consequences.** Answers arrive complete and short. Cost stays trivial at a handful of calls a
day, and truncation is no longer being used as an editor.

## The prompt wording needed a second pass

"Two or three sentences" turned out to be too loose. The model read it as permission for two
paragraphs, and Slack collapsed the second behind a show more link, which on a projector is the
same as not writing it. The answer prompt now asks for at most three sentences **as one
paragraph**, and says explicitly never to write a second one.

That is worth noting as a property of prompt based length control rather than an argument against
it. Asking for a sentence count constrains sentences and says nothing about paragraphs, and the
surface that renders the output has its own opinion about how much it will show. Constrain the
shape the surface cares about, not just the size.

The escalation draft asks for two sentences at most, which was already tight enough not to hit
this.

See [thinking shares the token budget](../gotchas/thinking-shares-the-token-budget.md) and
[any fallback without a log line gets debugged twice](../gotchas/log-every-fallback-path.md).
