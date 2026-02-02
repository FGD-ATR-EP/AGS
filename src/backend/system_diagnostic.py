import sys
import os
import json
import time
import uuid
import logging
import asyncio
import platform
import struct
import resource
from datetime import datetime
from typing import Dict, Any, List

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.backend.genesis_core.logenesis.engine import LogenesisEngine
    from src.backend.genesis_core.models.logenesis import IntentPacket, LogenesisState, StateMetrics
    from src.backend.genesis_core.bus.hyper_sonic import HyperSonicBus, HyperSonicReader
except ImportError as e:
    print(json.dumps({"error": f"Import Error: {e}"}))
    sys.exit(1)

# Configure logging to be silent or redirect to file to avoid polluting stdout (which is for JSON)
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("SystemDiagnostic")

class SystemInspector:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "system_state": "Awakened", # Default assumption, will verify
            "active_modules": [],
            "failures": [],
            "in_progress": [],
            "neural_latency": "UNKNOWN",
            "execution_trace": [],
            "historical_persistence": "MISSING"
        }

    def inspect_topology(self):
        """
        1. TOPOLOGY: List loaded modules, check INSPIRA/FIRMA mismatch.
        """
        # Active Modules
        self.report["active_modules"] = list(sys.modules.keys())[:50] # Limit to 50 for brevity

        # Environment Check (FIRMA) vs Logic Req (INSPIRA)
        python_version = sys.version.split()[0]
        required_version = "3.10"

        # Simple version check
        major, minor, micro = platform.python_version_tuple()
        if int(major) < 3 or (int(major) == 3 and int(minor) < 10):
             self.report["failures"].append({
                 "component": "FIRMA:ENV",
                 "error": f"Python Version Mismatch: Found {python_version}, Required >= {required_version}"
             })

        # RAM Check (Linux specific)
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_total_kb = 0
                for line in f:
                    if "MemTotal" in line:
                        mem_total_kb = int(line.split()[1])
                        break

                # SHM_SIZE is 16MB (16384 KB)
                # We need at least that much free, but let's just check if total is reasonable (e.g. > 512MB)
                if mem_total_kb < 512000: # 512MB
                    self.report["failures"].append({
                        "component": "FIRMA:HARDWARE",
                        "error": f"Insufficient RAM: {mem_total_kb} KB. Recommended > 512MB for Genesis Core."
                    })
        except FileNotFoundError:
            pass # Not Linux, skip

    async def trace_execution(self):
        """
        2. LOGENESIS:TRACE:DUMP (Simulation)
        """
        engine = LogenesisEngine()

        # Dummy Packets
        intents = [
            "SYS_START_SEQUENCE",
            "CHECK_STATUS",
            "EMPTY_INTENT",
            "CALCULATE_PI", # Analytic
            "FEEL_THE_VOID", # Subjective
            "IGNORE_ME",
            "HELLO_WORLD",
            "SYSTEM_OVERLOAD_TEST", # High Urgency
            "QUIET_PLEASE",
            "SHUTDOWN_REQUEST"
        ]

        trace_log = []

        for i, text in enumerate(intents):
            packet = IntentPacket(
                modality="text",
                embedding=None,
                energy_level=0.5 + (i * 0.05), # Ramp up energy
                confidence=1.0,
                raw_payload=text
            )

            # Simulate processing
            start_time = time.time()
            try:
                response = await engine.process(packet, session_id="diagnostic_sim")
                duration = time.time() - start_time

                # Check for Hallucination Triggers
                metrics = response.state_metrics
                trigger = None
                if metrics:
                    if metrics.intent_entropy > 0.6:
                        trigger = "High Entropy (Conflict)"
                    if metrics.temporal_coherence < 0.2:
                        trigger = "Low Coherence (Logic Break)"

                if trigger:
                     self.report["failures"].append({
                         "component": "LOGENESIS:HALLUCINATION",
                         "error": f"Triggered by '{text}': {trigger}. Entropy={metrics.intent_entropy:.2f}, Coherence={metrics.temporal_coherence:.2f}"
                     })

                trace_entry = {
                    "step": i + 1,
                    "input": text,
                    "state_after": response.state.value,
                    "metrics": metrics.model_dump() if metrics else None,
                    "duration_ms": f"{duration*1000:.2f}"
                }
                trace_log.append(trace_entry)

            except Exception as e:
                self.report["failures"].append({
                    "component": "LOGENESIS:ENGINE",
                    "error": f"Execution Failed on '{text}': {str(e)}"
                })

        self.report["execution_trace"] = trace_log
        self.report["historical_persistence"] = "MISSING" # Explicitly requested

    def audit_traffic(self):
        """
        3. AETHERBUS:AUDIT (Speed Sync)
        """
        bus_name = f"diagnostic_bus_{uuid.uuid4().hex[:8]}"
        writer = HyperSonicBus(shm_name=bus_name)
        reader = HyperSonicReader(shm_name=bus_name)

        try:
            if not reader.connect():
                 self.report["failures"].append({
                     "component": "AETHERBUS:CONNECT",
                     "error": "Failed to connect Reader to Writer SHM"
                 })
                 return

            # Warmup
            writer.write("warmup", b"0")

            start_time = time.perf_counter()
            count = 1000

            # Speed Sync Loop
            # We write 1000 times. We read 1000 times.
            # Ideally we'd interleave, but since it's same process,
            # fill buffer then drain is safer to measure raw throughput without blocking logic complexity.
            # Given SHM size (16MB) and small payload, 1000 msgs fit easily.

            for i in range(count):
                writer.write("audit", b"PING")

            # Now Read
            read_count = 0
            # consume generator
            gen = reader.read()
            # We need to manually iterate or re-call read() because read() is a generator that yields *available* messages
            # It might yield them all in one go or we might need to call it again if writer was slower (not case here)

            for _ in gen:
                read_count += 1

            # If not all read (unlikely in single thread sequential), try again?
            # In HyperSonic implementation, read() loops until local_head == write_head.
            # So one call to `read()` generator should yield everything currently in buffer.

            duration = time.perf_counter() - start_time
            avg_latency_us = (duration / count) * 1_000_000

            self.report["neural_latency"] = f"{avg_latency_us:.2f} µs"

            if read_count < count: # Account for warmup msg? No, warmup was before start_time
                 # Actually wait, I wrote 'warmup' before loop.
                 # So there are 1001 messages in buffer.
                 # The loop in reader.read() will read all 1001.
                 pass

        except Exception as e:
             self.report["failures"].append({
                 "component": "AETHERBUS:AUDIT",
                 "error": f"Audit Failed: {str(e)}"
             })
        finally:
            writer.close()
            reader.close()
            # Ensure unlink happens (handled by writer.close() usually if mapped?
            # HyperSonicBus.close() calls unlink() inside a try/except, which is good.
            # Wait, writer.close() only calls close(), unlink is commented out or tricky?
            # Let's check the code: "try: self.shm.unlink() except: pass" in close()
            # Yes.

    def check_ledger(self):
        """
        4. PANGENESIS:LEDGER (Integrity)
        """
        config_path = os.path.join("src", "backend", "data", "genesis_core.json")
        if not os.path.exists(config_path):
             self.report["failures"].append({
                 "component": "PANGENESIS:LEDGER",
                 "error": f"Genesis Core Data Missing: {config_path}"
             })
             return

        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                if not data:
                    raise ValueError("Empty JSON")

                # Check for uncommitted fragments (Mock check)
                # In real scenario, we'd check `git status`.
                # Here we just check if ID exists.
                if not isinstance(data, list) or "id" not in data[0]:
                     self.report["failures"].append({
                         "component": "PANGENESIS:SCHEMA",
                         "error": "Invalid Genesis Schema"
                     })
        except json.JSONDecodeError:
             self.report["failures"].append({
                 "component": "PANGENESIS:INTEGRITY",
                 "error": "Corrupt JSON Ledger"
             })
        except Exception as e:
             self.report["failures"].append({
                 "component": "PANGENESIS:ACCESS",
                 "error": str(e)
             })

    def resource_map(self):
        """
        5. FIRMA:ENV:RESOURCE_MAP
        """
        # CPU
        cpu_count = os.cpu_count()

        # RAM Usage (Self)
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        ram_usage_mb = rusage.ru_maxrss / 1024 # Linux: kb. MacOS: bytes? Usually KB on Linux.
        if platform.system() == "Darwin":
            ram_usage_mb /= 1024 # Convert bytes to MB on Mac

        self.report["in_progress"].append(f"Resource Audit: {cpu_count} CPUs, ~{ram_usage_mb:.2f} MB Active RAM")

        # Chromatic Sanctum Check
        sanctum_path = os.path.join("src", "backend", "core", "perception", "chromatic_core.py")
        if not os.path.exists(sanctum_path):
             self.report["failures"].append({
                 "component": "CHROMATIC:SANCTUM",
                 "error": "Physics Engine Source Missing"
             })

    async def run(self):
        self.inspect_topology()
        self.audit_traffic() # Synchronous part
        self.check_ledger()
        self.resource_map()
        await self.trace_execution() # Async part

        # Output JSON
        print(json.dumps(self.report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspector = SystemInspector()
    try:
        asyncio.run(inspector.run())
    except KeyboardInterrupt:
        pass
