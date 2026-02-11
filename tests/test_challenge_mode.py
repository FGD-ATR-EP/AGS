from src.backend.genesis_core.logenesis.challenge_mode import FaultInjector
from src.backend.genesis_core.models.logenesis import IntentVector


def test_fault_injector_returns_canonical_keys_when_enabled():
    injector = FaultInjector(enabled=True, intensity=0.3, seed=7)
    base = IntentVector(
        epistemic_need=0.7,
        subjective_weight=0.2,
        decision_urgency=0.3,
        precision_required=0.8,
    )

    updated, event = injector.inject(base)

    assert event is not None
    assert set(event.canonical_keys.keys()) == {
        "fault_type",
        "severity",
        "quality_confidence",
        "quality_freshness",
        "quality_completeness",
    }
    assert updated != base


def test_fault_injector_disabled_no_changes():
    injector = FaultInjector(enabled=False)
    base = IntentVector(
        epistemic_need=0.5,
        subjective_weight=0.5,
        decision_urgency=0.5,
        precision_required=0.5,
    )

    updated, event = injector.inject(base)

    assert event is None
    assert updated == base
