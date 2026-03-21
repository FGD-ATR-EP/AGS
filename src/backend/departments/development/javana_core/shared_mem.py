import struct

# JAVANA: Shared Memory Implementation
# Zero-Copy Philosophy: Store raw bytes, ready for C-interop.

class JavanaMemory:
    """
    A simulated shared memory block for JAVANA.
    Uses a fixed-size bytearray to store critical state variables.
    Layout:
      [0-3]   Energy (float)
      [4-7]   X Coordinate (float)
      [8-11]  Y Coordinate (float)
      [12-15] Turbulence (float)
    """
    __slots__ = ('_buffer', '_struct')

    def __init__(self):
        # Allocate 16 bytes for 4 floats
        self._buffer = bytearray(16)
        # Struct format: Little-endian (<), 4 floats (ffff)
        self._struct = struct.Struct('<ffff')

    def write(self, energy: float, x: float, y: float, turbulence: float):
        """
        Writes raw sensor data into the memory block.
        This is a zero-copy operation (in C terms) because we overwrite the buffer in place.
        """
        # Clamp values for safety? Or just raw speed? Raw Speed.
        self._struct.pack_into(self._buffer, 0, energy, x, y, turbulence)

    def read(self) -> tuple:
        """
        Reads the current state from the memory block.
        Returns: (energy, x, y, turbulence)
        """
        return self._struct.unpack_from(self._buffer, 0)

    @property
    def buffer_address(self) -> int:
        """Returns the memory address of the buffer (for debug/future C-binding)."""
        import ctypes
        return ctypes.addressof(ctypes.c_char.from_buffer(self._buffer))
