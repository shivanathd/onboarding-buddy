"""report

trigger: Mondays at 09:00 scheduler time, or a mention saying run report
reads:   the List
writes:  nothing
surface: one Block Kit card in the channel
brain:   no, this is counting and nothing else
"""

import datetime

import policy
from tools import blocks, lists

LABELS = policy.STATUS_LABELS


def _link(client):
    """The List's own permalink, asked for rather than assembled out of ids."""
    try:
        return client.files_info(file=policy.LIST_ID)["file"]["permalink"]
    except Exception:
        return ""


def _consultant(step):
    """The consultant's name, when the step text carries one.

    Steps read "Sara Okonkwo <emdash> Access badge". The name lives in the TEXT
    rather than in a column because the List's New hire column is a PERSON
    column, and this workspace has one member, so grouping by that column rolls
    all twelve rows onto one human and the card ends up saying
    "@Shivanath 12 open, 5 late" under a list of four named consultants.
    Grouping by the text is what makes By person say something true.
    """
    parts = step.split(" %s " % chr(8212))
    return parts[0].strip() if len(parts) > 1 else ""


def _read(items, today):
    """Everything the card needs, counted once."""
    counts, overdue, upcoming, no_due, people = {}, [], [], [], {}
    for item in items:
        state = lists.select_label(item, policy.COLUMNS["status"], LABELS) or policy.STATUS_OPEN
        counts[state] = counts.get(state, 0) + 1
        step = lists.text_of(item, policy.COLUMNS["step"])
        hire = lists.first_user(item, policy.COLUMNS["hire"])
        owner = lists.first_user(item, policy.COLUMNS["owner"])
        due = lists.date_of(item, policy.COLUMNS["due"])
        label = _consultant(step) or (("<@%s>" % hire) if hire else "unassigned")
        seen = people.setdefault(label, {"total": 0, "late": 0})
        seen["total"] += 1
        if due is None:
            no_due.append(step)
        elif state == policy.STATUS_OPEN and due < today:
            overdue.append(((today - due).days, step, owner))
            seen["late"] += 1
        elif state == policy.STATUS_OPEN and due <= today + datetime.timedelta(days=7):
            upcoming.append((due, step))
    return counts, sorted(overdue, reverse=True), sorted(upcoming), no_due, people


def run(client):
    """Post the cohort status. Every number here can be recounted by eye from
    the List, which is the point."""
    items = lists.list_items(lists.lists_client(client), policy.LIST_ID)
    if not items:
        client.chat_postMessage(channel=policy.CHANNEL_ID, text="0 rows. Nothing to report.")
        print("REPORT 0 rows. Nothing to report.", flush=True)
        return

    today = datetime.date.today()
    counts, overdue, upcoming, no_due, people = _read(items, today)

    tiles = [(state, str(counts[state])) for state in sorted(counts)]
    tiles.append(("Overdue", str(len(overdue))))
    tiles.append(("No due date", str(len(no_due))))
    tiles.append(("Oldest open", "%s, %d days over" % (overdue[0][1], overdue[0][0])
                  if overdue else "nothing overdue"))

    late = "\n".join("*%s* %d day%s over, <@%s>" % (step, days, "" if days == 1 else "s", owner)
                     if owner else "*%s* %d days over, _unassigned_" % (step, days)
                     for days, step, owner in overdue[:5]) or "nothing overdue"
    soon = "\n".join("*%s* %s" % (step, when.isoformat())
                      for when, step in upcoming[:5]) or "nothing due this week"
    who = "\n".join("*%s* %d open, %d late" % (label, seen["total"], seen["late"])
                     for label, seen in sorted(people.items())[:6])

    body = [blocks.header("Cohort status"),
            blocks.fields(tiles),
            blocks.divider(),
            blocks.section("*Overdue now*\n" + late),
            blocks.section("*Due in the next seven days*\n" + soon)]
    if who:
        body.append(blocks.section("*By person*\n" + who))
    link = _link(client)
    if link:
        body.append(blocks.actions(blocks.link_button("Open the List", link)))
    body.append(blocks.context("%d steps in the List. Every number here is countable by eye."
                               % len(items)))

    client.chat_postMessage(channel=policy.CHANNEL_ID, blocks=body,
                            text="Cohort status, %d steps, %d overdue."
                                 % (len(items), len(overdue)))
    print("REPORT %d steps, %s, %d overdue, %d with no due date"
          % (len(items), ", ".join("%s %d" % (s, counts[s]) for s in sorted(counts)),
             len(overdue), len(no_due)), flush=True)
