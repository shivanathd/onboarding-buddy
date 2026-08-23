"""The brain.

The smallest file in this repo, on purpose. The room expects the model to be
the big part. It is one function, and swapping it is one line in .env.

Two rules hold everywhere: the model is asked nothing until the List read has
already succeeded, and a brain failure never blocks a state write.

One thing worth knowing: the model thinks before it writes, and that thinking
comes out of the same token budget. Set the ceiling too low and you get a
perfectly successful call carrying no words. Ask for brevity in the prompt
instead.
"""

import os

from anthropic import Anthropic

client = None  # built on first use, so this module imports with no key present


def ask(brief, context, question, fallback=None):
    """One call. Returns text, and never raises."""
    global client
    try:
        client = client or Anthropic(timeout=30.0, max_retries=1)
        reply = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", ""),
            max_tokens=1200,
            system=brief + " Never use a dash to join clauses. Use a comma or a full stop.",
            messages=[{"role": "user", "content": "%s\n\nQuestion: %s" % (context, question)}],
        )
        said = "".join(b.text for b in reply.content if getattr(b, "type", "text") == "text")
        said = said.replace(chr(8212), ",").replace(chr(8211), ",").strip()
        if not said:
            print("brain: a successful call carried no text, stop reason %s. Using a template."
                  % getattr(reply, "stop_reason", "unknown"), flush=True)
        return said or fallback or context
    except Exception as problem:
        print("brain: %s. Falling back to a template." % problem, flush=True)
        return fallback or ("I could not compose an answer just now. "
                            "Here is the raw state:\n%s" % context)
