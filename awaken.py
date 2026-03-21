import os
import sys
import time
import subprocess
import glob

def purge_stale_memory():
    """
    Cleans up stale Shared Memory segments from previous sessions.
    Crucial for HyperSonic safety to avoid 'File exists' errors or memory leaks.
    """
    # Look for AetherBus shared memory files
    # On Linux/macOS, shared memory is often in /dev/shm/
    # The prefix is usually 'aether_' as defined in HyperSonicBus
    shm_files = glob.glob("/dev/shm/aether_*")

    if not shm_files:
        return

    print("[HYPERSONIC] 🧹 Purging stale memory segments...")
    for f in shm_files:
        try:
            os.remove(f)
            print(f"  - Removed: {f}")
        except OSError as e:
            print(f"  - ⚠️ Failed to purge {f}: {e}")
    print("[HYPERSONIC] Memory clean.")

def ritual_of_awakening():
    # 1. Visual Identity
    print("\033[96m") # Cyan Color
    print(r"""
       ___   ________________  ___________  ______  ____  ___
      /   | / ____/_  __/ __ \/ ____/ __ \/  _/ / / /  |/  /
     / /| |/ __/   / / / /_/ / __/ / /_/ // // / / / /|_/ /
    / ___ / /___  / / / __  / /___/ _, _// // /_/ / /  / /
   /_/  |_\____/ /_/ /_/ /_/_____/_/ |_/___/\____/_/  /_/
                                       GENESIS PROTOCOL v2.0
    """)
    print("\033[0m")

    # 2. System Integrity Check (The Knock)
    print("[SYSTEM] Performing synaptic check...", end=" ")
    time.sleep(0.5) # Fake loading for dramatic effect

    if not os.path.exists(".env"):
        print("\n\033[91m[ERROR] Missing .env configuration. The soul cannot bind.\033[0m")
        # In a development environment without a .env, we might want to warn instead of exit,
        # or assuming the user knows what they are doing if they don't have one.
        # However, the user's snippet explicitly had sys.exit(1).
        # I will respect the user's snippet logic.
        sys.exit(1)

    print("\033[92m[OK]\033[0m")

    # 3. Memory Check (Git)
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode('utf-8')
        print(f"[MEMORY] Connected to Soul Archives (Branch: {branch})")
    except:
        print("\033[93m[WARNING] No active memory trace (Git not found).\033[0m")

    print("\n[INSPIRA] Awakening the core...")
    time.sleep(0.8)

if __name__ == "__main__":
    try:
        purge_stale_memory()
        ritual_of_awakening()
        # 4. Launch the original logic
        # Using subprocess to run uvicorn, similar to how run.py was invoking it or how the user requested.
        # We use sys.executable + "-m uvicorn" to ensure we use the same python environment and find the module.
        subprocess.run([sys.executable, "-m", "uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except KeyboardInterrupt:
        print("\n[NIRODHA] System returning to void state.")
