import logging
import os
from typing import Optional

from src.backend.genesis_core.bus.contracts import (
    BusCodec,
    BusCompression,
    BusConfig,
    BusEndpoint,
    BusReconnectPolicy,
    BusRole,
)

logger = logging.getLogger("BusFactory")


class BusFactory:
    _instance = None

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @staticmethod
    def _env(*names: str, default: str) -> str:
        for name in names:
            value = os.getenv(name)
            if value is not None and value.strip():
                return value.strip()
        return default

    @classmethod
    def _load_config(cls) -> BusConfig:
        implementation = cls._env("BUS_IMPLEMENTATION", "AETHERBUS_IMPLEMENTATION", default="tachyon").lower()
        codec = BusCodec(cls._env("BUS_CODEC", "AETHERBUS_CODEC", default=BusCodec.MSGPACK.value).lower())
        compression = BusCompression(
            cls._env("BUS_COMPRESSION", "AETHERBUS_COMPRESSION", default=BusCompression.NONE.value).lower()
        )
        internal_endpoint = BusEndpoint(
            role=BusRole.INTERNAL,
            transport=cls._env("BUS_INTERNAL_TRANSPORT", "AETHERBUS_INTERNAL_TRANSPORT", default="zeromq"),
            address=cls._env(
                "BUS_INTERNAL_ENDPOINT",
                "AETHERBUS_INTERNAL_ENDPOINT",
                "AETHERBUS_TACHYON_INTERNAL_ENDPOINT",
                default="tcp://127.0.0.1:5555",
            ),
        )
        external_endpoint = BusEndpoint(
            role=BusRole.EXTERNAL,
            transport=cls._env("BUS_EXTERNAL_TRANSPORT", "AETHERBUS_EXTERNAL_TRANSPORT", default="websocket"),
            address=cls._env(
                "BUS_EXTERNAL_ENDPOINT",
                "AETHERBUS_EXTERNAL_ENDPOINT",
                "AETHERBUS_TACHYON_EXTERNAL_ENDPOINT",
                default="ws://127.0.0.1:5556/ws",
            ),
        )
        reconnect = BusReconnectPolicy(
            initial_delay_ms=int(cls._env("BUS_RECONNECT_INITIAL_DELAY_MS", default="250")),
            max_delay_ms=int(cls._env("BUS_RECONNECT_MAX_DELAY_MS", default="5000")),
            max_attempts=int(cls._env("BUS_RECONNECT_MAX_ATTEMPTS", default="10")),
        )
        return BusConfig(
            implementation=implementation,
            internal_endpoint=internal_endpoint,
            external_endpoint=external_endpoint,
            codec=codec,
            compression=compression,
            timeout_ms=int(cls._env("BUS_TIMEOUT_MS", "AETHERBUS_TIMEOUT_MS", default="2000")),
            reconnect=reconnect,
            metadata={
                "canonical_bus": "tachyon",
                "migration_mode": "compatibility" if implementation in {"extreme", "legacy"} else "canonical",
            },
        )

    @classmethod
    def get_bus(cls, config: Optional[BusConfig] = None):
        if cls._instance is not None and config is None:
            return cls._instance

        resolved_config = config or cls._load_config()
        implementation = resolved_config.implementation.lower()

        if implementation == "tachyon":
            from src.backend.genesis_core.bus.tachyon import AetherBusTachyon
            bus = AetherBusTachyon(config=resolved_config)
        elif implementation in {"extreme", "legacy"}:
            logger.warning(
                "BusFactory is using compatibility bus implementation=%s. Set BUS_IMPLEMENTATION=tachyon for the canonical Phase 1 runtime path.",
                implementation,
            )
            from src.backend.genesis_core.bus.extreme import AetherBusExtreme
            bus = AetherBusExtreme(config=resolved_config)
        else:
            raise ValueError(f"Unsupported bus implementation: {implementation}")

        logger.info(
            "BusFactory selected implementation=%s internal=%s external=%s codec=%s compression=%s timeout_ms=%s",
            implementation,
            resolved_config.internal_endpoint.address,
            resolved_config.external_endpoint.address,
            resolved_config.codec.value,
            resolved_config.compression.value,
            resolved_config.timeout_ms,
        )
        if config is None:
            cls._instance = bus
        return bus
