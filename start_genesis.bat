@echo off
echo [AETHERIUM-GENESIS] Initiating Awakening Sequence...
echo [BOOT] Loading Environment...

REM Install dependencies if not present (Optional check, simplified here)
REM pip install -r requirements.txt

echo [BOOT] Starting Genesis Core...
uvicorn core.main:app --host 0.0.0.0 --port 8000 --reload

pause
