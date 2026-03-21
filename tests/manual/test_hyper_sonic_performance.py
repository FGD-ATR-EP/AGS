import time
import multiprocessing
import os
import sys
import uuid
import logging
from unittest.mock import MagicMock

# Mock torch before importing anything else to avoid ModuleNotFoundError
sys.modules['torch'] = MagicMock()

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.backend.genesis_core.bus.hyper_sonic import HyperSonicBus, HyperSonicReader

# Configuration
TEST_MSG_COUNT = 1000
PAYLOAD_SIZE = 1024  # 1KB
TEST_TOPIC = "genesis.test.speed"

def reader_process(stop_event):
    """
    Process that consumes messages from the bus.
    """
    # Re-mock torch in child process just in case
    sys.modules['torch'] = MagicMock()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Reader")

    reader = HyperSonicReader()
    # Poll until connected
    while not reader.connect():
        time.sleep(0.1)

    received_count = 0
    start_time = None

    while not stop_event.is_set() or received_count < TEST_MSG_COUNT:
        # Read available messages
        messages = list(reader.read())
        if messages:
            if start_time is None:
                start_time = time.time()

            received_count += len(messages)

            # Simple integrity check on last message
            last_ts, last_id, last_topic, last_payload = messages[-1]
            if received_count % 100 == 0:
                logger.info(f"Received {received_count} messages...")

        if received_count >= TEST_MSG_COUNT:
            break

        time.sleep(0.001) # Yield slightly

    end_time = time.time()
    duration = end_time - start_time if start_time else 0
    logger.info(f"Reader Finished. Total: {received_count}, Time: {duration:.4f}s")
    if duration > 0:
        logger.info(f"Throughput: {received_count / duration:.2f} msg/s")

    reader.close()

def run_test():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Main")

    # 1. Start Bus (Writer)
    bus = HyperSonicBus()
    logger.info("Bus Initialized.")

    # 2. Start Reader Process
    stop_event = multiprocessing.Event()
    reader_p = multiprocessing.Process(target=reader_process, args=(stop_event,))
    reader_p.start()

    # Give reader a moment to connect
    time.sleep(0.5)

    # 3. Blast Data
    logger.info(f"Starting write of {TEST_MSG_COUNT} messages...")
    payload = b"X" * PAYLOAD_SIZE

    start_write = time.time()
    for i in range(TEST_MSG_COUNT):
        bus.write(TEST_TOPIC, payload)
        # time.sleep(0.0001) # Optional throttle

    end_write = time.time()
    logger.info(f"Write Finished. Time: {end_write - start_write:.4f}s")

    # 4. Wait for Reader
    reader_p.join(timeout=5)
    if reader_p.is_alive():
        logger.warning("Reader timed out!")
        stop_event.set()
        reader_p.terminate()

    bus.close()
    logger.info("Test Complete.")

if __name__ == "__main__":
    run_test()
