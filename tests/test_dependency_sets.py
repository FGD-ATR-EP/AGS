from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]


def test_root_requirements_points_to_runtime_split():
    assert _lines(ROOT / "requirements.txt") == ["-r requirements/runtime.txt"]


def test_runtime_and_dev_splits_are_present():
    runtime_lines = _lines(ROOT / "requirements/runtime.txt")
    dev_lines = _lines(ROOT / "requirements/dev.txt")
    optional_lines = _lines(ROOT / "requirements/optional-ml-visual.txt")

    assert runtime_lines == ["-r base.txt"]
    assert "-r runtime.txt" in dev_lines
    assert "-r optional-ml-visual.txt" in dev_lines
    assert "pytest" in dev_lines
    assert "sentence-transformers" in optional_lines
