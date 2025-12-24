from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="IQ Option Bot API")


class OrderSchema(BaseModel):
    order_id: str
    pair: str
    direction: str
    amount: float
    expiry: int
    status: str
    opened_at: datetime
    closed_at: datetime | None = None
    pnl: float | None = None


class SessionSchema(BaseModel):
    session_id: str
    status: str
    started_at: datetime


class StatsSchema(BaseModel):
    winrate: float
    pnl: float
    trades: int


_sessions: List[SessionSchema] = []
_orders: List[OrderSchema] = []
_stats = StatsSchema(winrate=0.0, pnl=0.0, trades=0)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def get_config() -> Dict[str, str]:
    return {"strategy": "ema_rsi_fractal", "mode": "paper"}


@app.get("/sessions")
def get_sessions() -> List[SessionSchema]:
    return _sessions


@app.get("/orders")
def get_orders() -> List[OrderSchema]:
    return _orders


@app.get("/stats")
def get_stats() -> StatsSchema:
    return _stats
