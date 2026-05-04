from dataclasses import dataclass
from typing import Any

from app.utils.phone import normalize_phone


@dataclass(frozen=True)
class ParsedWebhookMessage:
    phone: str
    text: str
    from_me: bool
    message_id: str | None
    customer_name: str | None
    sent_by_agent: bool


class WebhookParseError(ValueError):
    pass


def parse_evolution_webhook(payload: dict[str, Any]) -> ParsedWebhookMessage:
    data = payload.get("data") or payload
    key = data.get("key") or {}
    remote_jid = key.get("remoteJid") or data.get("remoteJid")
    if not remote_jid:
        raise WebhookParseError("payload sem remoteJid")

    text = _extract_text(data.get("message") or data)
    if not text:
        raise WebhookParseError("payload sem texto de mensagem")

    sent_by_agent = bool(
        payload.get("sent_by_agent")
        or payload.get("source") == "agent"
        or data.get("sent_by_agent")
        or data.get("source") == "agent"
    )

    return ParsedWebhookMessage(
        phone=normalize_phone(remote_jid),
        text=text.strip(),
        from_me=bool(key.get("fromMe") or data.get("fromMe")),
        message_id=key.get("id") or data.get("messageId") or data.get("id"),
        customer_name=data.get("pushName") or data.get("senderName"),
        sent_by_agent=sent_by_agent,
    )


def _extract_text(message: dict[str, Any]) -> str | None:
    if "conversation" in message:
        return message.get("conversation")
    if "text" in message:
        return message.get("text")
    if "extendedTextMessage" in message:
        return message["extendedTextMessage"].get("text")
    if "imageMessage" in message:
        return message["imageMessage"].get("caption")
    if "videoMessage" in message:
        return message["videoMessage"].get("caption")
    if "message" in message and isinstance(message["message"], dict):
        return _extract_text(message["message"])
    return None
