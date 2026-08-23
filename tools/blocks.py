"""How the worker presents itself: Block Kit shapes and the status indicator.

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


def thinking(client, channel, thread_ts, on=True):
    """Slack's native thinking indicator, if this app is allowed to use it.

    Needs assistant:write. That scope is optional, so a refusal here is not a
    problem: the caller falls back to posting an ordinary status message. Slack
    accepts this on a normal channel thread as well as in the assistant pane.
    """
    try:
        client.assistant_threads_setStatus(
            channel_id=channel, thread_ts=thread_ts,
            status="is thinking..." if on else "",
            loading_messages=["Reading the List...",
                              "Checking the job description...",
                              "Working out what is overdue..."] if on else None)
        return True
    except Exception:
        return False
