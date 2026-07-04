#!/usr/bin/env python3
"""Recommend architecture pattern fit from inventory and scorecard evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def classify(inventory: dict, scorecard: dict) -> dict[str, dict[str, object]]:
    workers = len(inventory.get("workers", []))
    routes = len(inventory.get("api_routes", []))
    integrations = len(inventory.get("integrations", []))
    risk = scorecard.get("risk_tier", "low")
    systems = scorecard.get("systems", 0)
    patterns = {
        "modular-monolith": {"fit": "fits", "reason": "Default until distribution pressure is proven."},
        "layered": {"fit": "fits" if routes else "maybe", "reason": "Fits request/response apps with clear delivery/application/domain/persistence flow."},
        "clean-architecture": {"fit": "fits" if routes or integrations else "maybe", "reason": "Useful when policy should be testable apart from frameworks, database, or web."},
        "event-driven": {"fit": "fits" if workers >= 2 or integrations >= 4 else "maybe", "reason": "Fits async workflows, fan-out, ingestion, notifications, and integrations."},
        "microkernel": {"fit": "maybe", "reason": "Use only if the product has a stable core plus plugin/extensions shape."},
        "microservices": {"fit": "avoid-for-now", "reason": "Needs scaling, isolation, ownership, security, or release-cadence evidence."},
        "space-based": {"fit": "avoid-for-now", "reason": "Only for extreme throughput/concurrency where central persistence is the bottleneck."},
    }
    if risk in {"high", "systemic"} and systems >= 6 and workers and integrations >= 4:
        patterns["microservices"] = {"fit": "maybe", "reason": "There is complexity, but verify operational pressure before distributing."}
    return patterns


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory")
    parser.add_argument("--scorecard")
    parser.add_argument("--out", default="architecture-pattern-fit.json")
    args = parser.parse_args()
    data = {"patterns": classify(read_json(args.inventory), read_json(args.scorecard))}
    Path(args.out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    for name, info in data["patterns"].items():
        print(f"- {name}: {info['fit']} — {info['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
