---
type: Concept
title: Canvas content has no read API
description: No official method returns canvas text; the unofficial download works but returns markup rather than the markdown that went in, so a fallback is mandatory.
source: ["docs/how-this-was-built.md", "tools/context.py", "spec EVIDENCE.md E11", "spec DECISIONS.md ADR-2", "BUILD_DECISIONS.md ADR-B4 (private build log)"]
verified: 2026-08-23
timestamp: 2026-08-24
tags: [canvas, undocumented, fallback]
---
# Canvas content has no read API

The worker reads its job description from a canvas at run time, which means anyone who can edit
that canvas can change how the worker behaves with no deploy and no code. That is the feature.
Getting the text out is the problem.

There is no official method that returns canvas content. The `canvases:read` scope is
compatible with exactly one method, which returns section identifiers matching criteria, not
document text.

## The unofficial path, which works

Fetch the file information for the canvas, take its private URL, and download it with the bot
token in an authorization header. That returns the document. It is not an official contract.

## What comes back is not what went in

The content is written as markdown and comes back as markup: on the canvas observed here, a
container element wrapping heading, paragraph and list item tags. So anything reading a canvas
has to strip tags, and the format is documented to vary by canvas generation, which means the
strip step must stay deliberately dumb: keep the text, drop the tags, put a newline where a
block ended.

## Therefore the fallback is not decorative

Because the read path is unofficial and the format varies, the worker falls back to a file in
the repository and says so loudly in the log. The fallback runs at boot as well as before an
answer, so a bad canvas identifier shows up in the boot log rather than during a demo. Holdout
H5 exists purely to prove that fallback is real.

There is a governance point hiding here. Whoever can edit that canvas can reprogram the
worker's tone and priorities. Hard limits therefore belong in the settings file and in
[the scopes](../setup/the-eight-bot-scopes.md), never in the brief.

Related: [ADR-2](../decisions/spec-adr-2-canvas-read-fallback.md),
[ADR-B4](../decisions/build-adr-b4-canvas-is-markup.md),
[a List is a file](a-list-is-a-file.md).
