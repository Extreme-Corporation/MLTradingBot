from __future__ import annotations

import time
from datetime import datetime
from typing import Callable, Dict, List

import pandas as pd

from app.bot.core.logger import setup_logger
from app.bot.core.risk import RiskManager, RiskState
from app.bot.core.session import Order, SessionState
from app.bot.strategies.base import StrategyContext


class TradingEngine:
    def __init__(
        self,
        strategy_name: str,
        strategy_factory: Callable[[], "Strategy"],
        fetch_candles: Callable[[str, int, int], List[Dict]],
        place_order: Callable[[str, str, float, int], str],
        check_order: Callable[[str], float],
        pair: str,
        timeframe_seconds: int,
        expiry_seconds: int,
        risk: RiskManager,
        initial_balance: float,
    ) -> None:
        self.strategy = strategy_factory()
        self.fetch_candles = fetch_candles
        self.place_order = place_order
        self.check_order = check_order
        self.pair = pair
        self.timeframe_seconds = timeframe_seconds
        self.expiry_seconds = expiry_seconds
        self.risk = risk
        self.state = RiskState(balance=initial_balance)
        self.session = SessionState(session_id=f"session-{int(time.time())}")
        self.logger = setup_logger("bot.engine")
        self.strategy_name = strategy_name

    def run_once(self) -> None:
        candles = self.fetch_candles(self.pair, self.timeframe_seconds, 200)
        df = pd.DataFrame(candles)
        ctx = StrategyContext(pair=self.pair, timeframe=self.timeframe_seconds, candles=df)
        signal = self.strategy.should_enter(ctx)

        if not self.risk.can_trade(self.state):
            self.logger.info(
                "risk_limits_reached",
                extra={"extra": {"balance": self.state.balance, "daily_pnl": self.state.daily_pnl}},
            )
            return

        if signal == "HOLD":
            return

        amount = self.risk.position_size(self.state)
        order_id = self.place_order(self.pair, signal.lower(), amount, self.expiry_seconds)
        order = Order(
            order_id=order_id,
            pair=self.pair,
            direction=signal,
            amount=amount,
            expiry=self.expiry_seconds,
            status="open",
            opened_at=datetime.utcnow(),
        )
        self.session.orders.append(order)
        self.logger.info(
            "order_placed",
            extra={"extra": {"order_id": order_id, "signal": signal, "amount": amount}},
        )
        pnl = self.check_order(order_id)
        order.status = "closed"
        order.closed_at = datetime.utcnow()
        order.pnl = pnl
        self.risk.update_after_trade(self.state, pnl)
        self.logger.info(
            "order_closed",
            extra={"extra": {"order_id": order_id, "pnl": pnl, "balance": self.state.balance}},
        )

    def loop(self, sleep_seconds: int = 1) -> None:
        self.session.status = "running"
        self.logger.info("engine_started", extra={"extra": {"strategy": self.strategy_name}})
        while self.session.status == "running":
            self.run_once()
            time.sleep(sleep_seconds)

    def stop(self) -> None:
        self.session.status = "stopped"
