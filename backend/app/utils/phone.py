import re


def normalize_phone(value: str) -> str:
    local = value.split("@", 1)[0]
    return re.sub(r"\D", "", local)
