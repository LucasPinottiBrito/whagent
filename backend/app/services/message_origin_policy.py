from dataclasses import dataclass
from enum import StrEnum


class MessageOrigin(StrEnum):
    CUSTOMER_INBOUND = "customer_inbound"
    HUMAN_OUTBOUND_TAKEOVER = "human_outbound_takeover"
    AGENT_ECHO_IGNORE = "agent_echo_ignore"
    IGNORED_FROM_ME = "ignored_from_me"
    IGNORED_INVALID = "ignored_invalid"
    DUPLICATE = "duplicate"


@dataclass(frozen=True)
class RuntimeOriginConfig:
    allow_from_me_as_inbound: bool = False
    human_handoff_enabled: bool = True


class MessageOriginPolicy:
    def __init__(self, config: RuntimeOriginConfig):
        self.config = config

    def classify(
        self,
        *,
        from_me: bool,
        sent_by_agent: bool,
        source: str | None,
    ) -> MessageOrigin:
        # Agent echoes must not trigger human takeover or reprocessing.
        if sent_by_agent or source == "agent":
            return MessageOrigin.AGENT_ECHO_IGNORE
        if from_me and self.config.allow_from_me_as_inbound:
            return MessageOrigin.CUSTOMER_INBOUND
        if from_me and self.config.human_handoff_enabled:
            return MessageOrigin.HUMAN_OUTBOUND_TAKEOVER
        if from_me:
            return MessageOrigin.IGNORED_FROM_ME
        return MessageOrigin.CUSTOMER_INBOUND
