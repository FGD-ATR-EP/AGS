"""
Tests for the "Operational Quick Reference (Contributor Template Filled)" section
added to AGENTS.md in this PR.

These tests validate that the documentation section is present, structurally correct,
and contains the precise commands and guidance that contributors rely on.
"""

import re
from pathlib import Path

AGENTS_MD = Path(__file__).parent.parent / "AGENTS.md"


def _read_agents_md() -> str:
    return AGENTS_MD.read_text(encoding="utf-8")


def _extract_quick_reference_section(content: str) -> str:
    """Return only the text of the Operational Quick Reference section."""
    match = re.search(
        r"(## Operational Quick Reference.*)",
        content,
        re.DOTALL,
    )
    assert match, "Operational Quick Reference section not found in AGENTS.md"
    return match.group(1)


# ---------------------------------------------------------------------------
# Section presence
# ---------------------------------------------------------------------------

def test_quick_reference_section_exists():
    content = _read_agents_md()
    assert "## Operational Quick Reference (Contributor Template Filled)" in content


def test_quick_reference_section_is_not_empty():
    content = _read_agents_md()
    section = _extract_quick_reference_section(content)
    # Must contain more than just the heading line
    assert len(section.strip().splitlines()) > 2


# ---------------------------------------------------------------------------
# Required subsections
# ---------------------------------------------------------------------------

REQUIRED_SUBSECTIONS = [
    "### Project Overview",
    "### Setup Commands",
    "### Development Workflow",
    "### Testing Instructions",
    "### Code Style",
    "### Build and Deployment",
    "### Pull Request Guidelines",
    "### Additional Notes",
]


def test_all_required_subsections_present():
    content = _read_agents_md()
    section = _extract_quick_reference_section(content)
    for heading in REQUIRED_SUBSECTIONS:
        assert heading in section, f"Missing subsection: {heading!r}"


def test_subsections_appear_in_correct_order():
    content = _read_agents_md()
    section = _extract_quick_reference_section(content)
    positions = [section.index(h) for h in REQUIRED_SUBSECTIONS]
    assert positions == sorted(positions), (
        "Subsections are not in the expected order within the Quick Reference section"
    )


# ---------------------------------------------------------------------------
# Project Overview content
# ---------------------------------------------------------------------------

def test_project_overview_names_aetherium_genesis():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "AETHERIUM-GENESIS" in section


def test_project_overview_lists_fastapi():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "FastAPI" in section


def test_project_overview_lists_uvicorn():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "Uvicorn" in section


def test_project_overview_lists_pytest():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "Pytest" in section or "pytest" in section


def test_project_overview_references_frontend_path():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "src/frontend/" in section


# ---------------------------------------------------------------------------
# Setup Commands content
# ---------------------------------------------------------------------------

def test_setup_commands_base_requirements():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "pip install -r requirements.txt" in section


def test_setup_commands_optional_ml_visual_requirements():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "pip install -r requirements/optional-ml-visual.txt" in section


def test_setup_commands_dev_requirements():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "pip install -r requirements/dev.txt" in section


def test_setup_commands_awaken_entrypoint():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "python awaken.py" in section


def test_setup_commands_uvicorn_asgi_invocation():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "python -m uvicorn src.backend.main:app" in section


def test_setup_commands_uvicorn_host_port():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "--host 0.0.0.0 --port 8000" in section


# ---------------------------------------------------------------------------
# Testing Instructions content
# ---------------------------------------------------------------------------

REQUIRED_TEST_FILES = [
    "tests/test_aetherium_api.py",
    "tests/test_integration_ui.py",
    "tests/test_frontend_homepage.py",
]


def test_testing_instructions_targeted_regression_command():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "pytest -q" in section
    for test_file in REQUIRED_TEST_FILES:
        assert test_file in section, f"Missing test file reference: {test_file!r}"


def test_testing_instructions_run_all_tests_command():
    section = _extract_quick_reference_section(_read_agents_md())
    # "pytest -q" on its own line covers running all tests
    lines = section.splitlines()
    full_suite_lines = [l for l in lines if "pytest -q" in l and "tests/" not in l]
    assert full_suite_lines, "No standalone 'pytest -q' (run-all) command found"


