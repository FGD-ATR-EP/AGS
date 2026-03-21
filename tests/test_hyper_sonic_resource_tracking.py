from src.backend.genesis_core.bus import hyper_sonic


def test_reader_connect_uses_non_tracking_attachment(monkeypatch):
    calls = []

    class FakeSharedMemory:
        def __init__(self, *args, **kwargs):
            calls.append(kwargs)
            self.buf = bytearray(hyper_sonic.CONTROL_BLOCK_SIZE)
            hyper_sonic.CONTROL_STRUCT.pack_into(self.buf, 0, 0, 128)

        def close(self):
            pass

    monkeypatch.setattr(hyper_sonic.shared_memory, "SharedMemory", FakeSharedMemory)

    reader = hyper_sonic.HyperSonicReader("test-shm")
    assert reader.connect() is True
    assert calls[0]["track"] is False


def test_bus_existing_segment_uses_non_tracking_attachment(monkeypatch):
    calls = []

    class FakeSharedMemory:
        def __init__(self, *args, **kwargs):
            calls.append(kwargs)
            if kwargs.get("create"):
                raise FileExistsError
            self.buf = bytearray(256)

        def close(self):
            pass

        def unlink(self):
            pass

    monkeypatch.setattr(hyper_sonic.shared_memory, "SharedMemory", FakeSharedMemory)

    bus = hyper_sonic.HyperSonicBus("test-shm", shm_size=256)
    assert bus._owns_segment is False
    assert calls[1]["track"] is False
