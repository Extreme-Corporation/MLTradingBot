from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class Order:
    order_id: str
    pair: str
    direction: str
    amount: float
    expiry: int
    status: str
    opened_at: datetime
    closed_at: datetime | None = None
    pnl: float | None = None


@dataclass
class SessionState:
    session_id: str
    status: str = "idle"
    started_at: datetime = field(default_factory=datetime.utcnow)
    orders: List[Order] = field(default_factory=list)
    stats: Dict[str, float] = field(default_factory=dict)
