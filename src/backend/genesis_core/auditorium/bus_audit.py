import time
import uuid
import logging
from src.backend.genesis_core.bus.hyper_sonic import HyperSonicBus, HyperSonicReader

logger = logging.getLogger("AetherBusAuditor")

class AetherBusAuditor:
    def __init__(self):
        self.latency_threshold_ns = 100
        self.writer = None
        self.reader = None

    def _ensure_connected(self):
        try:
            if not self.writer:
                self.writer = HyperSonicBus()
            if not self.reader:
                self.reader = HyperSonicReader()
                self.reader.connect()
        except Exception as e:
            logger.warning(f"Bus Connection Warning: {e}")

    def audit_lightning_speed(self):
        """Audits the speed and reliability of the AetherBus."""
        metrics = {
            "type": "communication",
            "metrics": {
                "latency_ms": 0.0,
                "throughput_msg_per_sec": 0.0,
                "health_score": 1.0
            }
        }

        # Latency Test (Loopback)
        try:
            latency = self.measure_loopback_latency()
            metrics["metrics"]["latency_ms"] = latency * 1000 # convert to ms

            # Score
            if metrics["metrics"]["latency_ms"] < 2.0: # Allow some slack for Python overhead
                metrics["metrics"]["health_score"] = 1.0
            elif metrics["metrics"]["latency_ms"] < 10.0:
                metrics["metrics"]["health_score"] = 0.8
            else:
                metrics["metrics"]["health_score"] = 0.5

        except Exception as e:
            logger.error(f"Bus Audit Error: {e}")
            metrics["metrics"]["health_score"] = 0.0

        return metrics

    def measure_loopback_latency(self) -> float:
        """Measures time to write and read back a message."""
        self._ensure_connected()
        if not self.writer or not self.reader:
            return 999.0

        try:
            test_id = uuid.uuid4().hex
            payload_data = test_id.encode()

            # Clear reader buffer (catch up to head)
            # We only want to read what we are about to write.
            # Reading everything in loop might be slow if bus is busy.
            # But we must catch up.
            for _ in self.reader.read():
                pass

            start = time.time()
            self.writer.write("audit.ping", payload_data)

            # Read loop with timeout
            found = False
            timeout = 0.1 # 100ms timeout
            loop_start = time.time()

            while time.time() - loop_start < timeout:
                for timestamp, msg_id, topic_hash, payload in self.reader.read():
                    if payload == payload_data:
                        found = True
                        break
                if found:
                    break
                time.sleep(0.001)

            if found:
                return time.time() - start
            return 999.0

        except Exception as e:
            logger.error(f"Latency Measure Error: {e}")
            return 999.0


    def close(self):
        """Release HyperSonic resources held by this auditor."""
        if self.reader:
            self.reader.close()
            self.reader = None
        if self.writer:
            self.writer.close()
            self.writer = None
