---
name: megatect
description: Use for evidence-backed software architecture discovery, review, pattern selection, boundary analysis, dependency graphing, scorecards, ADR creation, modularization plans, clean-architecture guidance, and deciding whether to keep a modular monolith or move toward event-driven, microkernel, microservices, space-based, layered, or clean architecture. Trigger when Codex is asked to act as an architect, improve architecture, choose architecture patterns, write ADRs, analyze coupling, define bounded contexts, generate architecture diagrams, or create architecture plans grounded in real code evidence and architecture best practices.
---

# Megatect

Use Megatect as the high-rigor architecture skill. Keep the original `architect` skill as v1; this skill is the heavier v2 path with scripted evidence.

## Core Rule

Inspect the repository before judging it. Use scripts for inventory, graphs, boundaries, scorecards, pattern fit, and ADRs. Use the references for architecture judgment only after repo evidence exists.

## Workflow

1. **Inventory the repo**
   - Run `scripts/architecture_inventory.py <repo> --out docs/architecture/inventory.json`.
   - Read existing `ARCHITECTURE.md`, `README.md`, `AGENTS.md`, `docs/**`, package scripts, schema/config files, workers, API routes, and integration surfaces.

2. **Generate graph evidence**
   - Run `scripts/architecture_diagrams.py <repo> --out docs/architecture-graphs`.
   - Use `--no-render` when SVG rendering is unnecessary or blocked.
   - Inspect `architecture-index.json` for systems, edges, cycles, and hubs.

3. **Check boundaries**
   - If a repo has `architecture-boundaries.json`, run `scripts/architecture_boundary_check.py <repo> --config architecture-boundaries.json`.
   - If no config exists, use the script without config to detect cycles and deep cross-system imports.

4. **Score architecture risk**
   - Run `scripts/architecture_scorecard.py --index docs/architecture-graphs/architecture-index.json --inventory docs/architecture/inventory.json`.
   - Treat the scorecard as evidence, not a verdict. Confirm with code reads.

5. **Choose pattern fit**
   - Run `scripts/architecture_pattern_fit.py --inventory docs/architecture/inventory.json --scorecard docs/architecture/scorecard.json`.
   - Default to modular monolith unless scaling, isolation, ownership, security, latency, or release-cadence evidence justifies distribution.

6. **Produce decisions**
   - For durable decisions, use `scripts/architecture_adr.py create`.
   - For plans, produce phases with small boundary moves, public entrypoints, dependency rules, tests, and verification commands.

## Judgment Rules

- Separate evidence from inference.
- Prefer boundaries before services.
- Treat frameworks, databases, web UI, queues, and external APIs as details around business/use-case policy.
- Recommend microservices only when operational evidence justifies the complexity.
- Favor stable dependencies, acyclic dependencies, narrow public entrypoints, and testable use-case boundaries.
- Do not present diagrams as proof by themselves; inspect hot paths and consumers.

## Script Quick Reference

- `scripts/architecture_inventory.py . --out docs/architecture/inventory.json`
- `scripts/architecture_diagrams.py . --out docs/architecture-graphs --no-render`
- `scripts/architecture_boundary_check.py . --index docs/architecture-graphs/architecture-index.json`
- `scripts/architecture_scorecard.py --index docs/architecture-graphs/architecture-index.json --inventory docs/architecture/inventory.json`
- `scripts/architecture_pattern_fit.py --inventory docs/architecture/inventory.json --scorecard docs/architecture/scorecard.json`
- `scripts/architecture_adr.py create "Use modular monolith boundaries" --context "..." --decision "..." --consequences "..."`

## References

- Read `references/software-architecture-patterns.md` for source-derived architecture pattern tradeoffs.
- Read `references/clean-architecture-principles.md` for dependency direction, boundaries, component principles, and details discipline.
- Read `references/architecture-best-practices.md` for practical review heuristics from the PDFs and 42 Coffee Cups article.
- Read `references/pattern-fit-rubric.md` when choosing or rejecting architecture styles.
- Read `references/source-manifest.md` only when verifying provenance or maintaining the public repo; do not vendor PDFs or long excerpts.
