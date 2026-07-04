#!/usr/bin/env python3
"""Create a lightweight architecture inventory for a repository."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "target", ".venv", "venv", "__pycache__"}
INTEGRATION_RE = re.compile(
    r"\b(vercel|supabase|stripe|resend|openai|anthropic|cloudflare|s3|aws|gcp|azure|postgres|redis|qdrant|pinecone|influx|tailscale)\b",
    re.I,
)


def iter_files(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*"):
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.is_file():
            out.append(path)
    return sorted(out)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect(root: Path) -> dict[str, object]:
    files = iter_files(root)
    rels = [rel(p, root) for p in files]
    package = read_json(root / "package.json") if (root / "package.json").exists() else {}

    stacks = []
    if package:
        stacks.append("node")
        deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
        for name in ["next", "react", "vite", "express", "fastapi", "supabase", "prisma"]:
            if name in deps:
                stacks.append(name)
    if any(p.endswith((".py", "pyw")) for p in rels) or (root / "pyproject.toml").exists():
        stacks.append("python")
    if any(p.endswith(".rs") for p in rels) or (root / "Cargo.toml").exists():
        stacks.append("rust")
    if any(p.endswith(".go") for p in rels) or (root / "go.mod").exists():
        stacks.append("go")

    api_routes = [p for p in rels if "/api/" in p or p.startswith(("api/", "pages/api/"))]
    workers = [p for p in rels if re.search(r"(worker|queue|cron|job|scheduler)", p, re.I)]
    schemas = [p for p in rels if re.search(r"(schema|migration|prisma|sql|model)", p, re.I)]
    configs = [p for p in rels if re.search(r"(^|/)(\\.env|.*config\\.|Dockerfile|docker-compose|vercel|netlify|cloudflare|wrangler)", p, re.I)]
    docs = [p for p in rels if p.lower().endswith((".md", ".mdx", ".rst")) or p.startswith("docs/")]
    entrypoints = [p for p in rels if p in {"src/main.ts", "src/main.tsx", "src/index.ts", "src/app/page.tsx", "app/page.tsx", "main.py", "app.py"}]

    integrations = set()
    for p in files:
        if p.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".py", ".rs", ".go", ".toml", ".json", ".yml", ".yaml"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")[:20000]
        integrations.update(match.group(1).lower() for match in INTEGRATION_RE.finditer(text))

    return {
        "root": str(root),
        "files": len(files),
        "stacks": sorted(set(stacks)),
        "package_scripts": package.get("scripts", {}),
        "entrypoints": sorted(entrypoints),
        "api_routes": sorted(api_routes),
        "workers": sorted(workers),
        "schemas": sorted(schemas),
        "configs": sorted(configs),
        "docs": sorted(docs[:200]),
        "integrations": sorted(integrations),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--out", default="architecture-inventory.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    data = detect(root)
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}: {data['files']} files, stacks={','.join(data['stacks']) or 'unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
