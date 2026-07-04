# Megatect

Megatect is an evidence-backed software architecture skill for AI coding agents. It combines repository inventory, dependency graphing, boundary checks, scorecards, pattern-fit analysis, ADR helpers, and concise architecture references.

Use it when you want an agent to inspect a real codebase before recommending architecture changes, choosing between modular monolith, layered, clean architecture, event-driven, microkernel, microservices, or space-based styles, or writing architecture plans grounded in code evidence.

## Install

### Codex

Clone or copy this folder into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone <repo-url> ~/.codex/skills/megatect
```

Restart Codex or start a new session, then ask for `$megatect` or use architecture-related prompts that match the skill description in `SKILL.md`.

### Other AI coding agents

Use `SKILL.md` as the entrypoint instructions. Keep `references/` and `scripts/` beside it so the agent can load the rubrics and run deterministic checks.

For agents without native skill discovery, paste or reference:

```text
Use the Megatect skill in this repository. Read SKILL.md first, then use the scripts and references it routes to.
```

## What It Includes

- `SKILL.md`: trigger description and workflow.
- `scripts/architecture_inventory.py`: repository inventory.
- `scripts/architecture_diagrams.py`: dependency graph indexes and DOT/Mermaid diagrams.
- `scripts/architecture_boundary_check.py`: cycle and boundary checks.
- `scripts/architecture_scorecard.py`: architecture risk scorecard.
- `scripts/architecture_pattern_fit.py`: pattern-fit recommendation from evidence.
- `scripts/architecture_adr.py`: concise ADR creation and checks.
- `references/`: concise original architecture rubrics.

## Source References

The bundled references are original summaries and rubrics derived from architecture books and public web material. The source PDFs are not included in this repository. See `references/source-manifest.md`.

For local verification, keep private source files under `local-sources/`; that folder is ignored by git.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_diagrams.py --self-test
for f in scripts/*.py; do PYTHONDONTWRITEBYTECODE=1 python3 "$f" --help >/dev/null; done
```

## License

MIT
