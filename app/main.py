from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.logger import logger
from app.webhook import router as webhook_router

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Shree Annapure Foods Instagram Auto-Responder")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(webhook_router)


@app.on_event("startup")
async def startup() -> None:
    settings = get_settings()
    logger.info(
        "Application started | instagram_account=%s | graph_api=%s | base_url=%s",
        settings.instagram_business_account_id,
        settings.graph_api_version,
        settings.base_url or "(not set — required for image attachments)",
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
