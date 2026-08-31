"""Door two. The same worker, reachable by Slackbot's MCP client.

Door one is Socket Mode: Bolt dials out, handles mentions, reactions, buttons
and the clock. Door two is this: an HTTP listener serving POST /mcp over the
MCP streamable HTTP transport, plus GET /healthz for the morning-of curl.

Three rules this file exists to enforce:

1. Read only. There is no write tool and no code path here that can create,
   update or delete anything. The capability boundary is the shape of the
   module, not a sentence in a prompt.
2. Slack signs every request it sends, whatever the auth type. We verify that
   signature and refuse everything else. A static bearer token is not one of
   the four auth types Slack supports, so there is none here.
3. A failure in this file must never take the worker down. Door one is the
   payload; door two is the extension.
"""

import logging
import os
import threading
import time
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from slack_sdk.signature import SignatureVerifier
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from mcp_server import hires

log = logging.getLogger("mcp")

SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "").strip()
TOOL_TIMEOUT = float(os.environ.get("MCP_TOOL_TIMEOUT_MS", "10000")) / 1000.0
PORT = int(os.environ.get("PORT", "3000"))


def _timed(name, fn):
    """Run one tool call under a deadline and one log line.

    Errors are raised, not swallowed: the SDK turns an exception into a tool
    result carrying is_error, which the model can read and recover from. A
    transport-level 500 would end the reasoning chain instead.
    """
    started = time.monotonic()
    deadline = started + TOOL_TIMEOUT
    try:
        text, structured = fn(deadline)
    except Exception as exc:
        log.info("tool %s error %dms", name, (time.monotonic() - started) * 1000)
        raise RuntimeError("onboarding-buddy: could not read the onboarding List "
                           "(%s)" % exc) from exc
    log.info("tool %s ok %dms", name, (time.monotonic() - started) * 1000)
    # Hand back both halves explicitly. Returning a plain dict lets the SDK
    # build the unstructured content itself, which means dumping the whole
    # payload into the text block as JSON. The text block is what the model
    # quotes into the panel answer, so it has to be the sentence.
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        structuredContent=structured,
    )


def build_server():
    """The three tools, with the descriptions the model plans against.

    read_only_hint matters more than it looks. Slackbot asks the user to
    approve each tool call, and an unclassified tool defaults to the write
    classification, so an unhinted read would put a confirmation dialog in
    front of every question on stage.
    """
    server = MCPServer(name="onboarding-buddy", version="1.0.0")
    read_only = ToolAnnotations(read_only_hint=True, destructive_hint=False,
                                idempotent_hint=True, open_world_hint=False)

    @server.tool(
        name="list_new_hires",
        title="List new hires",
        description="Read-only. Lists new hires from the Mindcat onboarding List: "
                    "name, buddy, status, and how many onboarding steps are done. "
                    "Cannot modify anything.",
        annotations=read_only,
        structured_output=True,
    )
    def list_new_hires(status: str = "all", limit: int = 20) -> dict[str, Any]:
        """Filter by derived status. 'all' returns every hire."""
        if status not in ("all", "onboarding", "done", "blocked"):
            raise ValueError("status must be one of: all, onboarding, done, blocked")
        limit = max(1, min(int(limit), 50))
        return _timed("list_new_hires",
                      lambda d: hires.list_new_hires(status, limit, d))

    @server.tool(
        name="get_onboarding_status",
        title="Get one new hire's onboarding status",
        description="Read-only. Returns one new hire's onboarding detail by name: "
                    "buddy, status, step progress, next due date. "
                    "Cannot modify anything.",
        annotations=read_only,
        structured_output=True,
    )
    def get_onboarding_status(new_hire: str) -> dict[str, Any]:
        """Full name as it appears in the List. Case-insensitive exact match."""
        if not new_hire or len(new_hire.strip()) < 2:
            raise ValueError("new_hire must be at least 2 characters")
        return _timed("get_onboarding_status",
                      lambda d: hires.get_onboarding_status(new_hire, d))

    @server.tool(
        name="get_onboarding_summary",
        title="Onboarding rollup",
        description="Read-only. Counts of new hires by onboarding status. "
                    "Cannot modify anything.",
        annotations=read_only,
        structured_output=True,
    )
    def get_onboarding_summary() -> dict[str, Any]:
        """A rollup, so a question about the cohort does not pull every row."""
        return _timed("get_onboarding_summary",
                      lambda d: hires.get_onboarding_summary(d))

    return server


