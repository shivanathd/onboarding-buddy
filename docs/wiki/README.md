# How a Slack digital worker was built

A knowledge base covering how `onboarding-buddy` was specified, built, proven and debugged: the
setup path, the undocumented Slack behaviour found by calling the API, every decision and its
reasoning, and the defects a fully green test suite did not catch.

Start at [bundle/index.md](bundle/index.md).

This sits in `docs/wiki/` rather than at the repository root on purpose. The root tree is meant
to be readable in one sitting, and a knowledge base this size would drown it.

## Related reading in this repository

- `README.md` at the root: the fifteen minute quickstart.
- `docs/how-this-was-built.md`: the same story as narrative, in the order it happened.
- `docs/provisioning-without-a-browser.md`: the headless provisioning path.

## What format this is

Open Knowledge Format (OKF): small markdown files, one concept each, with provenance in YAML
frontmatter and `index.md` files for navigation. A validator enforces the contract so the base
stays consistent as it grows. `SPEC.md` is the full format contract.

Every concept carries seven required keys: `type`, `title`, `description`, `source`, `verified`,
`timestamp` and `tags`. `verified` is the date the fact was last confirmed true; `timestamp` is
when the file was authored. Everything here was confirmed against a live Slack workspace on
2026-08-23.

## Validate

The validator parses YAML frontmatter with PyYAML:

```bash
pip install -r requirements.txt    # or: pip install pyyaml
python3 scripts/validate.py --bundle bundle
```

It must exit 0. Run it before every commit.

## Add a concept

1. Create `bundle/<section>/<concept>.md` with the required frontmatter.
2. Add a bullet for it in that section's `index.md`.
3. Cross link related concepts with relative markdown links. The `[[slug]]` form is rejected.
4. Validate.

## House rules for this bundle

Two constraints come from the repository's own test suite, which walks every Python, markdown,
text, JSON, shell and CSV file in the tree:

- **No em dashes and no en dashes anywhere.** Use a comma, a full stop, or a rewording.
- **No real identifiers.** No token, channel, user, file, List, column, team or app identifier,
  and no workspace or person name. Placeholder shapes such as `C0000000000` and `Col0000000000`
  are how a shape gets shown.

Both are enforced by the repository check, not by the OKF validator, so a passing validation run
does not prove either. Check them yourself before committing.

## Security

Never put a secret value in a concept. A credential concept documents the key name and where it
is retrieved, never the value. The validator scans for leaked secrets and fails on a hit.
