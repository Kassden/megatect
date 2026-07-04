#!/usr/bin/env python3
"""Create and validate concise architecture decision records."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

REQUIRED = ["## Status", "## Context", "## Decision", "## Consequences"]


def slug(title: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return value or "architecture-decision"


def render(title: str, status: str, context: str, decision: str, consequences: str) -> str:
    return f"""# {title}

Date: {date.today().isoformat()}

## Status
{status}

## Context
{context}

## Decision
{decision}

## Consequences
{consequences}
"""


def cmd_create(args: argparse.Namespace) -> int:
    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{date.today().isoformat()}-{slug(args.title)}.md"
    path.write_text(render(args.title, args.status, args.context, args.decision, args.consequences), encoding="utf-8")
    print(path)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    failures = []
    for raw in args.files:
        path = Path(raw)
        text = path.read_text(encoding="utf-8")
        missing = [field for field in REQUIRED if field not in text]
        if missing:
            failures.append((path, missing))
    for path, missing in failures:
        print(f"{path}: missing {', '.join(missing)}")
    print(f"checked {len(args.files)} ADR file(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    create = sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--status", default="Proposed")
    create.add_argument("--context", required=True)
    create.add_argument("--decision", required=True)
    create.add_argument("--consequences", required=True)
    create.add_argument("--dir", default="docs/architecture/adr")
    create.set_defaults(func=cmd_create)
    check = sub.add_parser("check")
    check.add_argument("files", nargs="+")
    check.set_defaults(func=cmd_check)
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
