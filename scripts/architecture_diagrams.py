#!/usr/bin/env python3
"""Generate portable architecture dependency diagrams and graph indexes."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".next", ".turbo", ".venv", "__pycache__", "build", "coverage", "dist", "node_modules", "target", "venv"}
SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
JS_IMPORT_RE = re.compile(r"""(?:from\s+["']([^"']+)["']|import\s*\(\s*["']([^"']+)["']\s*\)|require\(\s*["']([^"']+)["']\s*\))""")


def iter_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in SUFFIXES
        and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    )


def read_imports(path: Path) -> list[str]:
    text = path.read_text(errors="ignore")
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append("." * node.level + (node.module or ""))
        return imports
    return [match for group in JS_IMPORT_RE.findall(text) for match in group if match]


def candidate_paths(base: Path) -> list[Path]:
    candidates = [base]
    for suffix in SUFFIXES:
        candidates.append(base.with_suffix(suffix))
    for suffix in SUFFIXES:
        candidates.append(base / f"index{suffix}")
        candidates.append(base / f"__init__{suffix}")
    return candidates


def resolve_import(root: Path, importer: Path, spec: str, files: set[Path]) -> Path | None:
    bases = []
    if spec.startswith(".") and "/" in spec:
        bases.append((importer.parent / spec).resolve())
    elif spec.startswith("."):
        dots = len(spec) - len(spec.lstrip("."))
        rel = spec[dots:].replace(".", "/")
        base = importer.parent
        for _ in range(max(dots - 1, 0)):
            base = base.parent
        bases.append(base / rel)
    elif spec.startswith("@/") or spec.startswith("~/"):
        bases.append(root / "src" / spec[2:])
    elif "." in spec and not spec.startswith("@"):
        bases.append(root / spec.replace(".", "/"))
    else:
        return None
    for base in bases:
        for candidate in candidate_paths(base):
            if candidate in files:
                return candidate
    return None


def discover_system_root(root: Path) -> Path:
    for rel in ("src/systems", "systems", "src"):
        path = root / rel
        if path.is_dir():
            return path
    return root


def system_name(path: Path, system_root: Path) -> str:
    try:
        rel = path.relative_to(system_root)
    except ValueError:
        return "_root"
    return rel.parts[0] if rel.parts else "_root"


def node_id(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def mermaid(edges: set[tuple[str, str]], nodes: set[str]) -> str:
    lines = ["flowchart LR"]
    for node in sorted(nodes):
        lines.append(f'  {safe_id(node)}["{node}"]')
    for src, dst in sorted(edges):
        lines.append(f"  {safe_id(src)} --> {safe_id(dst)}")
    return "\n".join(lines) + "\n"


def dot(edges: set[tuple[str, str]], nodes: set[str]) -> str:
    lines = ["digraph architecture {", '  rankdir="LR";']
    lines.extend(f'  "{node}";' for node in sorted(nodes))
    lines.extend(f'  "{src}" -> "{dst}";' for src, dst in sorted(edges))
    lines.append("}")
    return "\n".join(lines) + "\n"


def run_quiet(cmd: list[str]) -> bool:
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def render_svg(mmd: Path, dot_file: Path) -> None:
    if shutil.which("dot"):
        run_quiet(["dot", "-Tsvg", str(dot_file), "-o", str(dot_file.with_suffix(".dot.svg"))])
    if shutil.which("mmdc"):
        run_quiet(["mmdc", "-i", str(mmd), "-o", str(mmd.with_suffix(".mmd.svg"))])
    elif shutil.which("npx"):
        run_quiet(["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(mmd), "-o", str(mmd.with_suffix(".mmd.svg"))])


def write_graph(out: Path, stem: str, edges: set[tuple[str, str]], nodes: set[str], render: bool) -> None:
    mmd = out / f"{stem}.mmd"
    dot_file = out / f"{stem}.dot"
    mmd.write_text(mermaid(edges, nodes), encoding="utf-8")
    dot_file.write_text(dot(edges, nodes), encoding="utf-8")
    if render:
        render_svg(mmd, dot_file)


def cycles(edges: set[tuple[str, str]]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)
    found: set[tuple[str, ...]] = set()

    def visit(start: str, node: str, path: list[str]) -> None:
        for nxt in graph.get(node, []):
            if nxt == start and len(path) > 1:
                cycle = path[:]
                rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
                found.add(min(rotations))
            elif nxt not in path and len(path) < 12:
                visit(start, nxt, path + [nxt])

    for node in graph:
        visit(node, node, [node])
    return [list(cycle) for cycle in sorted(found)[:50]]


def top_hubs(edges: set[tuple[str, str]], limit: int = 20) -> dict[str, list[dict[str, object]]]:
    incoming = Counter(dst for _, dst in edges)
    outgoing = Counter(src for src, _ in edges)
    return {
        "incoming": [{"node": k, "count": v} for k, v in incoming.most_common(limit)],
        "outgoing": [{"node": k, "count": v} for k, v in outgoing.most_common(limit)],
    }


def generate(root: Path, out: Path, system_root: Path | None = None, render: bool = True) -> dict[str, object]:
    root = root.resolve()
    out.mkdir(parents=True, exist_ok=True)
    system_root = (system_root or discover_system_root(root)).resolve()
    files = set(iter_files(root))
    file_edges: set[tuple[str, str]] = set()
    systems: dict[str, set[str]] = defaultdict(set)
    system_edges: set[tuple[str, str]] = set()
    for src in files:
        src_id = node_id(src, root)
        src_system = system_name(src, system_root)
        systems[src_system].add(src_id)
        for spec in read_imports(src):
            dst = resolve_import(root, src, spec, files)
            if not dst:
                continue
            dst_id = node_id(dst, root)
            dst_system = system_name(dst, system_root)
            file_edges.add((src_id, dst_id))
            systems[dst_system].add(dst_id)
            if src_system != dst_system:
                system_edges.add((src_system, dst_system))

    nodes = {node_id(path, root) for path in files}
    write_graph(out, "whole-repo", file_edges, nodes, render)
    for name, system_nodes in sorted(systems.items()):
        write_graph(out, f"system-{name}", {e for e in file_edges if e[0] in system_nodes and e[1] in system_nodes}, system_nodes, render)
    write_graph(out, "meta-systems", system_edges, set(systems), render)
    index = {
        "root": str(root),
        "system_root": str(system_root),
        "files": len(files),
        "file_edges": len(file_edges),
        "systems": {name: sorted(values) for name, values in sorted(systems.items())},
        "system_edges": sorted(system_edges),
        "edges": sorted(file_edges),
        "cycles": cycles(file_edges),
        "system_cycles": cycles(system_edges),
        "top_hubs": top_hubs(file_edges),
    }
    (out / "architecture-index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return index


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src/systems/a").mkdir(parents=True)
        (root / "src/systems/b").mkdir(parents=True)
        (root / "src/systems/a/index.ts").write_text('import { b } from "../b";\nexport const a = b;\n', encoding="utf-8")
        (root / "src/systems/b/index.ts").write_text("export const b = 1;\n", encoding="utf-8")
        index = generate(root, root / "docs/architecture-graphs", render=False)
        assert ("a", "b") in {tuple(edge) for edge in index["system_edges"]}
        assert index["top_hubs"]["outgoing"]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--out", default="docs/architecture-graphs")
    parser.add_argument("--systems-root")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print("architecture_diagrams self-test passed")
        return 0
    root = Path(args.root)
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    system_root = Path(args.systems_root) if args.systems_root else None
    index = generate(root, out, system_root, render=not args.no_render)
    print(f"wrote {out}: {index['files']} files, {index['file_edges']} edges, {len(index['systems'])} systems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
