from __future__ import annotations

from datetime import datetime


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_ratio(a: int | None, b: int | None) -> float | None:
    if a is None or b in (None, 0):
        return None
    return round(a / b, 4)
