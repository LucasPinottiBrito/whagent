from dataclasses import dataclass
from typing import Any

from app.utils.phone import normalize_phone


@dataclass(frozen=True)
class ParsedEvolutionMessage:
    remote_jid: str
    phone: str
    text: str
    from_me: bool
    message_id: str | None
    push_name: str | None
    sent_by_agent: bool
    source: str | None
    is_group: bool
    raw_payload: dict[str, Any]


class WebhookParseError(ValueError):
    pass


class EvolutionWebhookParser:
    def parse(self, payload: dict[str, Any]) -> ParsedEvolutionMessage:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        key = data.get("key") if isinstance(data.get("key"), dict) else {}
        remote_jid = key.get("remoteJid") or data.get("remoteJid")
        if not remote_jid:
            raise WebhookParseError("payload sem remoteJid")

        text = self._extract_text(data.get("message") or data)
        if not text or not text.strip():
            raise WebhookParseError("payload sem texto reconhecivel")

        source = payload.get("source") or data.get("source")
        sent_by_agent = bool(
            payload.get("sent_by_agent")
            or data.get("sent_by_agent")
            or source == "agent"
        )
        return ParsedEvolutionMessage(
            remote_jid=remote_jid,
            phone=normalize_phone(remote_jid),
            text=text.strip(),
            from_me=bool(key.get("fromMe") or data.get("fromMe")),
            message_id=key.get("id") or data.get("messageId") or data.get("id"),
            push_name=data.get("pushName") or data.get("senderName"),
            sent_by_agent=sent_by_agent,
            source=source,
            is_group=str(remote_jid).endswith("@g.us"),
            raw_payload=payload,
        )

    def _extract_text(self, message: dict[str, Any]) -> str | None:
        if not isinstance(message, dict):
            return None
        if isinstance(message.get("conversation"), str):
            return message["conversation"]
        if isinstance(message.get("text"), str):
            return message["text"]
        for key in ("extendedTextMessage", "imageMessage", "videoMessage"):
            nested = message.get(key)
            if isinstance(nested, dict) and isinstance(nested.get("text"), str):
                return nested["text"]
            if isinstance(nested, dict) and isinstance(nested.get("caption"), str):
                return nested["caption"]
        nested_message = message.get("message")
        if isinstance(nested_message, dict):
            return self._extract_text(nested_message)
        return None
