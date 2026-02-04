import time
import pytest
from src.backend.departments.presentation.lcl import LightControlLogic
from src.backend.departments.presentation.light_schemas import LightIntent, LightAction, PriorityLevel, LightEntity

def test_gatekeeper_rate_limit():
    lcl = LightControlLogic()
    # Override for testing
    lcl.RATE_LIMIT = 2
    lcl.WINDOW_SIZE = 1.0

    source = "test_source"

    assert lcl._check_rate_limit(source) is True
    assert lcl._check_rate_limit(source) is True
    assert lcl._check_rate_limit(source) is False # 3rd time within window

def test_gatekeeper_priority():
    lcl = LightControlLogic()
    intent_low = LightIntent(action=LightAction.SPAWN, priority=PriorityLevel.AMBIENT, source="test")
    intent_high = LightIntent(action=LightAction.SPAWN, priority=PriorityLevel.USER, source="test")

    assert lcl._check_priority(intent_low) is True
    assert lcl._check_priority(intent_high) is True

def test_metabolism_energy():
    lcl = LightControlLogic()
    lcl.system_energy = 1.0

    # SPAWN costs 2.0
    assert lcl._deduct_energy(LightAction.SPAWN) is False
    assert lcl.system_energy == 1.0

    # MOVE costs 0.5
    assert lcl._deduct_energy(LightAction.MOVE) is True
    assert lcl.system_energy == 0.5

def test_physics_tick():
    lcl = LightControlLogic()
    # Add an entity
    entity = LightEntity(id="e1", position=(0.5, 0.5), velocity=(0.1, 0.0), energy=1.0)
    lcl.entities = {"e1": entity}

    lcl.tick(0.1)

    # Fetch updated state
    updated_entity = lcl.entities["e1"]

    # New x = 0.5 + 0.1 * 0.1 = 0.51
    # Logic applies friction (0.95) BEFORE position update
    # vx = 0.1 * 0.95 = 0.095
    # x = 0.5 + 0.095 * 0.1 = 0.5095
    assert updated_entity.position[0] > 0.5
    assert abs(updated_entity.position[0] - 0.5095) < 0.0001
    # Velocity should decay: 0.1 * 0.95 = 0.095
    assert updated_entity.velocity[0] < 0.1
    assert abs(updated_entity.velocity[0] - 0.095) < 0.0001

def test_target_position_zero_vector():
    lcl = LightControlLogic()
    entity = LightEntity(
        id="e1",
        position=(0.5, 0.5),
        velocity=(0.0, 0.0),
        energy=1.0,
        target_position=(0.0, 0.0)
    )
    lcl.entities = {"e1": entity}

    updated_entity = lcl.entities["e1"]

    assert updated_entity.target_position == (0.0, 0.0)

def test_process_spawn_move():
    lcl = LightControlLogic()

    # Spawn
    intent = LightIntent(action=LightAction.SPAWN, source="test")
    instruction = lcl.process(intent)

    assert instruction is not None
    assert instruction.intent == LightAction.SPAWN
    assert len(lcl.entities) == 1
    entity_id = list(lcl.entities.keys())[0]

    # Move
    intent_move = LightIntent(action=LightAction.MOVE, vector=(1.0, 0.0), source="test")
    instruction = lcl.process(intent_move)

    assert instruction.intent == LightAction.MOVE
    # Velocity should increase
    ent = lcl.entities[entity_id]
    assert ent.velocity[0] > 0.0
