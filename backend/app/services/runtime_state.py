from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class RuntimeState:
    ai_runtime_enabled: bool
    allow_from_me_as_inbound: bool


_settings = get_settings()
runtime_state = RuntimeState(
    ai_runtime_enabled=_settings.ai_runtime_enabled,
    allow_from_me_as_inbound=_settings.debug_allow_from_me_as_inbound,
)


def reset_runtime_state() -> RuntimeState:
    settings = get_settings()
    runtime_state.ai_runtime_enabled = settings.ai_runtime_enabled
    runtime_state.allow_from_me_as_inbound = settings.debug_allow_from_me_as_inbound
    return runtime_state
