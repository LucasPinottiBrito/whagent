import re


def normalize_phone(value: str) -> str:
    jid = value.split("@", 1)[0]
    return re.sub(r"\D+", "", jid)
