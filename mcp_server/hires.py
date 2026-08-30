"""Read-only tools over the onboarding List. The second door's whole vocabulary.

Door one (Socket Mode) and door two (MCP) read the same List through the same
tools/lists.py adapter, so a schema change lands in one place for both.

The List is one row per step, not one row per hire. These tools aggregate: a
hire's status is derived from the statuses of their steps, which is why nothing
here writes and nothing here caches across a request. Stale onboarding data
quoted on stage is worse than a slow call.
"""

import collections
import datetime
import time

from slack_sdk import WebClient

import policy
from tools import lists

_web = WebClient(token=policy.SLACK_BOT_TOKEN)

# Display names for user ids. Slack user ids are stable for the life of a
# process, so this is a memo, not a cache of List state. The List itself is
# re-read on every single call.
_NAMES = {}


def _display_name(user_id):
    """A buddy's name, falling back to the raw id so a lookup failure never
    empties a row."""
    if not user_id:
        return ""
    if user_id in _NAMES:
        return _NAMES[user_id]
    try:
        profile = _web.users_info(user=user_id)["user"]
        name = (profile.get("profile") or {}).get("real_name") or profile.get("name") or user_id
    except Exception:
        name = user_id
    _NAMES[user_id] = name
    return name


def _person_or_text(item, column_id):
    """A name from a cell that may be either a person column or a text column.

    The live List holds the new hire as a person reference; Spec 4's proposed
    schema holds it as text, because fictional hires have no Slack account.
    Reading both means the tools survive either List without a code change, and
    a person column no longer silently reads as an empty string.
    """
    plain = lists.text_of(item, column_id)
    if plain:
        return plain
    return _display_name(lists.first_user(item, column_id))


def _derive_status(done, escalated, total):
    """A hire is done when every step is, blocked when any step escalated, and
    onboarding otherwise. Order matters: blocked beats done-so-far."""
    if escalated:
        return "blocked"
    if total and done == total:
        return "done"
    return "onboarding"


def read_hires(deadline):
    """Every hire in the List, aggregated from their step rows.

    deadline is an absolute time.monotonic() value. It is checked between
    pages rather than enforced by a timer thread, so a slow Slack response
    cannot leave a half-read List behind.
    """
    client = lists.lists_client(_web)
    items = lists.list_items(client, policy.LIST_ID)
    if time.monotonic() > deadline:
        raise TimeoutError("reading the List took too long")

    cols = policy.COLUMNS
    by_hire = collections.OrderedDict()

    for item in items:
        hire = _person_or_text(item, cols["hire"]).strip()
        if not hire:
            continue
        row = by_hire.get(hire)
        if row is None:
            row = by_hire[hire] = {
                "name": hire,
                "buddy": "",
                "status": "onboarding",
                "steps_done": 0,
                "steps_total": 0,
                "next_due": None,
                "_escalated": 0,
            }

        row["steps_total"] += 1
        status = (lists.select_value(item, cols["status"]) or "").lower()
        if status == "done":
            row["steps_done"] += 1
        elif status == "escalated":
            row["_escalated"] += 1

        if not row["buddy"]:
            row["buddy"] = _person_or_text(item, cols["owner"])

        # The soonest date still owed. Completed steps cannot be next.
        if status != "done":
            due = lists.date_of(item, cols["due"])
            if due and (row["next_due"] is None or due < row["next_due"]):
                row["next_due"] = due

    out = []
    for row in by_hire.values():
        row["status"] = _derive_status(row["steps_done"], row.pop("_escalated"),
                                       row["steps_total"])
        due = row["next_due"]
        row["next_due"] = due.isoformat() if isinstance(due, datetime.date) else None
        out.append(row)
    return out


def _sentence(row):
    """One hire, phrased the way the model should quote it into the panel."""
    line = ("%s (buddy %s, %s, %d/%d steps"
            % (row["name"], row["buddy"] or "unassigned", row["status"],
               row["steps_done"], row["steps_total"]))
    if row["next_due"]:
        line += ", next due %s" % row["next_due"]
    return line + ")"


# ------------------------------------------------------------------ the tools

def list_new_hires(status="all", limit=20, deadline=None):
    rows = read_hires(deadline)
    if status != "all":
        rows = [r for r in rows if r["status"] == status]
    rows = rows[:limit]

    if not rows:
        text = "No new hires with status '%s'." % status
    else:
        text = "%d new hires. %s." % (len(rows), ". ".join(_sentence(r) for r in rows))
    return text, {"count": len(rows), "new_hires": rows}


def get_onboarding_status(new_hire, deadline=None):
    rows = read_hires(deadline)
    wanted = new_hire.strip().lower()

    for row in rows:
        if row["name"].lower() == wanted:
            text = ("%s: buddy %s, status %s, %d of %d steps done"
                    % (row["name"], row["buddy"] or "unassigned", row["status"],
                       row["steps_done"], row["steps_total"]))
            if row["next_due"]:
                text += ", next step due %s" % row["next_due"]
            return text + ".", {"found": True, "new_hire": row}

    # An empty lookup is an answer, not a failure. Offer the near misses so the
    # model can correct itself in one more turn instead of giving up.
    first_word = wanted.split(" ")[0] if wanted else ""
    closest = [r["name"] for r in rows if first_word and first_word in r["name"].lower()]
    text = "No row in the onboarding List matches '%s'." % new_hire
    if closest:
        text += " Closest names: %s." % ", ".join(closest)
    return text, {"found": False, "closest": closest}


def get_onboarding_summary(deadline=None):
    rows = read_hires(deadline)
    counts = collections.Counter(r["status"] for r in rows)
    by_status = {k: counts.get(k, 0) for k in ("onboarding", "blocked", "done")}
    text = ("%d new hires: %s."
            % (len(rows), ", ".join("%d %s" % (v, k) for k, v in by_status.items())))
    return text, {"total": len(rows), "by_status": by_status}
