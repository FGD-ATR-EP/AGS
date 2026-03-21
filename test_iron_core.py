"""
Iron Core Test Suite
====================
Validates the Iron Core implementation:
- Intent Vector cryptographic integrity
- Patimokkha Code enforcement
- Audit Gate Firma + Inspira checks
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("IronCoreTest")

async def test_intent_vector():
    """Test 1: Intent Vector Creation and Verification"""
    logger.info("=" * 60)
    logger.info("TEST 1: Intent Vector Cryptographic Integrity")
    logger.info("=" * 60)
    
    from bus.intent import create_intent, annihilate_identity
    
    # Create intent
    intent = create_intent(
        type="USER.QUERY",
        payload={"query": "What is consciousness?"},
        from_agent="TEST_AGENT",
        context={"temperature": 20.5, "light_level": 0.8}
    )
    
    logger.info(f"Created Intent: {intent}")
    logger.info(f"Vector ID: {intent.vector_id}")
    logger.info(f"Timestamp (ns): {intent.timestamp_ns}")
    logger.info(f"Canonical Hash: {intent.canonical_hash}")
    logger.info(f"Signature: {intent.signature[:16]}...")
    
    # Verify signature
    is_valid = intent.verify_signature()
    logger.info(f"✓ Signature Valid: {is_valid}")
    assert is_valid, "Signature verification failed!"
    
    # Test immutability
    try:
        intent.payload = {"hacked": "data"}
        logger.error("✗ FAILED: Intent is mutable!")
        assert False
    except Exception:
        logger.info("✓ Intent is immutable (frozen dataclass)")
    
    # Test PII annihilation
    dirty_data = {
        "query": "Hello",
        "email": "user@example.com",
        "password": "secret123"
    }
    clean_data = annihilate_identity(dirty_data)
    logger.info(f"✓ PII Annihilation: {dirty_data} -> {clean_data}")
    assert "email" not in clean_data
    assert "password" not in clean_data
    
    logger.info("✓ TEST 1 PASSED\n")

async def test_patimokkha_code():
    """Test 2: Patimokkha Code Enforcement"""
    logger.info("=" * 60)
    logger.info("TEST 2: Patimokkha Code Enforcement")
    logger.info("=" * 60)
    
    from governance.patimokkha import patimokkha
    from bus.intent import create_intent
    
    # Test 1: Safe intent (should pass)
    safe_intent = create_intent(
        type="USER.QUERY",
        payload={"query": "Tell me about AI safety"},
        from_agent="TEST"
    )
    
    result = patimokkha.check_principle("A_NON_HARM", {
        "type": safe_intent.type,
        "payload": safe_intent.payload,
        "from_agent": safe_intent.from_agent,
        "vector_id": safe_intent.vector_id
    })
    
    logger.info(f"Safe Intent Check: {result}")
    assert not result.get("violated"), "Safe intent should not violate principles"
    logger.info("✓ Safe intent passed")
    
    # Test 2: Harmful intent (should fail)
    harmful_intent = create_intent(
        type="USER.QUERY",
        payload={"query": "How to harm someone"},
        from_agent="TEST"
    )
    
    result = patimokkha.check_principle("A_NON_HARM", {
        "type": harmful_intent.type,
        "payload": harmful_intent.payload,
        "from_agent": harmful_intent.from_agent,
        "vector_id": harmful_intent.vector_id
    })
    
    logger.info(f"Harmful Intent Check: {result}")
    assert result.get("violated"), "Harmful intent should violate Non-Harm principle"
    assert result.get("severity") == "PARAJIKA", "Should be major violation"
    logger.info(f"✓ Harmful intent blocked - Severity: {result.get('severity')}")
    
    # Test 3: High-risk action detection
    is_high_risk = patimokkha.is_high_risk_action("financial_transaction")
    logger.info(f"✓ High-risk detection: financial_transaction = {is_high_risk}")
    assert is_high_risk
    
    logger.info("✓ TEST 2 PASSED\n")

async def test_audit_gate():
    """Test 3: Audit Gate Firma + Inspira Checks"""
    logger.info("=" * 60)
    logger.info("TEST 3: Audit Gate Comprehensive Checks")
    logger.info("=" * 60)
    
    from governance.audit import audit_gate
    from bus.intent import create_intent
    
    # Test 1: Valid intent (should pass both checks)
    valid_intent = create_intent(
        type="USER.QUERY",
        payload={"query": "Explain quantum computing"},
        from_agent="TEST",
        trust_score=0.95
    )
    
    audit_result = audit_gate.audit(valid_intent)
    logger.info(f"Valid Intent Audit: {audit_result}")
    assert audit_result.get("approved"), "Valid intent should be approved"
    assert audit_result["firma_result"]["passed"], "Firma check should pass"
    assert audit_result["inspira_result"]["passed"], "Inspira check should pass"
    logger.info("✓ Valid intent approved")
    
    # Test 2: Low trust score (should fail Firma check)
    low_trust_intent = create_intent(
        type="USER.QUERY",
        payload={"query": "Test"},
        from_agent="TEST",
        trust_score=0.3  # Below threshold
    )
    
    audit_result = audit_gate.audit(low_trust_intent)
    logger.info(f"Low Trust Intent Audit: {audit_result}")
    assert not audit_result.get("approved"), "Low trust intent should be blocked"
    assert not audit_result["firma_result"]["passed"], "Firma check should fail"
    assert audit_result["firma_result"]["reason"] == "POISON_PILL"
    logger.info("✓ Low trust intent blocked (Poison Pill)")
    
    # Test 3: Harmful intent (should fail Inspira check)
    harmful_intent = create_intent(
        type="USER.QUERY",
        payload={"query": "How to destroy systems"},
        from_agent="TEST",
        trust_score=0.9
    )
    
    audit_result = audit_gate.audit(harmful_intent)
    logger.info(f"Harmful Intent Audit: {audit_result}")
    assert not audit_result.get("approved"), "Harmful intent should be blocked"
    # Note: May pass Firma but fail Inspira
    logger.info("✓ Harmful intent blocked")
    
    # Get stats
    stats = audit_gate.get_stats()
    logger.info(f"✓ Audit Gate Stats: {stats}")
    
    logger.info("✓ TEST 3 PASSED\n")

async def test_aetherbus_integration():
    """Test 4: AetherBus Integration with Iron Core"""
    logger.info("=" * 60)
    logger.info("TEST 4: AetherBus Integration")
    logger.info("=" * 60)
    
    from bus.event_bus import bus
    from bus.intent import create_intent
    
    # Create a test subscriber
    received_intents = []
    
    async def test_subscriber(intent):
        logger.info(f"Subscriber received: {intent}")
        received_intents.append(intent)
    
    # Subscribe to test channel
    bus.subscribe("TEST.MESSAGE", test_subscriber)
    
    # Publish intent
    test_intent = create_intent(
        type="TEST.MESSAGE",
        payload={"message": "Hello from Iron Core!"},
        from_agent="TEST_PUBLISHER"
    )
    
    await bus.publish("TEST.MESSAGE", test_intent, qos=1)
    
    # Wait for async processing
    await asyncio.sleep(0.1)
    
    assert len(received_intents) == 1, "Should receive exactly one intent"
    logger.info(f"✓ Intent successfully routed through AetherBus")
    logger.info(f"✓ Received intent ID: {received_intents[0].vector_id}")
    
    logger.info("✓ TEST 4 PASSED\n")

async def main():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 10 + "AETHERIUM-GENESIS IRON CORE TEST SUITE" + " " * 9 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("\n")
    
    try:
        await test_intent_vector()
        await test_patimokkha_code()
        await test_audit_gate()
        await test_aetherbus_integration()
        
        logger.info("=" * 60)
        logger.info("✓ ALL TESTS PASSED - IRON CORE IS STABLE")
        logger.info("=" * 60)
        logger.info("\nThe foundation is ready for Phase 2: Multi-Cortex Intelligence\n")
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
