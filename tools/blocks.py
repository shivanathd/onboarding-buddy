"""Block Kit shapes, in one place.

Block Kit JSON is verbose and it is shared by the report and the approval flow.
Keeping it here means the job files stay short enough to read on a projector,
which is the whole point of how this repository is laid out.
"""


def header(text):
    return {"type": "header", "text": {"type": "plain_text", "text": text, "emoji": True}}


def section(text):
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def fields(pairs):
    """Two column key and value tiles, up to ten per block."""
    return {"type": "section", "fields": [{"type": "mrkdwn", "text": "*%s*\n%s" % (k, v)}
                                          for k, v in pairs[:10]]}


def divider():
    return {"type": "divider"}


def context(text):
    return {"type": "context", "elements": [{"type": "mrkdwn", "text": text}]}


def button(action_id, label, value, style=None):
    made = {"type": "button", "action_id": action_id, "value": value,
            "text": {"type": "plain_text", "text": label, "emoji": True}}
    return dict(made, style=style) if style else made


def actions(*elements):
    return {"type": "actions", "elements": list(elements)}
