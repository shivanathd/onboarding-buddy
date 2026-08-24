# How this was built

This worker was not written by feel. It was specified, then built against
executable checks, then proven against a live Slack workspace. If you want to
build your own worker, the method matters more than the code.

## The order of operations

1. **A spec with evidence.** Every claim about the Slack API traced to a
   primary source document before any code existed. Where no document answered
   a question, the spec marked it unverified and routed it to a live rehearsal
   rather than guessing. Six behaviours were marked that way. Four are now
   answered, and the answers are below.

2. **Evals before implementation.** Fifteen tasks, each with one command that
   says pass or fail. Seven shell checks on structure and configuration, eight
   Python checks on behaviour, and six end to end scenarios that run against a
   real workspace. Nothing was committed until its check passed.

3. **A throwaway app.** All of the live work happened against a disposable
   Slack app in a real workspace, never against anything that mattered.

4. **Live before believed.** Every job was run against real Slack before being
   called done. This is the part that found the bugs.

## What the checks could not catch

Four real defects survived a green test suite and were only found by running
the thing. This is worth stating plainly, because a green board is not proof.

**A clock that compressed too much.** The demo mode was supposed to shrink one
thing, the grace window. It also shrank the escalation threshold. With a short
threshold every step that was a day overdue jumped straight to escalation, so
the ordinary nudge never appeared at all. Every test still passed, because no
test asserted that both behaviours could occur in the same run.

**A duplicate that only appears on the second pass.** Chase writes a message id
back into the row so it knows not to chase the same thing twice. That guard was
applied to the nudge path but not to the escalation path, so every scan opened
another approval on the same row. One run looks perfect. Three runs in a row is
what exposed it.

**A wrong argument type that no test exercised.** One module passed a plain
Slack client where a wrapper was expected. Every call through that path would
have failed at runtime. No check covered it, and reading the code found it.

**Output that was correct and still useless.** The escalation text was accurate
and three paragraphs long, so Slack folded it behind a Show more link. On a
projector that is the same as not writing it. Correct is not the same as
usable.

## Undocumented behaviour, learned the hard way

These are all things the documentation does not say, established by calling the
API and reading what came back. Ids below are placeholders.

### A select column needs three fields per choice

Creating a List with a select column requires each choice to carry a value, a
label AND a colour. All three are mandatory. Omit any one and the call fails.

    {"key": "status", "name": "Status", "type": "select",
     "options": {"choices": [
       {"value": "open", "label": "Open", "color": "blue"},
       {"value": "done", "label": "Done", "color": "green"}]}}

The way to discover this is to read the error, not the docs. Slack returns
json-pointer paths naming the exact missing field, which is genuinely helpful:

    [ERROR] missing required field: color [json-pointer:/schema/4/options/choices/0]

### The create response already contains the column ids

There is no need for a second call to learn the generated column ids. The
create response carries them under list metadata, which is why the bootstrap
script can print a complete mapping immediately.

### Clearing a text cell is not writing an empty string

An empty text node is rejected with "must be more than 0 characters". To empty
a text cell, send an empty array instead.

    {"column_id": "Col0000000000", "rich_text": []}

### A List is a file

Which means the ordinary file deletion method removes one. There is no separate
List deletion method to look for.

### Canvas content comes back as markup, not as markdown

There is no official way to read canvas text. The unofficial route works: fetch
the file information, then download the private URL with the bot token in an
Authorization header. What returns is markup wrapped in a container element,
not the markdown that was written in, so anything reading a canvas needs to
strip tags. The format is documented to vary by canvas generation, so this path
should always have a fallback. Ours falls back to a file in the repository and
says so in the log.

### The model thinks before it writes, out of the same budget

This one cost the most time to see, because it fails silently.

The model returns a thinking block before it returns any words, and both come
out of the same output token allowance. Set the allowance low and you get a
call that succeeds, returns no text at all, and leaves you staring at a
fallback while holding a perfectly valid key.

Measured on the same prompt:

    max_tokens=220  stop_reason max_tokens  blocks ['thinking']          text 0 chars
    max_tokens=600  stop_reason max_tokens  blocks ['thinking', 'text']  text 213 chars

Two lessons. Give the call a generous ceiling, because truncation is a terrible
way to shorten anything: it either cuts a sentence in half or, as here, removes
the answer entirely. And control length in the prompt, where it belongs. Asking
for two sentences works. Starving the model does not.

The second lesson is about logging. The code fell back correctly and said
nothing about it, because the failure was an empty success rather than an
exception. Any fallback path worth having is worth a log line, or you will
debug it twice.

### Events are load balanced, not duplicated

An app may hold several socket connections at once, and Slack sends each event
to exactly one of them. Two copies of a worker do not both act. They each get a
random half, which is much harder to debug than a duplicate would be. Hence the
one worker on shift rule.

## The rehearsal questions, and their answers

| Question | Answer |
|---|---|
| Does a reaction on the app's own message raise an event | Yes. Proven end to end |
| Can a background scheduler and a socket connection share one process | Yes, on a laptop and hosted |
| Can a canvas be read with a bot token | Yes, as markup, with a fallback in place |
| Does a mention inside a thread carry the thread id | Still open. Both paths are coded |
| Is live search available to a custom app | Still open. Quarantined behind one function |
| Can the original message be updated after a button click | Still open. Needs a human click |

The first one mattered most. The entire completion flow depends on a person
reacting to a message the worker itself posted, and no document says whether
that raises an event. It does.

## Presentation is architecture too

Two of the seven defects were presentation failures, not logic failures: output
that was correct and unusable because Slack folded it behind a link, and a wall
of raw user ids where names belonged. Both passed every test, because no test
asks whether a human can read the result.

So presentation got the same treatment as everything else. Block Kit shapes live
in one module rather than being inlined in each job, which keeps the job files
short. And every payload the worker can send is checked with `blocks.validate`,
a real Slack method, so "it rendered once in my channel" is not the standard of
proof. See `docs/block-kit.md`.

One detail worth stealing: a url button opens a browser AND sends an interaction
payload. Unhandled, Slack marks the message with a warning triangle that means
nobody was listening. So the link button carries an action id, gets acknowledged
like any other click, and the decision handler ignores anything that is not a
decision.

## What the worker is not

It knows one channel and one List. It does not know your customer database and
it does not know that other workers exist. Routing between workers is still a
human habit. That ceiling is deliberate: a worker you can fully describe in one
page is a worker you can trust.
