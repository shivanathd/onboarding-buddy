"""End-to-end check of door two. Real HTTP, real Slack signatures, fake List.

Runs the actual Starlette app under uvicorn on a loopback port and speaks
JSON-RPC to it exactly the way Slackbot would. Nothing is mocked below the
transport, so a broken tool schema or a broken signature gate fails here.
"""
import hashlib
import hmac
import json
import os
import pathlib
import sys
import threading
import time

# Run me from anywhere: python mcp_server/test_mcp.py
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

SECRET = "test-signing-secret"
os.environ.update({
    "SLACK_SIGNING_SECRET": SECRET,
    "SLACK_BOT_TOKEN": "xoxb-fake",
    "SLACK_APP_TOKEN": "xapp-fake",
    "CHANNEL_ID": "C1", "MANAGER_ID": "U1", "LIST_ID": "F1",
    "COL_STEP": "c_step", "COL_HIRE": "c_hire", "COL_OWNER": "c_owner",
    "COL_DUE": "c_due", "COL_STATUS": "c_status", "COL_THREAD": "c_thread",
    "PORT": "8765", "MCP_TOOL_TIMEOUT_MS": "10000",
})

import httpx
import uvicorn

from mcp_server import hires, server


# ------------------------------------------------------------- the fake List
def _row(step, hire, owner, due, status, hire_as_person=False):
    """hire_as_person mirrors the live List, which holds the new hire as a
    person reference rather than text. Reading that cell with a text reader
    returns '' and silently drops the row, which is exactly what happened."""
    hire_cell = ({"column_id": "c_hire", "user": [hire]} if hire_as_person
                 else {"column_id": "c_hire", "text": hire})
    return {"fields": [
        {"column_id": "c_step", "text": step},
        hire_cell,
        {"column_id": "c_owner", "user": [owner]},
        {"column_id": "c_due", "date": [due]},
        {"column_id": "c_status", "select": [status]},
    ]}


ROWS = [
    _row("Laptop delivery", "Priya Nair", "U_ARJUN", "2026-09-02", "done"),
    _row("Email account", "Priya Nair", "U_ARJUN", "2026-09-03", "done"),
    _row("Security training", "Priya Nair", "U_ARJUN", "2026-09-05", "open"),
    _row("Access badge", "Omar Farouk", "U_LENA", "2026-08-25", "escalated"),
    _row("Manager intro", "Omar Farouk", "U_LENA", "2026-08-28", "open"),
    _row("Laptop delivery", "Sana Iqbal", "U_ARJUN", "2026-08-10", "done"),
    # the live-List shape: hire held as a person, not text
    _row("Laptop delivery", "U_TARIQ", "U_LENA", "2026-09-01", "done", hire_as_person=True),
    _row("Email account", "U_TARIQ", "U_LENA", "2026-09-04", "open", hire_as_person=True),
]
NAMES = {"U_ARJUN": "Arjun Rao", "U_LENA": "Lena Kruger", "U_TARIQ": "Tariq Hassan"}


class WriteAttempted(AssertionError):
    """Raised if door two ever reaches for a write method. It must not."""


class FakeWeb:
    """Reads answer; every write method detonates.

    tools/lists.py binds the whole surface eagerly, so the write methods have
    to exist. Making them raise turns 'this server is read-only' from a claim
    in a description string into something the test suite can falsify.
    """

    def slackLists_items_list(self, **kw):
        return {"items": ROWS}

    def users_info(self, user):
        return {"user": {"profile": {"real_name": NAMES[user]}}}

    def slackLists_create(self, **kw):
        raise WriteAttempted("slackLists.create")

    def slackLists_items_create(self, **kw):
        raise WriteAttempted("slackLists.items.create")

    def slackLists_items_update(self, **kw):
        raise WriteAttempted("slackLists.items.update")


hires._web = FakeWeb()

# ------------------------------------------------------------------ the server
app = server.build_app()
config = uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="error")
uv = uvicorn.Server(config)
threading.Thread(target=uv.run, daemon=True).start()
for _ in range(100):
    if uv.started:
        break
    time.sleep(0.05)

