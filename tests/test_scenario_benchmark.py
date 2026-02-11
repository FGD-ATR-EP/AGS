import asyncio

from src.backend.genesis_core.benchmark.scenario import (
    ScenarioCase,
    compute_quality_score,
    run_scenario_benchmark,
)


def test_compute_quality_score_uses_unified_rubric():
    score = compute_quality_score(
        response_text="Resonator maintains stable response under uncertainty",
        expected_keywords=("stable", "uncertainty"),
        confidence=0.9,
        freshness=0.95,
    )
    assert 0.9 <= score <= 1.0


def test_run_scenario_benchmark_single_pass_metrics():
    async def fake_runner(prompt: str) -> tuple[str, float]:
        await asyncio.sleep(0.01)
        if "fault" in prompt:
            return "stable adaptation with fallback", 0.86
        return "clean response", 0.9

    scenarios = [
        ScenarioCase(name="normal", prompt="baseline"),
        ScenarioCase(name="fault", prompt="inject fault", expected_keywords=("stable", "fallback")),
    ]

    report = asyncio.run(run_scenario_benchmark(scenarios, fake_runner))

    assert len(report.results) == 2
    assert report.latency_p95_ms > 0
    assert 0 <= report.stability_avg <= 1
    assert 0 <= report.quality_avg <= 1
