"""report

trigger: Mondays at 09:00 scheduler time, or a mention saying run report
reads:   the List
writes:  nothing
surface: one message in the channel
brain:   no, this is counting and nothing else
"""

import datetime

import policy
from tools import lists

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
        elif state == "Open":
            if today <= due <= soon:
                upcoming.append("%s on %s" % (step, due.isoformat()))
            if oldest is None or due < oldest[1]:
                oldest = (step, due)

    lines = ["Cohort status, %d steps." % len(items)]
    lines += ["%s: %d" % (state, counts[state]) for state in sorted(counts)]
    lines.append("Oldest open step: %s, due %s"
                 % (oldest[0], oldest[1].isoformat()) if oldest else "No open steps.")
    lines.append("No due date: %d" % len(no_due) + (" (%s)" % ", ".join(no_due[:3]) if no_due else ""))
    lines.append("Due in the next seven days: %s" % ("; ".join(upcoming[:6]) or "nothing"))
    client.chat_postMessage(channel=policy.CHANNEL_ID, text="\n".join(lines[:20]))
    print("REPORT %d steps, %s, %d with no due date"
          % (len(items), ", ".join("%s %d" % (s, counts[s]) for s in sorted(counts)), len(no_due)),
          flush=True)