def test_testing_instructions_coverage_command():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "--cov=src" in section
    assert "--cov-report=term-missing" in section


# ---------------------------------------------------------------------------
# Code Style content
# ---------------------------------------------------------------------------

SUBSYSTEM_NAMES = ["Mind", "Kernel", "Bus", "Hands", "Memory", "Body"]


def test_code_style_subsystem_boundaries_all_present():
    section = _extract_quick_reference_section(_read_agents_md())
    for subsystem in SUBSYSTEM_NAMES:
        assert subsystem in section, f"Missing subsystem name: {subsystem!r}"


def test_code_style_governance_bypass_prohibition():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "Do not bypass governance checks" in section


def test_code_style_frontend_manifestation_constraint():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "manifestation-only" in section


# ---------------------------------------------------------------------------
# Build and Deployment content
# ---------------------------------------------------------------------------

def test_build_deployment_asgi_app_target():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "src.backend.main:app" in section


def test_build_deployment_route_references():
    section = _extract_quick_reference_section(_read_agents_md())
    for route in ["/", "/dashboard", "/public", "/docs"]:
        assert route in section, f"Missing route reference: {route!r}"


def test_build_deployment_docs_reference():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "docs/" in section


# ---------------------------------------------------------------------------
# Pull Request Guidelines content
# ---------------------------------------------------------------------------

def test_pr_guidelines_title_format():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "[component] Brief description" in section


def test_pr_guidelines_required_checks_command():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "pytest -q tests/test_aetherium_api.py tests/test_integration_ui.py tests/test_frontend_homepage.py" in section


def test_pr_guidelines_low_blast_radius():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "low-blast-radius" in section


# ---------------------------------------------------------------------------
# Additional Notes content
# ---------------------------------------------------------------------------

def test_additional_notes_protocol_clarity():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "protocol clarity" in section


def test_additional_notes_auditability():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "auditability" in section


def test_additional_notes_no_hidden_coupling():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "hidden coupling" in section


def test_additional_notes_manifestation_faithful_to_backend():
    section = _extract_quick_reference_section(_read_agents_md())
    assert "faithful to backend-decided state" in section


# ---------------------------------------------------------------------------
# Regression / boundary / negative cases
# ---------------------------------------------------------------------------

def test_agents_md_file_is_readable_and_nonempty():
    """Basic file health check — regression guard against accidental truncation."""
    content = _read_agents_md()
    assert len(content) > 1000, "AGENTS.md appears unexpectedly short"


def test_quick_reference_section_is_last_major_section():
    """The Quick Reference section was appended at the end; it must appear after
    the Agent Status Log section."""
    content = _read_agents_md()
    agent_status_pos = content.find("## Agent Status Log")
    quick_ref_pos = content.find("## Operational Quick Reference")
    assert agent_status_pos != -1, "Agent Status Log section not found"
    assert quick_ref_pos != -1, "Operational Quick Reference section not found"
    assert quick_ref_pos > agent_status_pos, (
        "Operational Quick Reference must appear after Agent Status Log"
    )


def test_quick_reference_preceded_by_horizontal_rule():
    """Section should be separated from prior content with a markdown '---' rule."""
    content = _read_agents_md()
    quick_ref_pos = content.find("## Operational Quick Reference")
    assert quick_ref_pos != -1
    preceding_text = content[:quick_ref_pos]
    # The '---' separator must appear in the 100 characters before the heading
    nearby = preceding_text[-100:]
    assert "---" in nearby, (
        "Expected a '---' horizontal rule immediately before the Quick Reference section"
    )


def test_no_placeholder_text_in_quick_reference():
    """Verify that no generic template placeholder tokens remain unfilled."""
    section = _extract_quick_reference_section(_read_agents_md())
    placeholders = ["<your_project>", "<TODO>", "PLACEHOLDER", "TBD", "FIXME"]
    for placeholder in placeholders:
        assert placeholder not in section, (
            f"Unfilled template placeholder found: {placeholder!r}"
        )


def test_quick_reference_heading_exact_text():
    """Guard against subtle heading typos that would break tooling that
    parses this heading by exact string."""
    content = _read_agents_md()
    assert "## Operational Quick Reference (Contributor Template Filled)" in content