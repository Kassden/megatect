#!/usr/bin/env python3
"""Check whether a Megatect canonical context is fresh enough to use."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import architecture_context_pack  # noqa: E402

LIGHT_PATTERNS = (
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lockb",
    "Cargo.toml",
    "Cargo.lock",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "go.sum",
    "tsconfig.json",
    "next.config.",
    "vite.config.",
    "vercel.json",
    "docker-compose",
    "Dockerfile",
    ".env",
)
FULL_SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs", ".swift"}
SCHEMA_SUFFIXES = {".sql", ".prisma"}


def git(root: Path, args: list[str], ok: tuple[int, ...] = (0,)) -> tuple[int, str]:
    try:
        proc = subprocess.run(["git", "-C", str(root), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return 127, ""
    if proc.returncode not in ok:
        return proc.returncode, ""
    return proc.returncode, proc.stdout.strip()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def parse_name_status(text: str) -> list[dict[str, str]]:
    changes = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        status = parts[0]
        path = parts[-1]
        changes.append({"status": status, "path": path})
    return changes


def porcelain_changes(text: str) -> list[dict[str, str]]:
    changes = []
    for line in text.splitlines():
        if not line:
            continue
        if line.startswith("?? "):
            status = "??"
            path = line[3:]
        elif len(line) >= 3 and line[2] == " ":
            status = line[:2].strip() or "?"
            path = line[3:]
        elif len(line) >= 2 and line[1] == " ":
            status = line[0].strip() or "?"
            path = line[2:]
        else:
            status = line[:2].strip() or "?"
            path = line[3:] if len(line) > 3 else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changes.append({"status": status, "path": path})
    return changes


def changed_files(root: Path, generated_commit: str) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    if generated_commit and generated_commit != "unknown":
        code, text = git(root, ["diff", "--name-status", f"{generated_commit}..HEAD"], ok=(0, 128))
        if code == 0:
            changes.extend(parse_name_status(text))
    _, status = git(root, ["status", "--porcelain=v1"])
    changes.extend(porcelain_changes(status))
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for change in changes:
        dedup[(change["status"], change["path"])] = change
    return sorted(dedup.values(), key=lambda item: (item["path"], item["status"]))


def is_doc_or_test(path: str) -> bool:
    p = Path(path)
    lower = path.lower()
    return (
        lower.endswith((".md", ".mdx", ".rst", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg"))
        or "/test/" in lower
        or "/tests/" in lower
        or lower.startswith("test/")
        or lower.startswith("tests/")
        or ".test." in lower
        or ".spec." in lower
        or lower.startswith("docs/")
        or p.name in {"README.md", "CHANGELOG.md", "LICENSE"}
    )


def is_light(path: str) -> bool:
    lower = path.lower()
    return any(pattern.lower() in lower for pattern in LIGHT_PATTERNS) or "/api/" in lower or lower.startswith(("api/", "pages/api/")) or "schema" in lower


def is_full(change: dict[str, str]) -> bool:
    path = change["path"]
    status = change["status"]
    suffix = Path(path).suffix
    if (status.startswith(("A", "D", "R")) or status == "??") and (suffix in FULL_SOURCE_SUFFIXES or suffix in SCHEMA_SUFFIXES):
        return True
    if suffix in SCHEMA_SUFFIXES:
        return True
    return False


def classify(root: Path, manifest: dict) -> dict:
    generated_commit = manifest.get("generated_commit", "unknown")
    _, head = git(root, ["rev-parse", "HEAD"])
    changes = changed_files(root, generated_commit)
    current_hash = architecture_context_pack.source_files_hash(root)
    hash_changed = bool(manifest.get("source_files_hash")) and current_hash != manifest.get("source_files_hash")
    if not manifest:
        state = "needs-full-refresh"
        reasons = ["context manifest missing"]
    elif head == generated_commit and not changes and not hash_changed:
        state = "fresh"
        reasons = ["generated commit matches HEAD and source hash is unchanged"]
    elif any(is_full(change) for change in changes):
        state = "needs-full-refresh"
        reasons = ["source/schema files were added, deleted, moved, or schema files changed"]
    elif any(is_light(change["path"]) for change in changes):
        state = "needs-light-refresh"
        reasons = ["entrypoint, config, dependency, route, env, or schema-adjacent files changed"]
    elif changes and all(is_doc_or_test(change["path"]) for change in changes):
        state = "usable-with-drift"
        reasons = ["only docs, tests, or media files changed"]
    elif hash_changed:
        state = "needs-light-refresh"
        reasons = ["tracked architecture-relevant source hash changed"]
    else:
        state = "usable-with-drift"
        reasons = ["commit drift exists but no high-impact architecture files were detected"]
    return {
        "state": state,
        "generated_commit": generated_commit,
        "current_commit": head or "unknown",
        "source_files_hash": current_hash,
        "manifest_source_files_hash": manifest.get("source_files_hash", "unknown"),
        "changed_files": changes,
        "reasons": reasons,
    }


def self_test() -> None:
    cases = [
        ([], "fresh", False),
        ([{"status": "M", "path": "README.md"}], "usable-with-drift", False),
        ([{"status": "M", "path": "package.json"}], "needs-light-refresh", False),
        ([{"status": "A", "path": "src/new.ts"}], "needs-full-refresh", False),
        ([{"status": "??", "path": "src/new.ts"}], "needs-full-refresh", False),
        ([{"status": "M", "path": "src/schema.prisma"}], "needs-full-refresh", False),
    ]
    for changes, expected, hash_changed in cases:
        if any(is_full(change) for change in changes):
            got = "needs-full-refresh"
        elif any(is_light(change["path"]) for change in changes):
            got = "needs-light-refresh"
        elif changes and all(is_doc_or_test(change["path"]) for change in changes):
            got = "usable-with-drift"
        elif hash_changed:
            got = "needs-light-refresh"
        else:
            got = "fresh"
        assert got == expected, (changes, got, expected)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--manifest", default="docs/architecture/context-manifest.json")
    parser.add_argument("--json-out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        print("architecture_context_check self-test passed")
        return 0
    repo = Path(args.repo).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo / manifest_path
    result = classify(repo, load_manifest(manifest_path))
    if args.json_out:
        out = Path(args.json_out)
        if not out.is_absolute():
            out = repo / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"context freshness: {result['state']}")
    for reason in result["reasons"]:
        print(f"- {reason}")
    for change in result["changed_files"][:30]:
        print(f"- {change['status']} {change['path']}")
    return 2 if result["state"] == "needs-full-refresh" else 1 if result["state"] == "needs-light-refresh" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
