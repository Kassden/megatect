#!/usr/bin/env python3
"""Run the Megatect artifact pipeline and generate canonical context."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], accept: tuple[int, ...] = (0,)) -> int:
    print("+ " + " ".join(cmd))
    proc = subprocess.run(cmd)
    if proc.returncode not in accept:
        raise SystemExit(proc.returncode)
    return proc.returncode


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--out", default="docs/architecture")
    parser.add_argument("--graphs-out", default="docs/architecture-graphs")
    parser.add_argument("--boundary-config", default="architecture-boundaries.json")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    out = Path(args.out)
    graphs_out = Path(args.graphs_out)
    if not out.is_absolute():
        out = repo / out
    if not graphs_out.is_absolute():
        graphs_out = repo / graphs_out
    out.mkdir(parents=True, exist_ok=True)
    graphs_out.mkdir(parents=True, exist_ok=True)
    inventory = out / "inventory.json"
    index = graphs_out / "architecture-index.json"
    boundary = out / "boundary-report.json"
    scorecard_json = out / "scorecard.json"
    scorecard_md = out / "scorecard.md"
    pattern_fit = out / "pattern-fit.json"
    boundary_config = repo / args.boundary_config

    run([sys.executable, str(SCRIPT_DIR / "architecture_inventory.py"), str(repo), "--out", str(inventory)])
    diagram_cmd = [sys.executable, str(SCRIPT_DIR / "architecture_diagrams.py"), str(repo), "--out", str(graphs_out)]
    if not args.render:
        diagram_cmd.append("--no-render")
    run(diagram_cmd)
    boundary_cmd = [sys.executable, str(SCRIPT_DIR / "architecture_boundary_check.py"), str(repo), "--index", str(index), "--out", str(boundary)]
    if boundary_config.exists():
        boundary_cmd.extend(["--config", str(boundary_config)])
    run(boundary_cmd, accept=(0, 1))
    run([sys.executable, str(SCRIPT_DIR / "architecture_scorecard.py"), "--index", str(index), "--inventory", str(inventory), "--json-out", str(scorecard_json), "--md-out", str(scorecard_md)])
    run([sys.executable, str(SCRIPT_DIR / "architecture_pattern_fit.py"), "--inventory", str(inventory), "--scorecard", str(scorecard_json), "--out", str(pattern_fit)])
    run([
        sys.executable,
        str(SCRIPT_DIR / "architecture_context_pack.py"),
        "--repo",
        str(repo),
        "--inventory",
        str(inventory),
        "--index",
        str(index),
        "--scorecard",
        str(scorecard_json),
        "--boundary",
        str(boundary),
        "--pattern-fit",
        str(pattern_fit),
        "--out",
        str(out / "CONTEXT.md"),
        "--manifest",
        str(out / "context-manifest.json"),
    ])
    print(f"canonical context ready: {out / 'CONTEXT.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
