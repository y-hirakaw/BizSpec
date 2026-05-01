<!--
Thanks for sending a PR! Please fill out the sections below.
For trivial changes (typos, doc-only fixes), feel free to keep it short.
-->

## Summary

<!-- One or two sentences: what does this PR change, and why? -->

## Related issue

<!-- Closes #NNN — or remove this section if there is no linked issue -->

## Changes

<!-- Bulleted list of the substantive changes -->
-
-

## Tests

<!-- How did you verify this? -->
- [ ] Added or updated tests under `tests/`
- [ ] `uv run --with pytest pytest tests/ -v` passes locally
- [ ] `uv run bizspec validate` passes locally
- [ ] N/A — explain why:

## Breaking change

<!-- Does this change CLI behavior, YAML schema, or any public API? -->
- [ ] Yes — described in the Summary
- [ ] No

## Checklist

- [ ] Followed the conventions in [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] Updated docs (`README.md`, `docs/cli.md`, `docs/yaml-spec.md`) if behavior or schema changed
- [ ] Code is Python 3.9 compatible (no `match`, `tomllib`, `typing.Self`, etc.)
- [ ] If a Claude Code skill was edited, the change is in `src/bizspec/skills/` (the source of truth)
