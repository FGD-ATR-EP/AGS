from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional
from uuid import uuid4


CORRELATION_KEYS = ("correlation_id", "causation_id", "trace_id")


class CorrelationPolicy:
    """Canonical correlation metadata policy for V3 envelopes and replayable records."""

    @staticmethod
    def new_id(prefix: Optional[str] = None) -> str:
        value = uuid4().hex
        return f"{prefix}-{value}" if prefix else value

    @classmethod
    def infer_trace_id(cls, correlation_id: Optional[str], trace_id: Optional[str] = None) -> str:
        return trace_id or correlation_id or cls.new_id("trace")

    @classmethod
    def infer_correlation_id(
        cls,
        correlation_id: Optional[str] = None,
        *,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        fallback: Optional[str] = None,
    ) -> str:
        return correlation_id or trace_id or session_id or fallback or cls.new_id("corr")

    @classmethod
    def build(
        cls,
        *,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        fallback: Optional[str] = None,
    ) -> dict[str, Optional[str]]:
        resolved_correlation = cls.infer_correlation_id(
            correlation_id,
            trace_id=trace_id,
            session_id=session_id,
            fallback=fallback,
        )
        resolved_trace = cls.infer_trace_id(resolved_correlation, trace_id=trace_id)
        return {
            "correlation_id": resolved_correlation,
            "causation_id": causation_id,
            "trace_id": resolved_trace,
        }

    @classmethod
    def validate(cls, metadata: Mapping[str, Any]) -> dict[str, Optional[str]]:
        normalized = cls.build(
            correlation_id=_string_or_none(metadata.get("correlation_id")),
            causation_id=_string_or_none(metadata.get("causation_id")),
            trace_id=_string_or_none(metadata.get("trace_id")),
            session_id=_string_or_none(metadata.get("session_id")),
            fallback=_string_or_none(metadata.get("fallback")),
        )
        if not normalized["correlation_id"]:
            raise ValueError("correlation_id is required")
        if not normalized["trace_id"]:
            raise ValueError("trace_id is required")
        return normalized

    @classmethod
    def merge_into(cls, target: MutableMapping[str, Any], **kwargs: Any) -> dict[str, Optional[str]]:
        normalized = cls.build(
            correlation_id=_string_or_none(kwargs.get("correlation_id", target.get("correlation_id"))),
            causation_id=_string_or_none(kwargs.get("causation_id", target.get("causation_id"))),
            trace_id=_string_or_none(kwargs.get("trace_id", target.get("trace_id"))),
            session_id=_string_or_none(kwargs.get("session_id", target.get("session_id"))),
            fallback=_string_or_none(kwargs.get("fallback")),
        )
        for key, value in normalized.items():
            if value is not None:
                target[key] = value
        return normalized



def _string_or_none(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
