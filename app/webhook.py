import hashlib
import hmac
import json
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request, Response

from app.config import get_settings
from app import keyword_engine
from app.instagram_service import build_static_image_url, send_image_message, send_text_message
from app.logger import logger

router = APIRouter()


def _validate_signature(raw_body: bytes, signature_header: str | None) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False

    settings = get_settings()
    expected = hmac.new(
        settings.meta_app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)


async def _process_messaging_event(messaging_event: dict[str, Any], entry_id: str) -> None:
    settings = get_settings()

    if entry_id != settings.instagram_business_account_id:
        logger.info("Skipping event for unrelated account | entry_id=%s", entry_id)
        return

    message = messaging_event.get("message", {})
    if message.get("is_echo"):
        logger.info("Skipping echo message")
        return

    text = message.get("text")
    if not text:
        logger.info("Skipping non-text message")
        return

    sender_id = messaging_event.get("sender", {}).get("id")
    timestamp = messaging_event.get("timestamp")

    if not sender_id:
        logger.warning("Missing sender id in messaging event")
        return

    logger.info("Incoming message | sender=%s | timestamp=%s | text=%s", sender_id, timestamp, text)

    match = keyword_engine.match(text)
    logger.info("Matched keyword rule | rule=%s", match.rule_name)

    await send_text_message(sender_id, match.response_text)

    if match.image_filename:
        try:
            image_url = build_static_image_url(match.image_filename)
            await send_image_message(sender_id, image_url)
        except ValueError as exc:
            logger.error("Could not build image URL | error=%s", exc)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> Response:
    settings = get_settings()

    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        logger.info("Webhook verification succeeded")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning("Webhook verification failed")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request) -> dict[str, str]:
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    if not _validate_signature(raw_body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = json.loads(raw_body)
    logger.info("Webhook received | payload=%s", json.dumps(payload))

    if payload.get("object") != "instagram":
        logger.info("Ignoring non-instagram webhook | object=%s", payload.get("object"))
        return {"status": "ok"}

    for entry in payload.get("entry", []):
        entry_id = entry.get("id", "")
        for messaging_event in entry.get("messaging", []):
            try:
                await _process_messaging_event(messaging_event, entry_id)
            except Exception:
                logger.exception("Error processing messaging event")

    return {"status": "ok"}
