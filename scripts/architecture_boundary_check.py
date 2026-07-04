#!/usr/bin/env python3
"""Check architecture boundary violations from a Megatect graph index."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import architecture_diagrams  # noqa: E402


def load_index(root: Path, index_path: str | None) -> dict:
    if index_path and Path(index_path).exists():
        return json.loads(Path(index_path).read_text(encoding="utf-8"))
    out = root / ".megatect" / "architecture-graphs"
    return architecture_diagrams.generate(root, out, render=False)


def load_config(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatch(path, pattern) or path.startswith(pattern.rstrip("/") + "/")


def public_entry(system: str, path: str, config: dict) -> bool:
    entries = config.get("public_entrypoints", {}).get(system, [])
    if entries:
        return any(matches(path, entry) for entry in entries)
    parts = path.split("/")
    return parts[-1].startswith("index.") or parts[-1].startswith("__init__.")


def system_for(path: str, systems: dict[str, list[str]]) -> str | None:
    for system, nodes in systems.items():
        if path in nodes:
            return system
    return None


def check(index: dict, config: dict) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    systems = index.get("systems", {})
    for src, dst in index.get("edges", []):
        for rule in config.get("forbidden_imports", []):
            if matches(src, rule.get("from", "")) and matches(dst, rule.get("to", "")):
                violations.append({"type": "forbidden-import", "src": src, "dst": dst, "rule": json.dumps(rule)})
        src_system = system_for(src, systems)
        dst_system = system_for(dst, systems)
        if src_system and dst_system and src_system != dst_system and not public_entry(dst_system, dst, config):
            violations.append({"type": "deep-cross-boundary-import", "src": src, "dst": dst, "rule": f"{dst_system} public entrypoint"})
    for cycle in index.get("cycles", []):
        violations.append({"type": "cycle", "src": " -> ".join(cycle), "dst": cycle[0] if cycle else "", "rule": "acyclic dependencies"})
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--index")
    parser.add_argument("--config")
    parser.add_argument("--out")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    index = load_index(root, args.index)
    violations = check(index, load_config(args.config))
    result = {"violations": violations, "count": len(violations)}
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"boundary violations: {len(violations)}")
    for v in violations[:50]:
        print(f"- {v['type']}: {v['src']} -> {v['dst']}")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