class SlackSignedOnly:
    """ASGI middleware. Nothing reaches /mcp without a valid Slack signature.

    Slack signs every request to an MCP server regardless of the configured
    auth type, so this is the gate for all of them. The body has to be buffered
    to compute the signature and then replayed downstream, which is why this is
    raw ASGI rather than a Starlette BaseHTTPMiddleware.
    """

    def __init__(self, app, verifier, protect="/mcp"):
        self.app = app
        self.verifier = verifier
        self.protect = protect

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith(self.protect):
            return await self.app(scope, receive, send)

        # REQ-BUDDY-002. Stateless JSON mode answers every call on the POST, so
        # the SDK's GET handler only opens an SSE stream nothing will ever read.
        # Refusing it here keeps idle streams off the service entirely.
        if scope.get("method") not in ("POST",):
            response = JSONResponse({"error": "method_not_allowed"}, status_code=405)
            return await response(scope, receive, send)

        body = b""
        while True:
            message = await receive()
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

        headers = {k.decode("latin-1").lower(): v.decode("latin-1")
                   for k, v in scope.get("headers", [])}
        try:
            ok = self.verifier.is_valid(
                body=body,
                timestamp=headers.get("x-slack-request-timestamp", ""),
                signature=headers.get("x-slack-signature", ""),
            )
        except Exception:
            # A missing or malformed header is a failed check, not a crash.
            # Without this, an unsigned probe gets a 500 and learns that the
            # headers are parsed before they are compared.
            ok = False
        if not ok:
            # Fail closed and say nothing useful. No hint about what was wrong.
            response = JSONResponse({"error": "unauthorized"}, status_code=401)
            return await response(scope, receive, send)

        replayed = False

        async def replay():
            nonlocal replayed
            if replayed:
                return {"type": "http.disconnect"}
            replayed = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay, send)


async def _healthz(_request):
    return JSONResponse({"ok": True})


def build_app():
    """The ASGI app: /healthz always, /mcp only when configured.

    The endpoint is a route on the MCP app itself, not a Mount. A Mount would
    make Starlette answer POST /mcp with a 307 to /mcp/, and a redirect on the
    hot path is a coin flip on whether the client re-POSTs the body.
    """
    if not SIGNING_SECRET:
        log.warning("MCP: SLACK_SIGNING_SECRET unset, /mcp not mounted. Buddy runs on.")
        return Starlette(routes=[Route("/healthz", _healthz, methods=["GET"])])

    server = build_server()
    # Railway terminates TLS at a public domain we cannot know at build time,
    # and the only caller is Slack, whose signature we verify below. Host
    # checking here would reject Railway's own domain for no added safety.
    app = server.streamable_http_app(
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
        max_request_body_size=256 * 1024,
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    )
    app.routes.insert(0, Route("/healthz", _healthz, methods=["GET"]))
    return SlackSignedOnly(app, SignatureVerifier(SIGNING_SECRET), protect="/mcp")


def serve_forever():
    """Blocking. Run this on a thread; Socket Mode owns the main one."""
    import uvicorn
    uvicorn.run(build_app(), host="0.0.0.0", port=PORT, log_level="warning")


def start_in_background():
    """Never let door two stop door one from opening."""
    try:
        thread = threading.Thread(target=serve_forever, name="mcp", daemon=True)
        thread.start()
        print("MCP: listening on :%d - door two open" % PORT, flush=True)
    except Exception as exc:  # pragma: no cover - refuses to be fatal
        print("MCP: failed to start (%s). Buddy runs on." % exc, flush=True)
