"""The only crosser of the Lists boundary.

Every Lists call in this repo goes through this file. No job file calls a
slackLists method directly, so if Slack changes a shape, one file changes.

Two things here are easy to get wrong and expensive to debug:

1. Text cells must be rich_text block arrays. A plain string is rejected. One
   helper builds that shape and everything reuses it.
2. Columns are addressed by opaque column_id, not by name. bootstrap.py prints
   the mapping once so nobody has to guess.

Date cells are arrays of YYYY-MM-DD strings.
"""

import datetime


class _Group:
    """Turns a flat set of methods into a dotted path, so calls in this file
    read the way the API reference does: slackLists.items.list."""

    def __init__(self, **members):
        self.__dict__.update(members)


def lists_client(web_client):
    """Present slack_sdk's underscored methods as the dotted API shape.

    slack_sdk exposes slackLists_items_list. The documentation, and every
    example anyone will read, calls it slackLists.items.list. This adapter keeps
    the code looking like the docs. See ADR-B2.
    """
    return _Group(
        slackLists=_Group(
            create=web_client.slackLists_create,
            items=_Group(
                create=web_client.slackLists_items_create,
                update=web_client.slackLists_items_update,
                list=web_client.slackLists_items_list,
            ),
        )
    )


# ----------------------------------------------------------------- cell shapes

def text_cell(value):
    """Wrap a plain string in the rich_text block array a text cell needs."""
    return [{
        "type": "rich_text",
        "elements": [{
            "type": "rich_text_section",
            "elements": [{"type": "text", "text": str(value)}],
        }],
    }]


def date_cell(value):
    """A date cell is an array of YYYY-MM-DD strings."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        value = value.strftime("%Y-%m-%d")
    return [value]


def user_cell(user_id):
    return [user_id]


def select_cell(option_id):
    return [option_id]


# --------------------------------------------------------------------- reading

def list_items(client, list_id):
    """Every row, following next_cursor until it runs out.

    Pagination lives here and nowhere else.
    """
    rows = []
    cursor = None
    while True:
        params = {"list_id": list_id, "limit": 100}
        if cursor:
            params["cursor"] = cursor
        page = client.slackLists.items.list(**params)
        rows.extend(page.get("items") or [])
        cursor = (page.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            return rows


def field(item, column_id):
    """One cell, or None. An empty cell is absent entirely, never an error."""
    for cell in item.get("fields") or []:
        if cell.get("column_id") == column_id:
            return cell
    return None


def text_of(item, column_id):
    """The plain string in a text cell, or an empty string when the cell is
    missing. Reads both the flat text property and the rich_text array."""
    cell = field(item, column_id)
    if not cell:
        return ""
    if cell.get("text"):
        return cell["text"]
    for block in cell.get("rich_text") or []:
        for section in block.get("elements") or []:
            for piece in section.get("elements") or []:
                if piece.get("text"):
                    return piece["text"]
    return ""


def find_by_text(items, column_id, value):
    """The row whose text cell equals value, or None.

    This is how the loop closes. chase writes a message ts into the Thread cell,
    and later a reaction on that message finds its way back to this row.
    """
    if not value:
        return None
    for item in items:
        if text_of(item, column_id) == value:
            return item
    return None


def date_of(item, column_id):
    """A date object, or None when the cell is empty. No grace math runs on an
    unknown date, so None is a valid answer and not a failure."""
    cell = field(item, column_id)
    values = (cell or {}).get("date") or []
    if not values:
        return None
    try:
        return datetime.datetime.strptime(values[0], "%Y-%m-%d").date()
    except ValueError:
        return None


def first_user(item, column_id):
    """The first user id in a user cell, or an empty string when unassigned."""
    cell = field(item, column_id)
    values = (cell or {}).get("user") or []
    return values[0] if values else ""


def select_value(item, column_id):
    """The raw option value in a select cell, for example open or escalated."""
    cell = field(item, column_id)
    values = (cell or {}).get("select") or []
    return values[0] if values else ""


def select_label(item, column_id, options):
    """A select cell holds option ids. Map one back to its label."""
    cell = field(item, column_id)
    values = (cell or {}).get("select") or []
    return options.get(values[0], "") if values else ""


# --------------------------------------------------------------------- writing

def create_list(client, name, schema):
    """Create the List. Never pass copy_from_list_id alongside a schema."""
    return client.slackLists.create(name=name, schema=schema)


def create_item(client, list_id, initial_fields):
    """Add one row. Every entry in initial_fields is keyed by column_id."""
    return client.slackLists.items.create(list_id=list_id, initial_fields=initial_fields)


def update_cells(client, list_id, row_id, cells):
    """Update cells on one row. Jobs only ever touch Status, Due, and Thread."""
    payload = [dict(cell, row_id=row_id) for cell in cells]
    return client.slackLists.items.update(list_id=list_id, cells=payload)
