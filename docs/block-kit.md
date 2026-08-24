# Block Kit is the house style

Every message this worker sends is Block Kit, and every payload it can send has
been validated against Slack rather than eyeballed once.

## What each surface looks like

| Surface | Layout |
|---|---|
| Answer | a section, then a grey footer saying how many steps it read |
| Working status | Slack's own thinking indicator, or a context line as a fallback |
| Chase nudge | the step in bold, then a footer telling you to tick the message |
| Completion | a tick, the step, and a note that the List holds the state |
| Retired nudge | the same message rewritten, so a closed step cannot be reopened |
| Escalation | a header, the drafted reason, and two buttons |
| Decision made | the buttons replaced by what was decided |
| Report | a header, a grid of counts, a divider, the next seven days, a link button |

## Where prose beats a card

The answer is deliberately a plain section rather than a card with a header. It
is one or two sentences from a colleague, and wrapping that in a dashboard makes
it read like a report from a system. Structure goes where there is structure: the
report has counts, so it gets a grid. The escalation needs a decision, so it gets
buttons. A sentence gets a sentence.

## Three mistakes worth knowing

**There is no text block type.** Text is a composition object:
`{"type": "plain_text", "text": "..."}` or `{"type": "mrkdwn", "text": "..."}`.

**Slack markdown is single asterisk.** `*bold*` and `_italic_`, not the doubled
form. A doubled asterisk renders literally.

**Every message needs a top level text fallback.** Validation will not complain
if you leave it out, but notifications and screen readers show the fallback
instead of your blocks, so an empty one means a silent notification. Every
`blocks=` call in this repository has a matching `text=`.

## A url button still sends you an interaction

The Open the List button opens a browser, and Slack also sends an interaction
payload for it. Left unhandled, Slack marks the message with a warning triangle
meaning nobody was listening. So the button carries an action id, `app.py`
acknowledges it like any other click, and the decision handler ignores anything
that is not a decision.

That triangle is worth recognising. It does not mean your layout is wrong. It
means your process is not running, or it is running and nothing matched.

## Validating your own layouts

`blocks.validate` is a real method and it costs nothing to call. Build the
payload, send it, read the answer:

    curl -s https://slack.com/api/blocks.validate \
      -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"blocks": [{"type": "section",
                       "text": {"type": "mrkdwn", "text": "*hello*"}}]}'

A valid payload answers `{"ok": true}`. An invalid one names the offending field
and the path to it, which is far more useful than guessing from a message that
looks slightly wrong.

Every payload this worker can send returns `ok` and carries a fallback.

## Slack publish a skill for this

Slack maintain a Block Kit skill for AI coding tools, MIT licensed, at
`github.com/slackapi/slack-skills-plugin` under `skills/block-kit`. It walks
surface choice, layout, generation and validation, and it insists on reading each
component's schema from the live documentation rather than from memory. Worth
installing if you are going to build your own layouts:

    ~/.claude/skills/block-kit/SKILL.md

It is deliberately not vendored here. It is theirs, it changes, and a stale copy
of somebody else's skill is worse than a pointer to the current one.

## Reading the component schemas

Append `.md` to any Block Kit reference URL and it comes back as markdown:

    https://docs.slack.dev/reference/block-kit.md
    https://docs.slack.dev/reference/block-kit/blocks/section-block.md
    https://docs.slack.dev/reference/block-kit/block-elements/button-element.md

That index is the authoritative list. If a block type is not on it, it does not
exist, whatever an example somewhere else says.
