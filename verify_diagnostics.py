import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.diagnostic_api import replay_console, simulate_policy, diff_inspector, execution_ledger
import asyncio

async def test_diagnostics():
    print("--- Testing Replay Console ---")
    replay = await replay_console("session-xyz")
    print(replay)
    
    print("\n--- Testing Diff Inspector ---")
    diff = await diff_inspector("intent-123")
    print(diff)
    
    print("\n--- Testing Governance Simulator ---")
    sim = await simulate_policy({"action": "fire_weapons", "target": "enemy_base"})
    print(sim)
    
    print("\n--- Testing Execution Ledger ---")
    ledger = await execution_ledger()
    print(ledger)

if __name__ == "__main__":
    asyncio.run(test_diagnostics())
