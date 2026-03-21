from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from typing import Awaitable, Callable, DefaultDict, Dict, Iterable, Optional, Set

from src.backend.genesis_core.bus.base import BaseAetherBus
from src.backend.genesis_core.bus.contracts import BusConfig, BusRole
from src.backend.genesis_core.protocol.schemas import AetherEvent

logger = logging.getLogger("AetherBusTachyon")

try:
    import zmq
    import zmq.asyncio
except ImportError:  # pragma: no cover - optional dependency path
    zmq = None
    zmq_asyncio = None
else:  # pragma: no cover - optional dependency path
    zmq_asyncio = zmq.asyncio

try:
    import websockets
except ImportError:  # pragma: no cover - optional dependency path
    websockets = None


class AetherBusTachyon(BaseAetherBus):
    """Tachyon adapter using ZeroMQ for internal transport and WebSocket fan-out for external consumers."""

    def __init__(self, config: BusConfig | None = None):
        super().__init__(config=config)
        self._subscribers: DefaultDict[str, Set[Callable[[AetherEvent], Awaitable[None]]]] = defaultdict(set)
        self._global_listeners: Set[Callable[[AetherEvent], Awaitable[None]]] = set()
        self._ws_clients: DefaultDict[str, Set[object]] = defaultdict(set)
        self._zmq_context = None
        self._publisher = None
        self._subscriber = None
        self._websocket_bridge = None
        self._reader_task: Optional[asyncio.Task] = None

    async def connect(self):
        if self._running:
            return
        self._running = True
        if zmq is not None:
            try:
                self._zmq_context = zmq_asyncio.Context.instance()
                self._publisher = self._zmq_context.socket(zmq.PUB)
                self._publisher.bind(self.config.internal_endpoint.address)
                self._subscriber = self._zmq_context.socket(zmq.SUB)
                self._subscriber.connect(self.config.internal_endpoint.address)
                self._subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
                self._reader_task = asyncio.create_task(self._read_internal_loop())
            except zmq.ZMQError as exc:
                logger.warning(
                    "Tachyon could not bind %s (%s); falling back to degraded in-process dispatch.",
                    self.config.internal_endpoint.address,
                    exc,
                )
                for socket_name in ("_publisher", "_subscriber"):
                    socket = getattr(self, socket_name)
                    if socket is not None:
                        socket.close(0)
                        setattr(self, socket_name, None)
        else:
            logger.warning("pyzmq is unavailable; Tachyon internal transport is running in degraded in-process mode.")

        if websockets is not None:
            self._websocket_bridge = self.config.external_endpoint.address
        else:
            logger.warning("websockets package is unavailable; Tachyon external bridge fan-out is disabled.")

        logger.info(
            "AetherBusTachyon connected with internal=%s external=%s codec=%s compression=%s",
            self.config.internal_endpoint.address,
            self.config.external_endpoint.address,
            self.config.codec.value,
            self.config.compression.value,
        )

    async def close(self):
        self._running = False
        if self._reader_task:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
        for socket_name in ("_publisher", "_subscriber"):
            socket = getattr(self, socket_name)
            if socket is not None:
                socket.close(0)
                setattr(self, socket_name, None)
        self._subscribers.clear()
        self._global_listeners.clear()
        self._ws_clients.clear()
        logger.info("AetherBusTachyon closed.")

    async def publish(self, event: AetherEvent):
        if not self._running:
            return await self.error(event, "bus_not_running")

        event = self.validate_event(event, stage="publish")
        correlation_id = self.ensure_correlation_id(event)
        payload = self.serialize_event(event)
        delivered = False

        if self._publisher is not None:
            topic = event.topic or event.extensions.get("topic") or event.session_id or "system.broadcast"
            await self._publisher.send_multipart([topic.encode("utf-8"), payload])
            delivered = True
        else:
            await self._dispatch_local(event)
            delivered = True

        await self._dispatch_global(event)
        await self._fanout_websocket(event)

        if delivered:
            return await self.ack(event, f"tachyon_publish:{correlation_id}")
        return await self.error(event, "tachyon_delivery_failed")

    async def subscribe(self, session_id: str, callback):
        self._subscribers[session_id].add(callback)
        if self._subscriber is not None:
            self._subscriber.setsockopt_string(zmq.SUBSCRIBE, session_id)

    async def unsubscribe(self, session_id: str):
        self._subscribers.pop(session_id, None)
        if self._subscriber is not None:
            self._subscriber.setsockopt_string(zmq.UNSUBSCRIBE, session_id)

    async def add_global_listener(self, callback: Callable[[AetherEvent], Awaitable[None]]):
        self._global_listeners.add(callback)

    async def register_websocket_client(self, channel: str, websocket: object):
        self._ws_clients[channel].add(websocket)

    async def unregister_websocket_client(self, channel: str, websocket: object):
        self._ws_clients[channel].discard(websocket)
        if not self._ws_clients[channel]:
            self._ws_clients.pop(channel, None)

    async def _read_internal_loop(self):
        assert self._subscriber is not None
        while self._running:
            try:
                _topic, payload = await self._subscriber.recv_multipart()
                event = self.deserialize_event(payload)
                await self._dispatch_local(event)
                await self._dispatch_global(event)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("Tachyon internal read failure: %s", exc)
                await asyncio.sleep(self.config.reconnect.initial_delay_ms / 1000)

    def _candidate_channels(self, event: AetherEvent) -> Iterable[str]:
        yielded = []
        for value in (event.topic, event.session_id, event.target.channel, event.origin.channel, "*"):
            if value and value not in yielded:
                yielded.append(value)
                yield value

    async def _dispatch_local(self, event: AetherEvent):
        callbacks = []
        if event.session_id == "*" or event.session_id is None:
            for registered in self._subscribers.values():
                callbacks.extend(registered)
        else:
            for channel in self._candidate_channels(event):
                callbacks.extend(self._subscribers.get(channel, set()))
        seen = set()
        for callback in callbacks:
            if callback in seen:
                continue
            seen.add(callback)
            result = callback(event)
            if inspect.isawaitable(result):
                await result

    async def _dispatch_global(self, event: AetherEvent):
        for callback in self._global_listeners:
            result = callback(event)
            if inspect.isawaitable(result):
                await result

    async def _fanout_websocket(self, event: AetherEvent):
        if not self._ws_clients:
            return
        message = self.serialize_event(event, codec=self.config.codec)
        recipients = set()
        candidate_channels = list(self._candidate_channels(event))
        for channel in candidate_channels:
            recipients |= set(self._ws_clients.get(channel, set()))
        stale = []
        for websocket in recipients:
            try:
                if hasattr(websocket, "send"):
                    await websocket.send(message)
                elif hasattr(websocket, "send_bytes"):
                    await websocket.send_bytes(message)
            except Exception:
                stale.append(websocket)
        for websocket in stale:
            for channel in candidate_channels:
                await self.unregister_websocket_client(channel, websocket)
