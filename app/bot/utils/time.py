from __future__ import annotations

from datetime import datetime, timezone


def next_candle_expiry(timeframe_seconds: int) -> int:
    now = datetime.now(timezone.utc).timestamp()
    return int((int(now / timeframe_seconds) + 1) * timeframe_seconds)
