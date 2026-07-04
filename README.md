# Megatect

Megatect is an evidence-backed software architecture skill for AI coding agents. It combines repository inventory, dependency graphing, boundary checks, risk scorecards, pattern-fit analysis, ADR helpers, and concise architecture references.

The architecture rubrics are original summaries informed by Mark Richards' `Software Architecture Patterns` and Robert C. Martin's `Clean Architecture: A Craftsman's Guide to Software Structure and Design`, plus practical architecture best-practice material. The books are attributed as source material; their PDFs and long excerpts are not included.

Use Megatect when you want an agent to inspect a real codebase before recommending architecture changes, choosing between modular monolith, layered, clean architecture, event-driven, microkernel, microservices, or space-based styles, or writing architecture plans grounded in code evidence.

## Features

- Repository inventory: detects stack signals, source files, API routes, workers, schemas, integrations, package/config files, and docs.
- Architecture graphs: generates a whole-repo dependency graph, per-system graphs, a meta-system graph, and `architecture-index.json`.
- Portable graph formats: writes DOT (`.dot`) and Mermaid (`.mmd`) files; rendered output can be generated when local renderers are available.
- Boundary checks: reports cycles and deep cross-system imports, optionally using an `architecture-boundaries.json` config.
- Risk scorecards: summarizes coupling, hubs, system count, graph edges, API routes, workers, schemas, and integration pressure.
- Pattern fit: recommends whether modular monolith, layered, clean architecture, event-driven, microkernel, microservices, or space-based architecture fits the evidence.
- ADR helpers: creates and checks concise Architecture Decision Records.
- Source-derived references: includes compact rubrics for architecture patterns, Clean Architecture principles, practical best practices, and pattern selection.

## Install

### Codex

Clone this repo into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Kassden/megatect.git ~/.codex/skills/megatect
```

Restart Codex or start a new session, then ask for `$megatect` or use architecture prompts that match the skill description in `SKILL.md`.

If you already have Megatect installed and want repo updates to update the live skill:

```bash
cd ~/.codex/skills/megatect
git pull
```

### Other AI Coding Agents

Use `SKILL.md` as the entrypoint instructions. Keep `references/` and `scripts/` beside it so the agent can load the rubrics and run deterministic checks.

For agents without native skill discovery, paste or reference:

```text
Use the Megatect skill in this repository. Read SKILL.md first, then use the scripts and references it routes to.
```

## Quick Start

Run commands from the Megatect folder:

```bash
cd ~/.codex/skills/megatect
```

Set the repository you want to analyze:

```bash
REPO=/path/to/your/repo
OUT=/tmp/megatect-output
mkdir -p "$OUT/architecture" "$OUT/architecture-graphs"
```

Create an inventory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_inventory.py "$REPO" \
  --out "$OUT/architecture/inventory.json"
```

Generate dependency graphs and the graph index:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_diagrams.py "$REPO" \
  --out "$OUT/architecture-graphs"
```

Use source-only graph output when renderer tools are unavailable or unnecessary:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_diagrams.py "$REPO" \
  --out "$OUT/architecture-graphs" \
  --no-render
```

Run a boundary check:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_boundary_check.py "$REPO" \
  --index "$OUT/architecture-graphs/architecture-index.json" \
  --out "$OUT/architecture/boundary-report.json"
```

Generate a risk scorecard:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_scorecard.py \
  --index "$OUT/architecture-graphs/architecture-index.json" \
  --inventory "$OUT/architecture/inventory.json" \
  --json-out "$OUT/architecture/scorecard.json" \
  --md-out "$OUT/architecture/scorecard.md"
```

Recommend architecture pattern fit:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_pattern_fit.py \
  --inventory "$OUT/architecture/inventory.json" \
  --scorecard "$OUT/architecture/scorecard.json" \
  --out "$OUT/architecture/pattern-fit.json"
```

Create an ADR:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_adr.py create \
  "Use modular monolith boundaries" \
  --context "The repo has coupled systems but no proven independent deployment pressure." \
  --decision "Keep one deployable app and enforce package boundaries first." \
  --consequences "Lower operational cost now; revisit service boundaries when ownership or scaling evidence changes." \
  --dir "$REPO/docs/adr"
```

