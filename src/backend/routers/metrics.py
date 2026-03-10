import asyncio
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
from collections import defaultdict, deque
from pydantic import BaseModel, Field

from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType

logger = logging.getLogger("MetricCollector")


class ResonatorTelemetryPoint(BaseModel):
    resonator_id: str = Field(..., min_length=1)
    latency_ms: float = Field(..., ge=0.0)
    correction_rate: float = Field(..., ge=0.0, le=1.0)
    safety_override_triggered: bool = False
    timestamp: datetime | None = None


class ResonatorReliabilityTracker:
    """Tracks resonator health and computes reliability scorecards."""

    def __init__(self):
        self._window_seconds = 7 * 24 * 60 * 60
        self._telemetry: Dict[str, deque] = defaultdict(deque)

    def record(self, point: ResonatorTelemetryPoint):
        ts = (point.timestamp or datetime.now()).timestamp()
        queue = self._telemetry[point.resonator_id]
        queue.append(
            {
                "timestamp": ts,
                "latency_ms": point.latency_ms,
                "correction_rate": point.correction_rate,
                "safety_override_triggered": point.safety_override_triggered,
            }
        )
        self._trim(queue, now_ts=ts)

    def get_scorecard(self) -> Dict[str, Any]:
        now_ts = datetime.now().timestamp()
        scorecard: Dict[str, Any] = {}
        for resonator_id, queue in self._telemetry.items():
            self._trim(queue, now_ts=now_ts)
            if not queue:
                continue
            scorecard[resonator_id] = {
                "daily": self._summarize(queue, now_ts, 24 * 60 * 60),
                "weekly": self._summarize(queue, now_ts, self._window_seconds),
            }
        return scorecard

    @staticmethod
    def _health_status(reliability_score: float) -> str:
        if reliability_score >= 85.0:
            return "HEALTHY"
        if reliability_score >= 60.0:
            return "DEGRADED"
        return "CRITICAL"

    def _trim(self, queue: deque, now_ts: float):
        cutoff = now_ts - self._window_seconds
        while queue and queue[0]["timestamp"] < cutoff:
            queue.popleft()

    def _summarize(self, queue: deque, now_ts: float, window_seconds: int) -> Dict[str, Any]:
        cutoff = now_ts - window_seconds
        sample = [item for item in queue if item["timestamp"] >= cutoff]
        window_start = datetime.fromtimestamp(cutoff).isoformat()
        window_end = datetime.fromtimestamp(now_ts).isoformat()
        if not sample:
            return {
                "samples": 0,
                "window_start": window_start,
                "window_end": window_end,
                "avg_latency_ms": 0.0,
                "avg_correction_rate": 0.0,
                "safety_override_count": 0,
                "safety_override_frequency_per_hour": 0.0,
                "reliability_score": 0.0,
                "health_status": self._health_status(0.0),
            }

        samples = len(sample)
        avg_latency_ms = sum(item["latency_ms"] for item in sample) / samples
        avg_correction_rate = sum(item["correction_rate"] for item in sample) / samples
        safety_overrides = sum(1 for item in sample if item["safety_override_triggered"])
        hours = max(window_seconds / 3600, 1e-9)
        safety_override_frequency_per_hour = safety_overrides / hours

        latency_component = max(0.0, 1.0 - (avg_latency_ms / 1000.0))
        correction_component = max(0.0, 1.0 - avg_correction_rate)
        safety_component = max(0.0, 1.0 - safety_override_frequency_per_hour)
        reliability_score = round(
            (latency_component * 0.4 + correction_component * 0.4 + safety_component * 0.2) * 100,
            2,
        )

        return {
            "samples": samples,
            "window_start": window_start,
            "window_end": window_end,
            "avg_latency_ms": round(avg_latency_ms, 2),
            "avg_correction_rate": round(avg_correction_rate, 4),
            "safety_override_count": safety_overrides,
            "safety_override_frequency_per_hour": round(safety_override_frequency_per_hour, 4),
            "reliability_score": reliability_score,
            "health_status": self._health_status(reliability_score),
        }

class MetricCollector:
    """
    Singleton Aggregator for AetherBus Metrics.
    Provides data for the Pulse/Flow visualizations.
    """
    _instance = None

    def __init__(self):
        self.total_events = 0
        self.events_per_second = 0.0
        self.active_sessions = 0
        self.start_time = datetime.now().timestamp()
        self._window_events = 0
        self._last_tick = self.start_time

        # Aggregate Counters
        self.intent_count = 0
        self.manifestation_count = 0

        # Subscribers (Dashboards)
        self.subscribers: List[WebSocket] = []
        self.resonator_tracker = ResonatorReliabilityTracker()

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def track_event(self, event: AetherEvent):
        """Called by AetherBusExtreme for every event."""
        self.total_events += 1
        self._window_events += 1

        if event.type == AetherEventType.INTENT_DETECTED:
            self.intent_count += 1
        elif event.type == AetherEventType.MANIFESTATION:
            self.manifestation_count += 1

    async def broadcast_loop(self):
        """Periodic broadcast to dashboard subscribers (1Hz)."""
        while True:
            await asyncio.sleep(1.0)
            now = datetime.now().timestamp()
            dt = now - self._last_tick

            # Calc rate
            if dt > 0:
                self.events_per_second = self._window_events / dt

            # Reset window
            self._window_events = 0
            self._last_tick = now

            # Payload
            metrics = {
                "type": "METRICS_UPDATE",
                "uptime": int(now - self.start_time),
                "throughput": round(self.events_per_second, 2),
                "total_processed": self.total_events,
                "active_sessions": self.active_sessions,
                "intents_processed": self.intent_count,
                "manifestations_created": self.manifestation_count,
                "system_status": "STABLE" if self.events_per_second < 1000 else "SATURATED"
            }

            # Broadcast
            dead_sockets = []
            for ws in self.subscribers:
                try:
                    await ws.send_json(metrics)
                except Exception:
                    dead_sockets.append(ws)

            for ws in dead_sockets:
                self.subscribers.remove(ws)

    async def register_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.subscribers.append(websocket)
        logger.info("📈 Dashboard Connected")

router = APIRouter(tags=["metrics"])


@router.post("/v1/metrics/resonator-telemetry")
async def ingest_resonator_telemetry(payload: ResonatorTelemetryPoint):
    collector = MetricCollector.get_instance()
    collector.resonator_tracker.record(payload)
    return {"status": "ok", "resonator_id": payload.resonator_id}


@router.get("/v1/metrics/resonator-reliability")
async def get_resonator_reliability(resonator_id: str | None = None):
    collector = MetricCollector.get_instance()
    scorecard = collector.resonator_tracker.get_scorecard()

    if resonator_id:
        if resonator_id not in scorecard:
            raise HTTPException(status_code=404, detail="Resonator not found")
        return {"resonator_id": resonator_id, "scorecard": scorecard[resonator_id]}

    return {"scorecard": scorecard}

@router.websocket("/ws/v3/metrics")
async def metrics_endpoint(websocket: WebSocket):
    collector = MetricCollector.get_instance()
    await collector.register_dashboard(websocket)
    try:
        while True:
            # Just keep alive, ignore input
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in collector.subscribers:
            collector.subscribers.remove(websocket)
