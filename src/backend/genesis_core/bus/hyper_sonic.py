import time
import struct
import uuid
import zlib
import logging
import multiprocessing
from multiprocessing import shared_memory
from typing import Optional, Tuple, Generator

logger = logging.getLogger("HyperSonic")

# Constants
SHM_NAME = "aether_flashpoint_bus"
SHM_SIZE = 16 * 1024 * 1024  # 16 MB
CONTROL_BLOCK_SIZE = 64

# Control Block Structure:
# write_head (unsigned long long - 8 bytes)
# buffer_size (unsigned int - 4 bytes)
# reserved (52 bytes)
CONTROL_STRUCT = struct.Struct("Q I 52x")

# Message Header Structure:
# timestamp (double - 8 bytes)
# msg_id (16 bytes - raw bytes)
# topic_hash (unsigned int - 4 bytes)
# payload_len (unsigned int - 4 bytes)
HEADER_STRUCT = struct.Struct("d 16s I I")
HEADER_SIZE = HEADER_STRUCT.size

# Reserved Topic Hash for Padding/Skip
TOPIC_SKIP = 0xFFFFFFFF


class HyperSonicBus:
    """
    The Writer (Host) for the AetherBus Hyper-Sonic architecture.
    Manages the Shared Memory Ring Buffer and the Write Cursor.
    """
    def __init__(self, shm_name: str = SHM_NAME, shm_size: int = SHM_SIZE):
        self.shm_name = shm_name
        self.shm_size = shm_size
        self.shm: Optional[shared_memory.SharedMemory] = None
        self.buffer = None

        self._initialize_shm()

    def _initialize_shm(self):
        """Creates or connects to the shared memory segment."""
        try:
            # Try to create
            self.shm = shared_memory.SharedMemory(name=self.shm_name, create=True, size=self.shm_size)
            logger.info(f"⚡ [HyperSonic] Created Shared Memory: {self.shm_name} ({self.shm_size} bytes)")

            # Initialize Control Block
            # write_head = 0, buffer_size = actual data size
            data_size = self.shm_size - CONTROL_BLOCK_SIZE
            control_data = CONTROL_STRUCT.pack(0, data_size)
            self.shm.buf[:CONTROL_BLOCK_SIZE] = control_data

        except FileExistsError:
            # Connect to existing
            self.shm = shared_memory.SharedMemory(name=self.shm_name)
            logger.info(f"⚡ [HyperSonic] Connected to existing Shared Memory: {self.shm_name}")

        self.buffer = self.shm.buf

    def _read_control(self) -> Tuple[int, int]:
        """Reads (write_head, buffer_size) from control block."""
        head, size = CONTROL_STRUCT.unpack(self.buffer[:CONTROL_BLOCK_SIZE])
        return head, size

    def _update_write_head(self, new_head: int):
        """Updates the write_head in the control block atomically (Python GIL makes this safe enough for single writer)."""
        # We only update the first 8 bytes (Q)
        struct.pack_into("Q", self.buffer, 0, new_head)

    def write(self, topic: str, payload: bytes) -> str:
        """
        Writes a message to the bus.
        Returns the Message ID (UUID hex string).
        """
        current_head, buffer_limit = self._read_control()

        # Prepare Header Data
        msg_id_bytes = uuid.uuid4().bytes
        topic_hash = zlib.crc32(topic.encode()) & 0xFFFFFFFF
        payload_len = len(payload)
        timestamp = time.time()

        total_msg_size = HEADER_SIZE + payload_len

        # Calculate Offset
        offset = current_head % buffer_limit
        data_start_addr = CONTROL_BLOCK_SIZE + offset
        remaining_space = buffer_limit - offset

        # Check if we need to wrap
        if remaining_space < total_msg_size:
            # Not enough space for the full message.
            # Handle the "end of buffer" scenario.

            # Case 1: Can we fit a Skip Header?
            if remaining_space >= HEADER_SIZE:
                # Write SKIP header
                skip_len = remaining_space - HEADER_SIZE
                header_bytes = HEADER_STRUCT.pack(timestamp, b'\0'*16, TOPIC_SKIP, skip_len)
                self.buffer[data_start_addr : data_start_addr + HEADER_SIZE] = header_bytes
                # We don't need to write payload for SKIP

                # Advance head to wrap around
                current_head += remaining_space
            else:
                # Case 2: Not even enough space for a header (< 32 bytes).
                # Just burn the bytes.
                current_head += remaining_space

            # Now we are aligned at 0 (effectively)
            offset = 0
            data_start_addr = CONTROL_BLOCK_SIZE

        # Write Actual Message
        header_bytes = HEADER_STRUCT.pack(timestamp, msg_id_bytes, topic_hash, payload_len)

        # 1. Write Header
        self.buffer[data_start_addr : data_start_addr + HEADER_SIZE] = header_bytes

        # 2. Write Payload
        payload_start = data_start_addr + HEADER_SIZE
        self.buffer[payload_start : payload_start + payload_len] = payload

        # 3. Update Head
        new_head = current_head + total_msg_size
        self._update_write_head(new_head)

        return uuid.UUID(bytes=msg_id_bytes).hex

    def close(self):
        if self.shm:
            self.shm.close()
            # unlink is risky if other processes are using it, usually handled by a cleanup script or Orchestrator
            try:
                self.shm.unlink()
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class HyperSonicReader:
    """
    The Reader (Consumer) for the AetherBus Hyper-Sonic architecture.
    """
    def __init__(self, shm_name: str = SHM_NAME):
        self.shm_name = shm_name
        self.shm: Optional[shared_memory.SharedMemory] = None
        self.buffer = None
        self.local_head = 0
        self.buffer_limit = 0

    def connect(self) -> bool:
        try:
            self.shm = shared_memory.SharedMemory(name=self.shm_name)
            self.buffer = self.shm.buf

            # Read Buffer Size from Control Block
            _, self.buffer_limit = CONTROL_STRUCT.unpack(self.buffer[:CONTROL_BLOCK_SIZE])

            # Initialize local_head to current write_head (Start fresh)
            # OR start at 0?
            # "Catch-up" logic implies starting at latest or 0.
            # Usually we want to start reading *new* data.
            current_write_head, _ = CONTROL_STRUCT.unpack(self.buffer[:CONTROL_BLOCK_SIZE])
            self.local_head = current_write_head

            logger.info(f"⚡ [HyperSonic Reader] Connected. Head at {self.local_head}")
            return True
        except FileNotFoundError:
            logger.warning(f"⚡ [HyperSonic Reader] SHM '{self.shm_name}' not found.")
            return False
        except Exception as e:
            logger.error(f"⚡ [HyperSonic Reader] Connection Error: {e}")
            return False

    def read(self) -> Generator[Tuple[float, uuid.UUID, int, bytes], None, None]:
        """
        Yields new messages as (timestamp, msg_id, topic_hash, payload).
        """
        if not self.buffer:
            return

        # Read current write head
        write_head, _ = CONTROL_STRUCT.unpack(self.buffer[:CONTROL_BLOCK_SIZE])

        # Check for Overrun (Writer lapped us)
        if write_head - self.local_head > self.buffer_limit:
            logger.warning("⚡ [HyperSonic] Overrun detected! Jumping to latest.")
            self.local_head = write_head
            return

        # Read loop
        while self.local_head < write_head:
            offset = self.local_head % self.buffer_limit
            remaining_space = self.buffer_limit - offset

            # Handle Implicit Skip (Space < Header Size)
            if remaining_space < HEADER_SIZE:
                self.local_head += remaining_space
                continue

            # Read Header
            data_start_addr = CONTROL_BLOCK_SIZE + offset
            header_bytes = bytes(self.buffer[data_start_addr : data_start_addr + HEADER_SIZE])
            timestamp, msg_id_bytes, topic_hash, payload_len = HEADER_STRUCT.unpack(header_bytes)

            # Handle Explicit Skip
            if topic_hash == TOPIC_SKIP:
                total_skip = HEADER_SIZE + payload_len
                self.local_head += total_skip
                continue

            # Read Payload
            payload_start = data_start_addr + HEADER_SIZE
            # Zero-copy optimization: using memoryview/slicing (creates bytes copy here for safety in Python)
            # To be truly zero-copy we'd yield the memoryview, but that risks the writer overwriting it
            # while the user processes it. Safe copy is usually preferred unless logic is very tight.
            payload = bytes(self.buffer[payload_start : payload_start + payload_len])

            # Update local head
            self.local_head += (HEADER_SIZE + payload_len)

            yield timestamp, uuid.UUID(bytes=msg_id_bytes), topic_hash, payload

    def close(self):
        if self.shm:
            self.shm.close()
