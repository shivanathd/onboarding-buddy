"""Create the List, seed it, and print the mapping. Run this once.

Column ids like Col0000000000 are opaque and there is no way to guess them. So
this prints a paste ready block instead of hiding the mapping in a file you
never read. It deliberately does NOT write .env for you: the mapping is the
thing this session is trying to teach.

  python bootstrap.py

Then paste the printed lines over the matching lines in .env.

Who gets assigned to what:

  SEED_OWNERS   whoever should be chased about a step. Defaults to MANAGER_ID.
  SEED_HIRES    whoever the steps are for. Defaults to MANAGER_ID.

Both take a comma separated list of Slack user ids and both are optional. On a
one person workspace, leaving them empty is the right answer and everything
lands on you. If you have colleagues, keep SEED_OWNERS as yourself while you
are testing: the worker tags owners, and it will tag them every minute in
DEMO_MODE.
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


def pool(name):
    """User ids from one comma separated setting, or nothing."""
    return [u.strip() for u in os.environ.get(name, "").split(",") if u.strip()]


def people():
    """Who fills the New hire and Owner columns.

    SEED_USERS is the older single setting and still works, feeding both.
    """
    both = pool("SEED_USERS")
    hires = pool("SEED_HIRES") or both or [policy.MANAGER_ID]
    owners = pool("SEED_OWNERS") or both or [policy.MANAGER_ID]
    return hires, owners


def resolve(symbol, options, cache):
    """Give each distinct symbol in the csv a stable person from a pool."""
    if not symbol:
        return ""
    if symbol not in cache:
        cache[symbol] = options[len(cache) % len(options)]
    return cache[symbol]


def due_date(offset):
    """The csv stores day offsets so the seed never goes stale."""
    if offset in ("", None):
        return None
    return datetime.date.today() + datetime.timedelta(days=int(offset))


def explain(problem):
    """Say what a failure probably means, in words."""
    code = problem.response.get("error")
    if code == "enterprise_is_restricted":
        print("This workspace is an Enterprise org, where the Lists API cannot "
              "create a List at all. Build it by hand using the schema in the "
              "README, then read the column ids back and fill .env yourself.")
    elif code in ("method_not_supported_for_channel_type", "not_allowed_token_type",
                  "missing_scope", "invalid_auth", "account_inactive"):
        print("Slack refused the call with %s." % code)
        print("If this is a free or trial workspace, Lists may not be available "
              "on your plan. Check whether you can create a List by hand in "
              "Slack. If you cannot, the Lists half of this worker will not run "
              "here, and no amount of scopes will change that.")
    else:
        print("Could not create the List: %s" % code)
        print("If this is a trial workspace, the most likely cause is that "
              "Lists are not on your plan. Try creating one by hand in Slack "
              "first: if that is not offered, this is a plan limit.")
    for message in (problem.response.get("response_metadata") or {}).get("messages", []):
        print("  %s" % message)


def preflight():
    """Catch a bad setup before anything is created."""
    if policy.LIST_ID:
        print("LIST_ID is already set, so there is nothing to create. Clear it "
              "in .env first if you really want a second List.")
        return None
    if not policy.SLACK_BOT_TOKEN:
        print("SLACK_BOT_TOKEN is not set. Fill it in .env and run this again.")
        return None
    if not policy.MANAGER_ID:
        print("MANAGER_ID is not set. It is who unowned steps get routed to, so "
              "the seed needs it even if you are the only person here. Your own "
              "user id is fine.")
        return None
    web = WebClient(token=policy.SLACK_BOT_TOKEN)
    try:
        who = web.auth_test()
    except SlackApiError as problem:
        print("That bot token did not work: %s" % problem.response.get("error"))
        return None
    print("Connected to %s as %s." % (who.get("team"), who.get("user")))
    return web


def main():
    web = preflight()
    if web is None:
        return 1
    client = lists.lists_client(web)

    try:
        created = lists.create_list(client, "Onboarding cohort", SCHEMA)
    except SlackApiError as problem:
        explain(problem)
        return 1

    list_id = created["list_id"]
    schema = created["list_metadata"]["schema"]
    columns = {col["key"]: col["id"] for col in schema}
    options = {}
    for col in schema:
        for choice in ((col.get("options") or {}).get("choices") or []):
            options[choice["label"].lower()] = choice["value"]
    print("Created the List %s with %d columns." % (list_id, len(columns)))

    hire_pool, owner_pool = people()
    hires, owners = {}, {}
    rows = list(csv.DictReader(SEED.open()))
    made = 0
    for number, row in enumerate(rows, start=2):
        fields = [{"column_id": columns["step"], "rich_text": lists.text_cell(row["step"])},
                  {"column_id": columns["status"], "select": lists.select_cell(options["open"])}]

        hire = resolve(row["hire"], hire_pool, hires)
        if hire:
            fields.append({"column_id": columns["hire"], "user": lists.user_cell(hire)})

        owner = resolve(row["owner"], owner_pool, owners)
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

    print("Seeded %d of %d rows." % (made, len(rows)))
    distinct_hires = len(set(hires.values()))
    distinct_owners = len(set(v for v in owners.values() if v))
    print("New hire column uses %d person%s, Owner column uses %d."
          % (distinct_hires, "" if distinct_hires == 1 else "s", distinct_owners))
    if distinct_hires == 1 and distinct_owners == 1:
        print("That is normal on a one person workspace. Set SEED_HIRES to a "
              "couple of user ids if you want the cohort to look like a cohort.")
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
