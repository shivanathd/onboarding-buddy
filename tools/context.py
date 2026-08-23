"""What the worker knows before it says anything.

Three sources, always in this order:

1. The List. State. What steps exist and where they stand.
2. The brief. The canvas holding the job description, with the copy in
   seed/job-description.md as a fallback so a missing canvas is never fatal.
3. The conversation. Recent channel and thread text, for the human detail that
   never makes it into a cell.

Grounding comes first on purpose. The brain is never asked anything until the
List read has succeeded.
"""

import html.parser
import pathlib
import urllib.request

import policy
from tools import lists


def rows(client):
    """Every List row. State before opinion.

    Jobs are handed the plain Slack client, so the Lists adapter is built here
    rather than threaded through every caller.
    """
    return lists.list_items(lists.lists_client(client), policy.LIST_ID)


# ------------------------------------------------------------------- the brief

_FALLBACK = pathlib.Path(__file__).resolve().parent.parent / "seed" / "job-description.md"


class _Strip(html.parser.HTMLParser):
    """Canvas content comes back as markup, not as the markdown that went in.

    Observed on a channel canvas: a div carrying class quip-canvas-content
    wrapping h1, p and li tags. E11 warns the format varies by canvas
    generation, so this stays deliberately dumb: keep the text, drop the tags,
    put a newline where a block ended.
    """

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_endtag(self, tag):
        if tag in ("p", "div", "li", "h1", "h2", "h3", "br", "tr"):
            self.parts.append("\n")

    def text(self):
        joined = "".join(self.parts)
        return "\n".join(line.strip() for line in joined.splitlines() if line.strip())


def _canvas_text(client, file_id):
    """Download the canvas and return plain text.

    There is no official API that returns canvas content. files.info gives a
    url_private, and that download needs the bot token in an Authorization
    header. UNVERIFIED for newer canvas generations, rehearsal check 9.
    """
    info = client.files_info(file=file_id)
    url = info["file"].get("url_private") or info["file"]["url_private_download"]
    request = urllib.request.Request(url, headers={"Authorization": "Bearer " + client.token})
    with urllib.request.urlopen(request, timeout=20) as handle:
        body = handle.read().decode("utf-8", "replace")
    parser = _Strip()
    parser.feed(body)
    text = parser.text()
    if not text.strip():
        raise ValueError("canvas download was empty")
    return text


def brief(client):
    """The job description. Canvas when we can read it, repo copy when we cannot.

    Whoever can edit the canvas can change how this worker behaves, with no
    deploy. That is a feature and it is also a governance question.
    """
    if policy.CANVAS_FILE_ID:
        try:
            text = _canvas_text(client, policy.CANVAS_FILE_ID)
            print("brief: canvas %s, %d characters" % (policy.CANVAS_FILE_ID, len(text)), flush=True)
            return text
        except Exception as problem:
            print("brief: repo fallback, the canvas read failed with %s" % problem, flush=True)
    else:
        print("brief: repo fallback, no canvas file id is set", flush=True)
    return _FALLBACK.read_text()


# ------------------------------------------------------------- the conversation

def recent_messages(client, channel, limit=20):
    """The last few things said in the channel."""
    try:
        found = client.conversations_history(channel=channel, limit=limit)
        return [m.get("text", "") for m in found.get("messages") or []]
    except Exception as problem:
        print("context: channel history unavailable, %s" % problem, flush=True)
        return []


def thread_replies(client, channel, thread_ts):
    """Everything said under one message. This is where the reason a step is
    stuck usually lives."""
    try:
        found = client.conversations_replies(channel=channel, ts=thread_ts)
        return [m.get("text", "") for m in found.get("messages") or []]
    except Exception as problem:
        print("context: thread unavailable, %s" % problem, flush=True)
        return []


def search(client, query):
    """Real Time Search, quarantined.

    UNVERIFIED whether Real Time Search answers for a custom app token,
    rehearsal check 3. Until it does, context comes from the documented
    conversations methods above. If the rehearsal proves it out, it swaps in
    here and nothing else in the repo changes.
    """
    return NotImplemented


# ----------------------------------------------------------------- assembly

def summarise_rows(items):
    """The List as plain lines a person could read off a projector."""
    out = []
    for item in items:
        step = lists.text_of(item, policy.COLUMNS["step"])
        hire = lists.first_user(item, policy.COLUMNS["hire"])
        owner = lists.first_user(item, policy.COLUMNS["owner"])
        due = lists.date_of(item, policy.COLUMNS["due"])
        status = lists.text_of(item, policy.COLUMNS["status"]) or "Open"
        out.append("step=%s hire=%s owner=%s due=%s status=%s"
                   % (step, hire or "unassigned", owner or "unassigned",
                      due.isoformat() if due else "none", status))
    return out


def state_markdown(items, limit=12):
    """The List as Slack markdown for a human to read.

    summarise_rows above feeds the model, so it stays flat and boring. This one
    is for eyes: bold step names, a status marker, and real mentions rather than
    raw user ids.
    """
    marker = {policy.STATUS_OPEN: ":large_blue_circle:",
              policy.STATUS_DONE: ":white_check_mark:",
              policy.STATUS_ESCALATED: ":warning:"}
    out = []
    for item in items[:limit]:
        step = lists.text_of(item, policy.COLUMNS["step"])
        owner = lists.first_user(item, policy.COLUMNS["owner"])
        due = lists.date_of(item, policy.COLUMNS["due"])
        status = (lists.select_label(item, policy.COLUMNS["status"], policy.STATUS_LABELS)
                  or policy.STATUS_OPEN)
        out.append("%s *%s* %s %s" % (
            marker.get(status, ""), step,
            "due " + due.isoformat() if due else "no due date",
            "<@%s>" % owner if owner else "_unassigned_"))
    if len(items) > limit:
        out.append("_and %d more_" % (len(items) - limit))
    return out


def assemble(client, channel, thread_ts=None):
    """Everything the worker knows, in the order ANS-2 requires."""
    items = rows(client)
    text = brief(client)
    talk = recent_messages(client, channel)
    if thread_ts:
        talk = thread_replies(client, channel, thread_ts) + talk
    return {
        "items": items,
        "state": "\n".join(summarise_rows(items)) or "The List has no rows.",
        "brief": text,
        "conversation": "\n".join(t for t in talk if t)[:4000],
    }
