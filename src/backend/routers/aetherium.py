from fastapi import APIRouter, WebSocket, Request, WebSocketDisconnect, HTTPException
from typing import Dict, Any
import uuid
import json
import logging
import asyncio

from src.backend.genesis_core.protocol.correlation import CorrelationPolicy
from src.backend.genesis_core.protocol.schemas import (
    AetherEvent,
    AetherEventType,
    ManifestationDirectivePayload,
    ManifestationDirectiveState,
    StateData,
)
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext
from src.backend.governance.runtime import DirectiveRuntime
from src.backend.genesis_core.protocol.abe_contract import ABEContract
from src.backend.security.key_manager import KeyManager

logger = logging.getLogger("AetheriumAPI")


MANIFEST_VERSION = "2026.03-manifestation-v1"


def _directive_state(event: AetherEvent, *, lifecycle_stage: str | None = None, sandbox: bool = False) -> dict[str, Any]:
    return ManifestationDirectiveState(
        correlation_id=event.correlation_id,
        causation_id=event.causation_id,
        trace_id=event.trace_id,
        topic=event.topic,
        directive_type=event.type,
        manifest_version=MANIFEST_VERSION,
        session_id=event.session_id,
        lifecycle_stage=lifecycle_stage,
        sandbox=sandbox,
    ).model_dump(mode="json")


def _manifestation_bridge_payload(event: AetherEvent, *, lifecycle_stage: str | None = None) -> dict[str, Any]:
    payload = event.model_dump(mode="json")
    nested_payload = payload.get("payload", {})
    payload["directive_state"] = _directive_state(event, lifecycle_stage=lifecycle_stage)
    payload["manifest_version"] = MANIFEST_VERSION
    payload["semantic_source"] = "backend"
    payload["frontend_contract"] = "render-only"
    payload["render_state"] = payload.get("render_state") if isinstance(payload.get("render_state"), dict) else nested_payload.get("render_state", {})
    payload["status"] = payload.get("status") if isinstance(payload.get("status"), dict) else nested_payload.get("status_block") or nested_payload.get("status", {})
    payload["replay"] = payload.get("replay") if isinstance(payload.get("replay"), dict) else nested_payload.get("replay", {})
    payload["diagnostics"] = payload.get("diagnostics") if isinstance(payload.get("diagnostics"), dict) else nested_payload.get("diagnostics", {})
    ManifestationDirectivePayload.model_validate({
        "directive_state": payload["directive_state"],
        "render_state": payload["render_state"],
        "status": payload["status"],
        "replay": payload["replay"],
        "diagnostics": payload["diagnostics"],
        "semantic_source": payload["semantic_source"],
    })
    return payload


def _validate_ingress_envelope(raw_payload: Dict[str, Any], session_id: str) -> AetherEvent:
    text = raw_payload.get("text", "")
    correlation = CorrelationPolicy.build(
        correlation_id=raw_payload.get("correlation_id"),
        causation_id=raw_payload.get("causation_id"),
        trace_id=raw_payload.get("trace_id"),
        session_id=session_id,
    )
    payload = {
        "client_message": raw_payload,
        "text": text,
        "directive_state": {
            "session_id": session_id,
            "manifest_version": MANIFEST_VERSION,
            "semantic_source": "backend",
            **{k: v for k, v in correlation.items() if v is not None},
        },
    }
    return AetherEvent(
        type=AetherEventType.INTENT_DETECTED,
        session_id=session_id,
        topic="intent.ingress",
        correlation_id=correlation["correlation_id"],
        causation_id=correlation["causation_id"],
        trace_id=correlation["trace_id"],
        origin={"service": "api", "subsystem": "body", "channel": session_id},
        target={"service": "genesis_core", "subsystem": "mind", "channel": "lifecycle"},
        payload=payload,
        governance={"validated": True, "policy_mode": "enforce"},
        memory={"ledger_event_type": "intent_ingress", "causal_chain": [correlation["correlation_id"]]},
    )


def _manifestation_payload(event: AetherEvent, *, lifecycle_stage: str | None = None) -> str:
    return json.dumps(_manifestation_bridge_payload(event, lifecycle_stage=lifecycle_stage))


router = APIRouter(tags=["aetherium"])


@router.post("/v1/session")
async def create_session(request: Request, body: Dict[str, Any]):
    """
    Control Plane: Establish a conscious connection.
    Requires:
    1. Valid .abe Contract (Identity)
    2. Valid Access Key (Permission)
    """
    access_key = body.get("access_key")
    abe_contract_json = body.get("abe_contract")

    app_state = request.app.state
    if not hasattr(app_state, "key_manager"):
        logger.warning("KeyManager not found on app state. Allowing Anonymous (Dev Mode).")
    else:
        key_manager: KeyManager = app_state.key_manager

        try:
            if not abe_contract_json:
                raise ValueError("Missing .abe contract")

            contract = ABEContract.from_json(
                json.dumps(abe_contract_json) if isinstance(abe_contract_json, dict) else abe_contract_json
            )

            if not access_key:
                raise ValueError("Missing Access Key")

            if not key_manager.validate_access(access_key, contract.identity.abe_id):
                logger.warning("Session Rejected: Invalid Key/Subscription for %s", contract.identity.abe_id)
                raise HTTPException(status_code=403, detail="Access Denied: Invalid Key or Subscription Suspended")

            logger.info("Session Authorized: %s [%s]", contract.identity.entity_name, contract.intent.primary_intent)

        except ValueError as exc:
            logger.error("Contract Validation Error: %s", exc)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            if isinstance(exc, HTTPException):
                raise exc
            logger.error("Session Error: %s", exc)
            raise HTTPException(status_code=500, detail="Internal Handshake Error") from exc

    session_id = f"ae-{uuid.uuid4().hex[:8]}"

    return {
        "session_id": session_id,
        "ws_endpoint": "/ws/v3/stream",
        "expires_in": 3600,
    }


