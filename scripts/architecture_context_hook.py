#!/usr/bin/env python3
"""Install an optional git hook that reports Megatect context freshness."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MARKER = "# megatect-context-hook"


def git_dir(repo: Path) -> Path:
    out = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--git-dir"], text=True).strip()
    path = Path(out)
    return path if path.is_absolute() else repo / path


def hook_text(repo: Path) -> str:
    check = SCRIPT_DIR / "architecture_context_check.py"
    return f"""#!/bin/sh
{MARKER}
python3 "{check}" "{repo}" >/dev/null
status=$?
if [ "$status" -eq 1 ]; then
  echo "Megatect context needs light refresh: run architecture_context_bootstrap.py when convenient."
elif [ "$status" -eq 2 ]; then
  echo "Megatect context needs full refresh before architecture work."
fi
exit 0
"""


def install(repo: Path, force: bool) -> int:
    hooks = git_dir(repo) / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / "post-commit"
    text = hook_text(repo)
    if hook.exists():
        existing = hook.read_text(encoding="utf-8", errors="ignore")
        if MARKER in existing:
            hook.write_text(text, encoding="utf-8")
        elif force:
            backup = hook.with_suffix(hook.suffix + ".pre-megatect")
            backup.write_text(existing, encoding="utf-8")
            hook.write_text(text, encoding="utf-8")
            print(f"backed up existing hook to {backup}")
        else:
            print(f"refusing to overwrite existing hook: {hook}")
            print("rerun with --force to back it up and replace it")
            return 2
    else:
        hook.write_text(text, encoding="utf-8")
    hook.chmod(0o755)
    print(f"installed {hook}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    install_parser = sub.add_parser("install")
    install_parser.add_argument("--repo", default=".")
    install_parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "install":
        return install(Path(args.repo).resolve(), args.force)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