BASE = "http://127.0.0.1:8765"
HDRS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def signed(body: bytes):
    ts = str(int(time.time()))
    base = b"v0:" + ts.encode() + b":" + body
    sig = "v0=" + hmac.new(SECRET.encode(), base, hashlib.sha256).hexdigest()
    return {**HDRS, "X-Slack-Request-Timestamp": ts, "X-Slack-Signature": sig}


def rpc(client, method, params=None, _id=1, sign=True):
    body = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method,
                       "params": params or {}}).encode()
    headers = signed(body) if sign else HDRS
    r = client.post(f"{BASE}/mcp", content=body, headers=headers)
    return r


def parse(r):
    """Streamable HTTP may answer as JSON or as a one-event SSE frame."""
    text = r.text
    if text.startswith("event:") or text.startswith("data:"):
        for line in text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
    return r.json()


PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  PASS  " if cond else "  FAIL  ") + name + (("  <- " + str(detail)) if not cond else ""))


with httpx.Client(timeout=20) as c:
    # S1.3 health
    r = c.get(f"{BASE}/healthz")
    check("S1.3 healthz 200 {'ok':true}", r.status_code == 200 and r.json() == {"ok": True}, r.text)

    # S2.1 auth: unsigned is refused
    r = rpc(c, "initialize", sign=False)
    check("S2.1 unsigned POST /mcp -> 401", r.status_code == 401 and r.json() == {"error": "unauthorized"}, f"{r.status_code} {r.text[:120]}")

    # S2.1 auth: tampered signature is refused
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}).encode()
    bad = {**HDRS, "X-Slack-Request-Timestamp": str(int(time.time())), "X-Slack-Signature": "v0=deadbeef"}
    r = c.post(f"{BASE}/mcp", content=body, headers=bad)
    check("S2.1 bad signature -> 401", r.status_code == 401, r.status_code)

    # initialize (signed)
    r = rpc(c, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "slackbot-test", "version": "1"}})
    init = parse(r)
    check("initialize succeeds", r.status_code == 200 and "result" in init, r.text[:200])

    sid = r.headers.get("mcp-session-id")
    extra = {"Mcp-Session-Id": sid} if sid else {}

    def rpc2(method, params=None, _id=2):
        body = json.dumps({"jsonrpc": "2.0", "id": _id, "method": method,
                           "params": params or {}}).encode()
        return c.post(f"{BASE}/mcp", content=body, headers={**signed(body), **extra})

    # S1.2 GET and DELETE on /mcp are not the transport's business.
    # Read the status without draining the body: a GET that the server chooses
    # to answer as a stream would otherwise hang the client here.
    for verb in ("GET", "DELETE"):
        with c.stream(verb, f"{BASE}/mcp", headers={**signed(b""), **extra}) as rr:
            code = rr.status_code
        check(f"S1.2 {verb} /mcp -> 405", code == 405, code)

    # S1.1 tools/list
    r = rpc2("tools/list")
    listed = parse(r)
    names = sorted(t["name"] for t in listed.get("result", {}).get("tools", []))
    check("S1.1 tools/list == the three tools",
          names == ["get_onboarding_status", "get_onboarding_summary", "list_new_hires"], names)

    ann = {t["name"]: (t.get("annotations") or {}) for t in listed.get("result", {}).get("tools", [])}
    check("all three carry readOnlyHint:true",
          all(a.get("readOnlyHint") is True for a in ann.values()) and len(ann) == 3, ann)
    check("no tool name implies a write",
          not any(w in n for n in names for w in ("create", "update", "delete", "set_", "write")), names)

    # S3.1 list_new_hires
    r = rpc2("tools/call", {"name": "list_new_hires", "arguments": {"status": "all"}})
    res = parse(r)["result"]
    sc = res.get("structuredContent", {})
    check("S3.1 list_new_hires counts 4 hires", sc.get("count") == 4, sc)
    priya = next((h for h in sc.get("new_hires", []) if h["name"] == "Priya Nair"), {})
    check("S3.1 Priya 2/3 steps, onboarding, buddy resolved",
          priya.get("steps_done") == 2 and priya.get("steps_total") == 3
          and priya.get("status") == "onboarding" and priya.get("buddy") == "Arjun Rao", priya)
    omar = next((h for h in sc.get("new_hires", []) if h["name"] == "Omar Farouk"), {})
    check("escalated step -> hire status blocked", omar.get("status") == "blocked", omar)
    sana = next((h for h in sc.get("new_hires", []) if h["name"] == "Sana Iqbal"), {})
    check("all steps done -> hire status done", sana.get("status") == "done", sana)
    check("next_due skips completed steps", priya.get("next_due") == "2026-09-05", priya.get("next_due"))
    check("content carries a plain sentence",
          "Priya Nair" in json.dumps(res.get("content")), res.get("content"))

    tariq = next((h for h in sc.get("new_hires", []) if h["name"] == "Tariq Hassan"), {})
    check("person-column hire is read, not silently dropped",
          tariq.get("steps_total") == 2 and tariq.get("steps_done") == 1, tariq)

    # filter
    r = rpc2("tools/call", {"name": "list_new_hires", "arguments": {"status": "blocked"}})
    sc = parse(r)["result"]["structuredContent"]
    check("status filter works", sc.get("count") == 1 and sc["new_hires"][0]["name"] == "Omar Farouk", sc)

    # S3.2 case-insensitive hit
    r = rpc2("tools/call", {"name": "get_onboarding_status", "arguments": {"new_hire": "pRiYa nAiR"}})
    sc = parse(r)["result"]["structuredContent"]
    check("S3.2 case-insensitive match found", sc.get("found") is True, sc)

    # S3.2 miss is an answer, not an error
    r = rpc2("tools/call", {"name": "get_onboarding_status", "arguments": {"new_hire": "Priya Nayar"}})
    res = parse(r)["result"]
    sc = res["structuredContent"]
    check("S3.2 miss: found=false, isError absent/false, hints given",
          sc.get("found") is False and not res.get("isError") and sc.get("closest") == ["Priya Nair"], res)

    # summary
    r = rpc2("tools/call", {"name": "get_onboarding_summary", "arguments": {}})
    sc = parse(r)["result"]["structuredContent"]
    check("summary rollup correct",
          sc.get("total") == 4 and sc["by_status"] == {"onboarding": 2, "blocked": 1, "done": 1}, sc)

    # S3.3 upstream failure -> tool error, not a dead transport
    class Broken(FakeWeb):
        def slackLists_items_list(self, **kw):
            raise RuntimeError("invalid_auth")

    good, hires._web = hires._web, Broken()
    started = time.monotonic()
    r = rpc2("tools/call", {"name": "list_new_hires", "arguments": {}})
    elapsed = time.monotonic() - started
    res = parse(r)["result"]
    check("S3.3 upstream failure -> isError, HTTP still 200",
          r.status_code == 200 and res.get("isError") is True, res)
    check("S3.3 fails inside 11s", elapsed < 11, elapsed)
    hires._web = good

    # unknown tool
    r = rpc2("tools/call", {"name": "delete_everything", "arguments": {}})
    out = parse(r)
    check("unknown tool -> standard error, transport healthy",
          r.status_code == 200 and ("error" in out or out.get("result", {}).get("isError")), out)

    # bad input rejected by schema
    r = rpc2("tools/call", {"name": "get_onboarding_status", "arguments": {"new_hire": "x"}})
    out = parse(r)
    check("input validation rejects too-short name",
          "error" in out or out.get("result", {}).get("isError"), out)

# S2.2 boot guard: no signing secret -> no /mcp, worker unaffected. Served for
# real on a second port, because "is it mounted" is a behaviour, not a field.
server.SIGNING_SECRET = ""
guard = uvicorn.Server(uvicorn.Config(server.build_app(), host="127.0.0.1",
                                      port=8766, log_level="error"))
threading.Thread(target=guard.run, daemon=True).start()
for _ in range(100):
    if guard.started:
        break
    time.sleep(0.05)
with httpx.Client(timeout=10) as c:
    h = c.get("http://127.0.0.1:8766/healthz")
    m = c.post("http://127.0.0.1:8766/mcp", content=b"{}", headers=HDRS)
    check("S2.2 no secret -> /healthz 200 and /mcp 404 (worker unaffected)",
          h.status_code == 200 and m.status_code == 404, f"healthz={h.status_code} mcp={m.status_code}")

print("\n%d passed, %d failed" % (len(PASS), len(FAIL)))
if FAIL:
    print("FAILED: " + ", ".join(FAIL))
raise SystemExit(1 if FAIL else 0)
