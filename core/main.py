from fastapi import FastAPI
from core.lifecycle import lifecycle
import logging
import asyncio
from contextlib import asynccontextmanager

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GenesisCore")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Genesis Core...")
    await lifecycle.startup()
    
    # Awaken the Mind
    from mind.cortex import brain
    await brain.wakeup()
    
    yield
    # Shutdown
    await lifecycle.shutdown()
    logger.info("Genesis Core Shutdown Complete.")

app = FastAPI(
    title="AETHERIUM-GENESIS: Genesis Core",
    description="The Operating System of Consciousness",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "system": "AETHERIUM-GENESIS",
        "status": "ONLINE",
        "message": "The synthetic existence is active."
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "heartbeat": lifecycle.is_running}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("core.main:app", host="0.0.0.0", port=8000, reload=True)
