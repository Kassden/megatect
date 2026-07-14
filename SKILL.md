---
name: megatect
description: "Use for evidence-backed software architecture discovery, review, pattern selection, boundary analysis, dependency graphing, scorecards, ADR creation, modularization plans, and clean-architecture guidance. Megatect's rubrics are original summaries informed by Mark Richards' Software Architecture Patterns and Robert C. Martin's Clean Architecture: A Craftsman's Guide to Software Structure and Design, plus practical architecture best-practice material. Trigger when Codex is asked to act as an architect, improve architecture, choose between modular monolith, layered, clean architecture, event-driven, microkernel, microservices, or space-based patterns, write ADRs, analyze coupling, define bounded contexts, generate architecture diagrams, or create architecture plans grounded in real code evidence."
---

# Megatect

Use Megatect as the high-rigor architecture skill. Keep the original `architect` skill as v1; this skill is the heavier v2 path with scripted evidence.

## Core Rule

Inspect the repository before judging it. Prefer the canonical context pack when it exists and is fresh enough; otherwise use scripts for inventory, graphs, boundaries, scorecards, pattern fit, context packing, and ADRs. Use the references for architecture judgment only after repo evidence exists.

## Workflow

1. **Check canonical context first**
   - If `docs/architecture/CONTEXT.md` and `docs/architecture/context-manifest.json` exist, run `scripts/architecture_context_check.py <repo>`.
   - If freshness is `fresh` or `usable-with-drift`, read `CONTEXT.md` first and inspect only changed or task-specific files.
   - If freshness is `needs-light-refresh`, use `CONTEXT.md` as a baseline, inspect the changed entrypoint/config/dependency files, and refresh the context pack when cheap.
   - If freshness is `needs-full-refresh`, regenerate Megatect artifacts before relying on `CONTEXT.md`.

2. **Inventory the repo**
   - Run `scripts/architecture_inventory.py <repo> --out docs/architecture/inventory.json`.
   - Read existing `ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `docs/**`, package scripts, schema/config files, workers, API routes, and integration surfaces.

3. **Generate graph evidence**
   - Run `scripts/architecture_diagrams.py <repo> --out docs/architecture-graphs`.
   - Use `--no-render` when SVG rendering is unnecessary or blocked.
   - Inspect `architecture-index.json` for systems, edges, cycles, and hubs.

4. **Check boundaries**
   - If a repo has `architecture-boundaries.json`, run `scripts/architecture_boundary_check.py <repo> --config architecture-boundaries.json`.
   - If no config exists, use the script without config to detect cycles and deep cross-system imports.

5. **Score architecture risk**
   - Run `scripts/architecture_scorecard.py --index docs/architecture-graphs/architecture-index.json --inventory docs/architecture/inventory.json`.
   - Treat the scorecard as evidence, not a verdict. Confirm with code reads.

6. **Choose pattern fit**
   - Run `scripts/architecture_pattern_fit.py --inventory docs/architecture/inventory.json --scorecard docs/architecture/scorecard.json`.
   - Default to modular monolith unless scaling, isolation, ownership, security, latency, or release-cadence evidence justifies distribution.

7. **Pack canonical context**
   - Run `scripts/architecture_context_pack.py` after inventory, graph, boundary, scorecard, and pattern-fit artifacts exist.
   - Or run `scripts/architecture_context_bootstrap.py <repo>` to create all artifacts and `docs/architecture/CONTEXT.md` in one command.
   - Treat `CONTEXT.md` as the compact architecture baseline for future sessions. It is a token-saving cache, not a replacement for checking drift and relevant changed files.

8. **Produce decisions**
   - For durable decisions, use `scripts/architecture_adr.py create`.
   - For plans, produce phases with small boundary moves, public entrypoints, dependency rules, tests, and verification commands.

## Judgment Rules

- Separate evidence from inference.
- Prefer boundaries before services.
- Treat frameworks, databases, web UI, queues, and external APIs as details around business/use-case policy.
- Recommend microservices only when operational evidence justifies the complexity.
- Favor stable dependencies, acyclic dependencies, narrow public entrypoints, and testable use-case boundaries.
- Do not present diagrams as proof by themselves; inspect hot paths and consumers.
- Do not blindly trust exact commit pinning on fast-moving repos. Use the context freshness states to decide whether baseline-plus-drift is enough.
- Hooks are optional. Do not install git hooks unless the user asks; task-start freshness checks are the default mechanism.

## Script Quick Reference

- `scripts/architecture_context_check.py .`
- `scripts/architecture_context_bootstrap.py . --out docs/architecture --graphs-out docs/architecture-graphs`
- `scripts/architecture_inventory.py . --out docs/architecture/inventory.json`
- `scripts/architecture_diagrams.py . --out docs/architecture-graphs --no-render`
- `scripts/architecture_boundary_check.py . --index docs/architecture-graphs/architecture-index.json`
- `scripts/architecture_scorecard.py --index docs/architecture-graphs/architecture-index.json --inventory docs/architecture/inventory.json`
- `scripts/architecture_pattern_fit.py --inventory docs/architecture/inventory.json --scorecard docs/architecture/scorecard.json`
- `scripts/architecture_context_pack.py --repo . --inventory docs/architecture/inventory.json --index docs/architecture-graphs/architecture-index.json --scorecard docs/architecture/scorecard.json --boundary docs/architecture/boundary-report.json --pattern-fit docs/architecture/pattern-fit.json`
- `scripts/architecture_context_hook.py install --repo .`
- `scripts/architecture_adr.py create "Use modular monolith boundaries" --context "..." --decision "..." --consequences "..."`

## References

- Read `references/software-architecture-patterns.md` for source-derived architecture pattern tradeoffs informed by Mark Richards' `Software Architecture Patterns`.
- Read `references/clean-architecture-principles.md` for dependency direction, boundaries, component principles, and details discipline informed by Robert C. Martin's `Clean Architecture`.
- Read `references/architecture-best-practices.md` for practical review heuristics from the PDFs and 42 Coffee Cups article.
- Read `references/pattern-fit-rubric.md` when choosing or rejecting architecture styles.
- Read `references/source-manifest.md` only when verifying provenance or maintaining the public repo; do not vendor PDFs or long excerpts.
