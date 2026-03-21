#!/usr/bin/env python3
"""Compute perceived latency statistics and gate against a target.

Input formats:
1) JSON array: [{"latency_ms": 100, "latency_factor": 0.2}, ...]
2) NDJSON: one JSON object per line

Supported fields per record:
- perceived_latency_ms (preferred)
- latency_ms (+ optional latency_factor)

Perceived latency model when not explicitly provided:
    perceived_latency_ms = latency_ms * (1 + latency_factor)
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Iterable


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if p <= 0:
        return min(values)
    if p >= 100:
        return max(values)
    ordered = sorted(values)
    rank = (len(ordered) - 1) * (p / 100.0)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def parse_records(raw: str) -> list[dict]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of objects")
        return data
    records = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def extract_perceived_latencies(records: Iterable[dict]) -> list[float]:
    output: list[float] = []
    for record in records:
        if "perceived_latency_ms" in record:
            output.append(float(record["perceived_latency_ms"]))
            continue

        if "latency_ms" not in record:
            continue
        latency_ms = float(record["latency_ms"])
        latency_factor = float(record.get("latency_factor", 0.0))
        output.append(latency_ms * (1.0 + latency_factor))
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Perceived latency benchmark")
    parser.add_argument("input", type=Path, help="Path to JSON array or NDJSON file")
    parser.add_argument("--target-ms", type=float, default=120.0, help="Pass threshold for p95")
    args = parser.parse_args()

    raw = args.input.read_text(encoding="utf-8")
    records = parse_records(raw)
    latencies = extract_perceived_latencies(records)

    if not latencies:
        print(json.dumps({"samples": 0, "error": "No usable latency records"}, indent=2))
        return 2

    result = {
        "samples": len(latencies),
        "mean_latency_ms": round(mean(latencies), 2),
        "p95_latency_ms": round(percentile(latencies, 95), 2),
    }
    result["target_ms"] = args.target_ms
    result["pass"] = result["p95_latency_ms"] <= args.target_ms

    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
