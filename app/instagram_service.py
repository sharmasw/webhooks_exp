import httpx

from app.config import get_settings
from app.logger import logger


def build_static_image_url(filename: str) -> str:
    settings = get_settings()
    base_url = settings.base_url
    if not base_url:
        raise ValueError(
            "PUBLIC_BASE_URL or RENDER_EXTERNAL_URL must be set to send image attachments"
        )
    return f"{base_url}/static/{filename}"


async def send_text_message(recipient_id: str, text: str) -> dict | None:
    settings = get_settings()
    params = {"access_token": settings.meta_page_access_token}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(settings.messages_api_url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Text message sent to %s | message_id=%s", recipient_id, data.get("message_id"))
            return data
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Failed to send text message | status=%s | body=%s",
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("Failed to send text message | error=%s", exc)
        return None


async def send_image_message(recipient_id: str, image_url: str) -> dict | None:
    settings = get_settings()
    params = {"access_token": settings.meta_page_access_token}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url},
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(settings.messages_api_url, params=params, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("Image message sent to %s | message_id=%s", recipient_id, data.get("message_id"))
            return data
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Failed to send image message | status=%s | body=%s",
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.RequestError as exc:
        logger.error("Failed to send image message | error=%s", exc)
        return None
