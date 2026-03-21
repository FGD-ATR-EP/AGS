import json
import shutil
import tempfile
from pathlib import Path

import pytest

from src.backend.vessels.workspace import WorkspaceVessel


def build_directive(*, action='write_file', params=None, governance=None, scope=None, actor=None):
    return {
        'type': 'state_update',
        'topic': 'execution.workspace',
        'correlation_id': 'corr-test-001',
        'trace_id': 'trace-test-001',
        'origin': {'service': 'api', 'subsystem': 'body', 'channel': 'session-1'},
        'target': {'service': 'workspace', 'subsystem': 'hands', 'channel': 'adapter'},
        'payload': {
            'action': action,
            'params': params or {'path': 'artifact.txt', 'content': 'hello'},
            'execution_scope': scope or {'system': 'workspace', 'permissions': ['workspace.write']},
            'actor': actor or {'id': 'user-123', 'type': 'human'},
            'metadata': {'source': 'test-suite'},
        },
        'governance': governance or {'validated': True, 'decision': 'ALLOWED', 'risk_tier': 'TIER_1'},
        'memory': {'ledger_event_type': 'execution_requested', 'causal_chain': ['corr-test-001'], 'replayable': True},
    }


@pytest.fixture
def vessel_env():
    temp_dir = tempfile.mkdtemp(prefix='workspace-vessel-')
    ledger_path = Path(temp_dir) / 'akashic_records.json'
    vessel = WorkspaceVessel(workspace_root=temp_dir)
    vessel.ledger.db_path = str(ledger_path)
    vessel.ledger.ensure_db()
    try:
        yield vessel, Path(temp_dir), ledger_path
    finally:
        shutil.rmtree(temp_dir)


def test_workspace_vessel_uses_canonical_directive_and_logs_outcome(vessel_env):
    vessel, temp_dir, ledger_path = vessel_env

    preview = vessel.preview(build_directive())
    assert 'Write file' in preview.plan

    result = vessel.execute(build_directive())
    assert result['status'] == 'ok'
    assert result['memory']['ledger_record_id']
    assert result['memory']['correlation_id'] == 'corr-test-001'
    assert (temp_dir / 'artifact.txt').read_text() == 'hello'

    ledger = json.loads(ledger_path.read_text())
    assert len(ledger['chain']) == 1
    block = ledger['chain'][0]
    assert block['payload']['type'] == 'execution_outcome'
    assert block['payload']['action'] == 'write_file'
    assert block['correlation']['correlation_id'] == 'corr-test-001'


def test_workspace_vessel_blocks_unvalidated_governance(vessel_env):
    vessel, _, _ = vessel_env
    directive = build_directive(governance={'validated': False, 'decision': 'ALLOWED', 'risk_tier': 'TIER_1'})

    with pytest.raises(PermissionError):
        vessel.execute(directive)


def test_workspace_vessel_blocks_missing_execution_scope(vessel_env):
    vessel, _, _ = vessel_env
    directive = build_directive(scope={'system': 'workspace'})

    with pytest.raises(ValueError):
        vessel.preview(directive)


def test_workspace_vessel_blocks_hardcoded_credentials(vessel_env):
    vessel, _, _ = vessel_env
    directive = build_directive(params={'path': 'artifact.txt', 'content': 'hello', 'api_key': 'plaintext-secret'})

    with pytest.raises(ValueError):
        vessel.preview(directive)


def test_workspace_vessel_allows_secret_reference_convention(vessel_env):
    vessel, _, _ = vessel_env
    directive = build_directive(params={'path': 'artifact.txt', 'content': 'hello', 'api_key': '${WORKSPACE_API_KEY}'})

    preview = vessel.preview(directive)
    assert preview.evidence['path'] == 'artifact.txt'
