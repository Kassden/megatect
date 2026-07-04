#!/usr/bin/env python3
"""Generate an architecture risk scorecard from inventory and graph data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def score(index: dict, inventory: dict) -> dict:
    systems = index.get("systems", {})
    edges = index.get("edges", [])
    cycles = index.get("cycles", [])
    hubs = index.get("top_hubs", {})
    integrations = inventory.get("integrations", [])
    workers = inventory.get("workers", [])
    api_routes = inventory.get("api_routes", [])
    schemas = inventory.get("schemas", [])
    max_hub = max([0] + [h.get("count", 0) for h in hubs.get("incoming", []) + hubs.get("outgoing", [])])
    risk = {
        "systems": len(systems),
        "file_edges": len(edges),
        "cycles": len(cycles),
        "max_hub_degree": max_hub,
        "api_routes": len(api_routes),
        "workers": len(workers),
        "schemas": len(schemas),
        "integrations": len(integrations),
    }
    points = 0
    points += min(len(cycles) * 2, 8)
    points += 3 if max_hub >= 20 else 2 if max_hub >= 10 else 0
    points += 2 if len(integrations) >= 6 else 1 if len(integrations) >= 3 else 0
    points += 2 if workers and api_routes else 0
    points += 2 if len(systems) >= 10 else 1 if len(systems) >= 5 else 0
    tier = "low" if points <= 2 else "moderate" if points <= 6 else "high" if points <= 10 else "systemic"
    risk["risk_points"] = points
    risk["risk_tier"] = tier
    risk["recommendations"] = recommendations(risk)
    return risk


def recommendations(risk: dict) -> list[str]:
    recs = []
    if risk["cycles"]:
        recs.append("Break dependency cycles before extracting services.")
    if risk["max_hub_degree"] >= 10:
        recs.append("Review top hubs for accidental shared-kernel or god-module behavior.")
    if risk["api_routes"] and risk["schemas"]:
        recs.append("Check whether API handlers own policy or leak persistence models.")
    if risk["workers"] and risk["api_routes"]:
        recs.append("Separate web-path and worker-path contracts before changing runtime boundaries.")
    if not recs:
        recs.append("Architecture risk appears low; preserve simplicity and add only targeted boundaries.")
    return recs


def markdown(data: dict) -> str:
    lines = ["# Architecture Scorecard", "", f"- Risk tier: {data['risk_tier']}", f"- Risk points: {data['risk_points']}"]
    for key in ["systems", "file_edges", "cycles", "max_hub_degree", "api_routes", "workers", "schemas", "integrations"]:
        lines.append(f"- {key}: {data.get(key, 0)}")
    lines.extend(["", "## Recommendations"])
    lines.extend(f"- {r}" for r in data["recommendations"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index")
    parser.add_argument("--inventory")
    parser.add_argument("--json-out", default="architecture-scorecard.json")
    parser.add_argument("--md-out", default="architecture-scorecard.md")
    args = parser.parse_args()
    data = score(read_json(args.index), read_json(args.inventory))
    Path(args.json_out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    Path(args.md_out).write_text(markdown(data), encoding="utf-8")
    print(f"wrote {args.json_out} and {args.md_out}: {data['risk_tier']} risk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