@router.websocket("/ws/v3/stream")
async def stream_endpoint(websocket: WebSocket):
    """
    Data Plane: The Aetherium Stream.
    Bi-directional state emission and intent resonance.
    """
    await websocket.accept()

    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = f"ae-anon-{uuid.uuid4().hex[:6]}"

    logger.info("Stream Connected: %s", session_id)

    app_state = websocket.app.state
    if not hasattr(app_state, "aether_bus") or not hasattr(app_state, "engine"):
        logger.error("System Not Initialized (Bus/Engine missing)")
        await websocket.close(code=1011)
        return

    bus = app_state.aether_bus
    engine = app_state.engine
    directive_runtime: DirectiveRuntime = app_state.directive_runtime
    metric_collector = getattr(app_state, "metric_collector", None)

    async def bridge_callback(event: AetherEvent):
        try:
            if metric_collector:
                metric_collector.track_event(event)
            AetherEvent.model_validate(event.model_dump(mode="json"))
            await websocket.send_text(_manifestation_payload(event, lifecycle_stage="manifestation_emit"))
        except Exception as exc:
            logger.warning("Bridge Error %s: %s", session_id, exc)

    await bus.subscribe(session_id, bridge_callback)

    handshake_correlation = CorrelationPolicy.build(session_id=session_id)
    await bus.publish(
        AetherEvent(
            type=AetherEventType.HANDSHAKE,
            session_id=session_id,
            topic="manifestation.handshake",
            correlation_id=handshake_correlation["correlation_id"],
            trace_id=handshake_correlation["trace_id"],
            origin={"service": "api", "subsystem": "body", "channel": session_id},
            target={"service": "client", "subsystem": "manifestation", "channel": session_id},
            payload={
                "state": {"state": "connected", "confidence": 1.0, "energy": 1.0, "coherence": 1.0},
                "directive_state": {**handshake_correlation, "manifest_version": MANIFEST_VERSION, "semantic_source": "backend"},
                "status": {"phase": "connected", "label": "connected"},
                "diagnostics": {"bridge": "ws_v3", "frontend_contract": "render-only"},
            },
            state=StateData(state="connected", confidence=1.0, energy=1.0, coherence=1.0),
            memory={"ledger_event_type": "manifestation_handshake", "causal_chain": [handshake_correlation["correlation_id"]]},
        )
    )

    try:
        while True:
            data_text = await websocket.receive_text()

            try:
                payload = json.loads(data_text)
            except json.JSONDecodeError:
                continue

            if payload.get("type") == "PING":
                await websocket.send_json({"type": "PONG"})
                continue

            ingress_envelope = _validate_ingress_envelope(payload, session_id)
            await bus.publish(ingress_envelope)

            user_text = payload.get("text", "")
            if not user_text and "intent_vector" in payload:
                user_text = "[Abstract Intent]"

            if user_text:
                ingress_envelope.payload.setdefault("action", "cognitive_query")
                ingress_envelope.payload.setdefault("resource", "mind.lifecycle")
                ingress_envelope.payload.setdefault("intent_type", "COGNITIVE_QUERY")

                async def governed_planner(envelope: AetherEvent) -> SystemIntent | None:
                    intent = SystemIntent(
                        origin_agent=session_id,
                        target_agent="AgioSage_v1",
                        intent_type="COGNITIVE_QUERY",
                        payload=IntentPayload(content=user_text, modality="text"),
                        correlation_id=envelope.correlation_id,
                        context=IntentContext(
                            emotional_valence=0.0,
                            energy_level=0.5,
                            turbulence=0.0,
                            source_confidence=1.0,
                        ),
                    )
                    return await engine.lifecycle.process_request(intent)

                async def process_task() -> None:
                    try:
                        runtime_result = await directive_runtime.handle_envelope(ingress_envelope, planner=governed_planner)
                        if runtime_result.decision.status == "PENDING_APPROVAL":
                            await bus.publish(
                                AetherEvent(
                                    type=AetherEventType.STATE_UPDATE,
                                    session_id=session_id,
                                    topic="governance.approval.pending",
                                    correlation_id=ingress_envelope.correlation_id,
                                    causation_id=ingress_envelope.envelope_id,
                                    trace_id=ingress_envelope.trace_id,
                                    origin={"service": "governance", "subsystem": "kernel", "channel": session_id},
                                    target={"service": "client", "subsystem": "manifestation", "channel": session_id},
                                    payload={
                                        "status": "PENDING_APPROVAL",
                                        "approval_ticket_id": runtime_result.decision.ticket_id,
                                        "reason": runtime_result.decision.reason,
                                        "directive_state": {
                                            "correlation_id": ingress_envelope.correlation_id,
                                            "causation_id": ingress_envelope.envelope_id,
                                            "trace_id": ingress_envelope.trace_id,
                                        },
                                    },
                                    governance={
                                        "decision": "PENDING_APPROVAL",
                                        "risk_tier": runtime_result.decision.risk_tier.name,
                                        "policy_effect": runtime_result.decision.policy_effect or "REQUIRE_APPROVAL",
                                        "approval_ticket_id": runtime_result.decision.ticket_id,
                                        "policy_mode": runtime_result.decision.policy_mode,
                                        "validated": True,
                                    },
                                    memory={
                                        "ledger_event_type": "governance_pending_approval",
                                        "causal_chain": [ingress_envelope.correlation_id],
                                    },
                                )
                            )
                            return
                        if runtime_result.decision.status == "DENIED":
                            await bus.publish(
                                AetherEvent(
                                    type=AetherEventType.DEGRADATION,
                                    session_id=session_id,
                                    topic="governance.denied",
                                    correlation_id=ingress_envelope.correlation_id,
                                    causation_id=ingress_envelope.envelope_id,
                                    trace_id=ingress_envelope.trace_id,
                                    origin={"service": "governance", "subsystem": "kernel", "channel": session_id},
                                    target={"service": "client", "subsystem": "manifestation", "channel": session_id},
                                    payload={
                                        "error": runtime_result.decision.reason,
                                        "directive_state": {
                                            "correlation_id": ingress_envelope.correlation_id,
                                            "causation_id": ingress_envelope.envelope_id,
                                            "trace_id": ingress_envelope.trace_id,
                                        },
                                    },
                                    governance={
                                        "decision": "DENIED",
                                        "risk_tier": runtime_result.decision.risk_tier.name,
                                        "policy_effect": runtime_result.decision.policy_effect or "DENY",
                                        "policy_mode": runtime_result.decision.policy_mode,
                                        "validated": True,
                                    },
                                    memory={
                                        "ledger_event_type": "governance_denied",
                                        "causal_chain": [ingress_envelope.correlation_id],
                                    },
                                    error=runtime_result.decision.reason,
                                )
                            )
                            return

                        response_intent = runtime_result.response
                        if response_intent:
                            await bus.publish(
                                AetherEvent(
                                    type=AetherEventType.MANIFESTATION,
                                    session_id=session_id,
                                    topic="manifestation.response",
                                    correlation_id=response_intent.correlation_id or ingress_envelope.correlation_id,
                                    causation_id=ingress_envelope.envelope_id,
                                    trace_id=ingress_envelope.trace_id,
                                    origin={"service": "genesis_core", "subsystem": "mind", "channel": "lifecycle"},
                                    target={"service": "client", "subsystem": "manifestation", "channel": session_id},
                                    payload={
                                        "system_intent": response_intent.model_dump(),
                                        "directive_state": {
                                            "correlation_id": ingress_envelope.correlation_id,
                                            "causation_id": ingress_envelope.envelope_id,
                                            "trace_id": ingress_envelope.trace_id,
                                        },
                                    },
                                    governance={
                                        "decision": runtime_result.decision.status,
                                        "risk_tier": runtime_result.decision.risk_tier.name,
                                        "policy_effect": runtime_result.decision.policy_effect or "ALLOW",
                                        "policy_mode": runtime_result.decision.policy_mode,
                                        "validated": True,
                                    },
                                    memory={
                                        "ledger_event_type": "manifestation_emit",
                                        "causal_chain": [ingress_envelope.correlation_id],
                                    },
                                )
                            )
                    except Exception as exc:
                        logger.error("Processing Error: %s", exc)
                        await bus.publish(
                            AetherEvent(
                                type=AetherEventType.DEGRADATION,
                                session_id=session_id,
                                topic="system.error",
                                correlation_id=ingress_envelope.correlation_id,
                                causation_id=ingress_envelope.envelope_id,
                                trace_id=ingress_envelope.trace_id,
                                origin={"service": "api", "subsystem": "body", "channel": session_id},
                                target={"service": "client", "subsystem": "manifestation", "channel": session_id},
                                payload={
                                    "error": str(exc),
                                    "directive_state": {
                                        "correlation_id": ingress_envelope.correlation_id,
                                        "causation_id": ingress_envelope.envelope_id,
                                        "trace_id": ingress_envelope.trace_id,
                                    },
                                },
                                error=str(exc),
                            )
                        )

                asyncio.create_task(process_task())

    except WebSocketDisconnect:
        logger.info("Stream Disconnected: %s", session_id)
    except Exception as exc:
        logger.error("Stream Error: %s", exc)
    finally:
        await bus.unsubscribe(session_id)