Check ADR files:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_adr.py check "$REPO"/docs/adr/*.md
```

## Script Reference

| Script | Purpose | Main inputs | Main outputs | Example |
| --- | --- | --- | --- | --- |
| `scripts/architecture_inventory.py` | Build a lightweight architecture inventory. | Repo root, optional `--out`. | `inventory.json`. | `python3 scripts/architecture_inventory.py "$REPO" --out "$OUT/architecture/inventory.json"` |
| `scripts/architecture_diagrams.py` | Generate dependency graph sources and index files. | Repo root, optional `--out`, `--systems-root`, `--no-render`, `--self-test`. | `architecture-index.json`, `.dot`, `.mmd`, optional rendered files. | `python3 scripts/architecture_diagrams.py "$REPO" --out "$OUT/architecture-graphs" --no-render` |
| `scripts/architecture_boundary_check.py` | Check cycles and boundary violations from graph evidence. | Repo root, `--index`, optional `--config`, optional `--out`. | `boundary-report.json` plus console summary. | `python3 scripts/architecture_boundary_check.py "$REPO" --index "$OUT/architecture-graphs/architecture-index.json" --out "$OUT/architecture/boundary-report.json"` |
| `scripts/architecture_scorecard.py` | Produce an architecture risk scorecard. | `--index`, `--inventory`, output paths. | `scorecard.json`, `scorecard.md`. | `python3 scripts/architecture_scorecard.py --index "$OUT/architecture-graphs/architecture-index.json" --inventory "$OUT/architecture/inventory.json" --json-out "$OUT/architecture/scorecard.json" --md-out "$OUT/architecture/scorecard.md"` |
| `scripts/architecture_pattern_fit.py` | Recommend architecture style fit from evidence. | `--inventory`, `--scorecard`, optional `--out`. | `pattern-fit.json`. | `python3 scripts/architecture_pattern_fit.py --inventory "$OUT/architecture/inventory.json" --scorecard "$OUT/architecture/scorecard.json" --out "$OUT/architecture/pattern-fit.json"` |
| `scripts/architecture_adr.py` | Create or check concise ADRs. | `create` or `check` subcommand. | ADR markdown files or validation output. | `python3 scripts/architecture_adr.py create "Decision title" --context "..." --decision "..." --consequences "..." --dir docs/adr` |

## Generated Outputs

Common output files:

- `docs/architecture/inventory.json`: repository inventory and detected stack signals.
- `docs/architecture-graphs/architecture-index.json`: graph index used by boundary checks and scorecards.
- `docs/architecture-graphs/whole-repo.dot`: whole-repo dependency graph in DOT format.
- `docs/architecture-graphs/whole-repo.mmd`: whole-repo dependency graph in Mermaid format.
- `docs/architecture-graphs/meta-systems.dot` and `.mmd`: system-level graph.
- `docs/architecture-graphs/system-*.dot` and `.mmd`: per-system graphs.
- `docs/architecture/boundary-report.json`: cycles and boundary violations.
- `docs/architecture/scorecard.json` and `.md`: machine-readable and human-readable risk scorecards.
- `docs/architecture/pattern-fit.json`: architecture pattern fit recommendations.
- `docs/adr/*.md`: Architecture Decision Records created by the ADR helper.

When testing a dirty repo, write outputs to `/tmp` or another scratch path so generated evidence does not mix with unrelated work:

```bash
OUT=/tmp/megatect-output
```

## Graphs

Megatect graph generation is handled by `scripts/architecture_diagrams.py`.

By default it writes portable source graph files:

- DOT files for Graphviz-compatible tooling.
- Mermaid files for Markdown/rendering workflows.
- `architecture-index.json` for downstream scripts.

Without `--no-render`, the script attempts to render `.dot.svg` with Graphviz `dot` and `.mmd.svg` with `mmdc` or `npx @mermaid-js/mermaid-cli` when those tools are available. Use `--no-render` when you only need source graph files, want to avoid renderer dependencies, or want to avoid an `npx` download.

Run the graph self-test:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_diagrams.py --self-test
```

## Boundary Config

`architecture_boundary_check.py` can run with only a graph index, or with a project-specific config:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_boundary_check.py "$REPO" \
  --index "$OUT/architecture-graphs/architecture-index.json" \
  --config "$REPO/architecture-boundaries.json" \
  --out "$OUT/architecture/boundary-report.json"
```

Use a config when a repo has explicit allowed or forbidden system boundaries. Without a config, the script still reports general cycles and deep cross-system imports from the graph index.

## References

Megatect includes concise reference rubrics:

- `references/software-architecture-patterns.md`: layered, event-driven, microkernel, microservices, and space-based architecture tradeoffs, informed by Mark Richards' `Software Architecture Patterns`.
- `references/clean-architecture-principles.md`: dependency direction, boundaries, component principles, details discipline, services, tests, and packaging enforcement, informed by Robert C. Martin's `Clean Architecture`.
- `references/architecture-best-practices.md`: practical review heuristics synthesized from the source material and the 42 Coffee Cups article.
- `references/pattern-fit-rubric.md`: decision rubric for accepting or rejecting candidate architecture styles.
- `references/source-manifest.md`: provenance notes and local-only source filename expectations.

The source PDFs are not included in this repository. For local verification, keep private source files under `local-sources/`; that folder is ignored by git.

## Validate

Validate the skill package:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/megatect
```

Run script smoke checks:

```bash
cd ~/.codex/skills/megatect
PYTHONDONTWRITEBYTECODE=1 python3 scripts/architecture_diagrams.py --self-test
for f in scripts/*.py; do PYTHONDONTWRITEBYTECODE=1 python3 "$f" --help >/dev/null; done
```

Confirm the public repo does not include private source files:

```bash
find . -name '*.pdf' -o -path './local-sources/*' -o -name '__pycache__' -o -name '*.pyc'
```

That command should print nothing in a clean clone.

## Troubleshooting

- Missing rendered graphs: rerun `architecture_diagrams.py` with `--no-render` and use the generated `.dot` or `.mmd` files directly.
- Empty or tiny graphs: check that `REPO` points at the actual project root and that the repo uses supported source extensions.
- Unexpected boundary violations: inspect `architecture-index.json`, then add or adjust a project-specific `architecture-boundaries.json` if the repo has intentional cross-system edges.
- Dirty target repo: write outputs to `/tmp/megatect-output` instead of `docs/`.
- Python cache files: keep `PYTHONDONTWRITEBYTECODE=1` in validation and smoke-test commands.

## License

MIT
