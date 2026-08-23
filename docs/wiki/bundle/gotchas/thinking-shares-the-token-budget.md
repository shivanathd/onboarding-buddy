---
type: Concept
title: Thinking and writing share one token budget
description: The model emits a thinking block before it writes and both draw on the same output allowance, so a low ceiling returns a successful call with zero text.
source: ["docs/how-this-was-built.md measured block", "agent.py", "BUILD_DECISIONS.md ADR-B7 (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [model, tokens, silent-failure]
---
# Thinking and writing share one token budget

This one cost the most time to see, because it fails silently.

The model returns a thinking block before it returns any words, and both come out of the same
output token allowance. Set the allowance low and you get a call that succeeds, returns no text
at all, and leaves you looking at a fallback while holding a perfectly valid key. There is no
exception, so there is nothing to catch and, in the first version, nothing was logged either.

Measured on the same prompt:

```
max_tokens=220  stop_reason max_tokens  blocks ['thinking']          text 0 chars
max_tokens=600  stop_reason max_tokens  blocks ['thinking', 'text']  text 213 chars
```

At 220 the entire allowance went to thinking and the answer was empty. At 600 the thinking
finished and 213 characters of answer arrived.

## Two lessons

**Give the call a generous ceiling.** Truncation is a terrible way to shorten anything. It
either cuts a sentence in half or, as here, removes the answer entirely. The ceiling in this
worker is 1200.

**Control length in the prompt, where it belongs.** Asking for two or three sentences works.
Starving the model does not.

The path into this was itself instructive. An earlier fix cut the ceiling to 220 precisely
because the escalation text was running to three paragraphs, so a real defect was traded for a
worse and quieter one. Both are recorded in
[defects a green suite missed](../verification/defects-a-green-suite-missed.md).

The empty text path now logs the stop reason; see
[any fallback without a log line gets debugged twice](log-every-fallback-path.md) and
[ADR-B7](../decisions/build-adr-b7-generous-token-ceiling.md).
