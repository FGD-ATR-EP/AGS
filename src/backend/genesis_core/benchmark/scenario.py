from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from time import perf_counter
from typing import Awaitable, Callable, Sequence


@dataclass
class ScenarioCase:
    name: str
    prompt: str
    expected_keywords: tuple[str, ...] = ()


@dataclass
class ScenarioResult:
    name: str
    latency_ms: float
    stability_score: float
    quality_score: float


@dataclass
class ScenarioBenchmarkReport:
    results: list[ScenarioResult]
    latency_p95_ms: float
    stability_avg: float
    quality_avg: float


def compute_quality_score(
    response_text: str,
    expected_keywords: Sequence[str],
    confidence: float,
    freshness: float,
) -> float:
    """Unified quality rubric: confidence + freshness + completeness."""
    if expected_keywords:
        hits = sum(1 for kw in expected_keywords if kw.lower() in response_text.lower())
        completeness = hits / len(expected_keywords)
    else:
        completeness = 1.0

    score = (confidence * 0.4) + (freshness * 0.2) + (completeness * 0.4)
    return max(0.0, min(1.0, round(score, 4)))


async def run_scenario_benchmark(
    scenarios: Sequence[ScenarioCase],
    runner: Callable[[str], Awaitable[tuple[str, float]]],
) -> ScenarioBenchmarkReport:
    """Single-pass benchmark for latency, stability, and quality."""
    results: list[ScenarioResult] = []

    for scenario in scenarios:
        started = perf_counter()
        response_text, stability_score = await runner(scenario.prompt)
        latency_ms = (perf_counter() - started) * 1000

        freshness = 1.0 if latency_ms <= 200 else max(0.0, 1.0 - ((latency_ms - 200) / 1000))
        quality_score = compute_quality_score(
            response_text=response_text,
            expected_keywords=scenario.expected_keywords,
            confidence=stability_score,
            freshness=freshness,
        )

        results.append(
            ScenarioResult(
                name=scenario.name,
                latency_ms=round(latency_ms, 3),
                stability_score=round(stability_score, 3),
                quality_score=quality_score,
            )
        )

    latencies = sorted(item.latency_ms for item in results)
    p95_index = max(0, int((len(latencies) - 1) * 0.95))

    return ScenarioBenchmarkReport(
        results=results,
        latency_p95_ms=latencies[p95_index],
        stability_avg=round(mean(item.stability_score for item in results), 4),
        quality_avg=round(mean(item.quality_score for item in results), 4),
    )
