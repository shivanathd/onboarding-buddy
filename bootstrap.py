"""Create the List, seed it, and print the mapping. Run this once.

Column ids like Col0BS1300PSS are opaque and there is no way to guess them. So
this prints a paste ready block instead of hiding the mapping in a file you
never read. It deliberately does NOT write .env for you: the mapping is the
thing this session is trying to teach.

  python bootstrap.py

Then paste the printed lines over the matching lines in .env.
"""

import csv
import datetime
import os
import pathlib
import sys
import time

import policy
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from tools import lists

SEED = pathlib.Path(__file__).with_name("seed") / "onboarding.csv"

SCHEMA = [
    {"key": "step", "name": "Step", "type": "text", "is_primary_column": True},
    {"key": "hire", "name": "New hire", "type": "user"},
    {"key": "owner", "name": "Owner", "type": "user"},
    {"key": "due", "name": "Due", "type": "date"},
    {"key": "status", "name": "Status", "type": "select", "options": {"choices": [
        {"value": "open", "label": "Open", "color": "blue"},
        {"value": "done", "label": "Done", "color": "green"},
        {"value": "escalated", "label": "Escalated", "color": "red"},
    ]}},
    {"key": "thread", "name": "Thread", "type": "text"},
]

# Every choice object needs value AND label AND color. Slack rejects the create
# without all three, and the docs do not say so.

ENV_KEY = {"step": "COL_STEP", "hire": "COL_HIRE", "owner": "COL_OWNER",
           "due": "COL_DUE", "status": "COL_STATUS", "thread": "COL_THREAD"}


def seed_users():
    """Real user ids stay out of the seed file. The csv carries symbols like
    owner_1, and they map onto whoever SEED_USERS names, falling back to the
    manager. That keeps the shipped seed generic with no names in it."""
    raw = [u.strip() for u in os.environ.get("SEED_USERS", "").split(",") if u.strip()]
    return raw or [policy.MANAGER_ID]


def resolve(symbol, pool, cache):
    """Give each distinct symbol a stable user from the pool."""
    if not symbol:
        return ""
    if symbol not in cache:
        cache[symbol] = pool[len(cache) % len(pool)]
    return cache[symbol]


def due_date(offset):
    """The csv stores day offsets so the seed never goes stale."""
    if offset in ("", None):
        return None
    return datetime.date.today() + datetime.timedelta(days=int(offset))


def main():
    if policy.LIST_ID:
        print("LIST_ID is already set, so there is nothing to create. Clear it "
              "in .env first if you really want a second List.")
        return 1
    if not policy.SLACK_BOT_TOKEN:
        print("SLACK_BOT_TOKEN is not set. Fill it in .env and run this again.")
        return 1

    web = WebClient(token=policy.SLACK_BOT_TOKEN)
    client = lists.lists_client(web)

    try:
        created = lists.create_list(client, "Onboarding cohort", SCHEMA)
    except SlackApiError as problem:
        code = problem.response.get("error")
        if code == "enterprise_is_restricted":
            print("This workspace is an Enterprise org, where the Lists API "
                  "cannot create a List. Build the List by hand in Slack using "
                  "the schema in the README, then read the column ids back with "
                  "slackLists.items.list and fill .env yourself.")
            return 1
        print("Could not create the List: %s" % code)
        for message in (problem.response.get("response_metadata") or {}).get("messages", []):
            print("  %s" % message)
        return 1

    list_id = created["list_id"]
    schema = created["list_metadata"]["schema"]
    columns = {col["key"]: col["id"] for col in schema}
    options = {}
    for col in schema:
        for choice in ((col.get("options") or {}).get("choices") or []):
            options[choice["label"].lower()] = choice["value"]
    print("Created the List %s with %d columns." % (list_id, len(columns)))

    pool = seed_users()
    hires, owners = {}, {}
    rows = list(csv.DictReader(SEED.open()))
    made = 0
    for number, row in enumerate(rows, start=2):
        fields = [{"column_id": columns["step"], "rich_text": lists.text_cell(row["step"])},
                  {"column_id": columns["status"], "select": lists.select_cell(options["open"])}]

        hire = resolve(row["hire"], pool, hires)
        if hire:
            fields.append({"column_id": columns["hire"], "user": lists.user_cell(hire)})

        owner = resolve(row["owner"], pool, owners)
        if owner:
            fields.append({"column_id": columns["owner"], "user": lists.user_cell(owner)})
        else:
            print("  line %d, %s has no owner. The worker will route it to the "
                  "manager. This is allowed, not an error." % (number, row["step"]))

        when = due_date(row["due_offset_days"])
        if when:
            fields.append({"column_id": columns["due"], "date": lists.date_cell(when)})
        else:
            print("  line %d, %s has no due date. Chase will skip it and the "
                  "report counts it under no due date." % (number, row["step"]))

        try:
            lists.create_item(client, list_id, fields)
            made += 1
        except SlackApiError as problem:
            if problem.response.get("error") == "ratelimited":
                wait = int(problem.response.headers.get("Retry-After", 2))
                print("  rate limited, waiting %ds and retrying once" % wait)
                time.sleep(wait)
                lists.create_item(client, list_id, fields)
                made += 1
            else:
                print("  line %d failed: %s" % (number, problem.response.get("error")))
                return 1
        time.sleep(0.2)

    print("Seeded %d of %d rows. Owners used: %d." % (made, len(rows), len(set(owners.values()))))
    print("")
    print("Paste these seven lines over the matching lines in .env:")
    print("")
    print("LIST_ID=%s" % list_id)
    for key, name in ENV_KEY.items():
        print("%s=%s" % (name, columns[key]))
    print("")
    print("Then run: python app.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
