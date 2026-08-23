"""report

trigger: Mondays at 09:00 scheduler time, or a mention saying run report
reads:   the List
writes:  nothing
surface: one Block Kit message in the channel
brain:   no, this is counting and nothing else
"""

import datetime

import policy
from tools import blocks, lists


def run(client):
    """Post the cohort status. Every number here can be recounted by eye from
    the List, which is the point."""
    items = lists.list_items(lists.lists_client(client), policy.LIST_ID)
    if not items:
        client.chat_postMessage(channel=policy.CHANNEL_ID, text="0 rows. Nothing to report.")
        print("REPORT 0 rows. Nothing to report.", flush=True)
        return

    today = datetime.date.today()
    soon = today + datetime.timedelta(days=7)
    counts, no_due, upcoming, oldest = {}, [], [], None
    for item in items:
        state = lists.select_label(item, policy.COLUMNS["status"], policy.STATUS_LABELS) or policy.STATUS_OPEN
        counts[state] = counts.get(state, 0) + 1
        step = lists.text_of(item, policy.COLUMNS["step"])
        due = lists.date_of(item, policy.COLUMNS["due"])
        if due is None:
            no_due.append(step)
        elif state == policy.STATUS_OPEN:
            if today <= due <= soon:
                upcoming.append((due, step))
            if oldest is None or due < oldest[1]:
                oldest = (step, due)

    tiles = [(state, str(counts[state])) for state in sorted(counts)]
    tiles.append(("No due date", str(len(no_due)) + (" (%s)" % no_due[0] if no_due else "")))
    tiles.append(("Oldest open", "%s, due %s" % (oldest[0], oldest[1].isoformat())
                  if oldest else "nothing open"))
    lines = ["*%s*  %s" % (step, when.isoformat()) for when, step in sorted(upcoming)[:6]]
    body = [blocks.header("Cohort status"),
            blocks.fields(tiles),
            blocks.divider(),
            blocks.section("*Due in the next seven days*\n" + ("\n".join(lines) or "nothing")),
            blocks.context("%d steps in the List. Everything here is countable by eye."
                           % len(items))]
    client.chat_postMessage(channel=policy.CHANNEL_ID, blocks=body,
                            text="Cohort status, %d steps." % len(items))
    print("REPORT %d steps, %s, %d with no due date"
          % (len(items), ", ".join("%s %d" % (s, counts[s]) for s in sorted(counts)), len(no_due)),
          flush=True)
