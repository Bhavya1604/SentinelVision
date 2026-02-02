"""
SentinelVision FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: log config. Shutdown: nothing to clean."""
    settings = get_settings()
    logger.info("Starting %s (debug=%s)", settings.app_name, settings.debug)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="SentinelVision",
    description="Production-ready image moderation API with multi-label classification and explainability.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    """Health check for load balancers and Docker."""
    return {"status": "ok", "service": "SentinelVision"}
