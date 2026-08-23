"""The brain.

The smallest file in this repo, on purpose. The room expects the model to be
the big part. It is one function, and swapping it is one line in .env.

Two rules hold everywhere:
  the model is asked nothing until the List read has already succeeded, and
  a brain failure never blocks a state write. It degrades to a template.
"""

import os

from anthropic import Anthropic

client = None  # built on first use, so this module imports with no key present


def ask(brief, context, question, fallback=None):
    """One call. Returns text, and never raises."""
    global client
    try:
        client = client or Anthropic(timeout=20.0, max_retries=1)
        reply = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", ""),
            max_tokens=400,
            system=brief,
            messages=[{"role": "user", "content": "%s\n\nQuestion: %s" % (context, question)}],
        )
        parts = [b.text for b in reply.content if getattr(b, "type", "text") == "text"]
        return "\n".join(parts).strip() or fallback or context
    except Exception as problem:
        print("brain: %s. Falling back to a template." % problem, flush=True)
        return fallback or ("I could not compose an answer just now. "
                            "Here is the raw state:\n%s" % context)
