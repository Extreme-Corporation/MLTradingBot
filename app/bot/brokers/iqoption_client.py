from __future__ import annotations

import random
import time
from datetime import datetime
from typing import Dict, List

from iqoptionapi.stable_api import IQ_Option

from app.bot.core.logger import setup_logger


class IQOptionClient:
    def __init__(self, email: str, password: str, mode: str = "practice") -> None:
        self.email = email
        self.password = password
        self.mode = mode
        self.logger = setup_logger("bot.iqoption")
        self.client = IQ_Option(email, password)
        self.connected = False

    def connect(self) -> None:
        check, reason = self.client.connect()
        if not check:
            raise RuntimeError(f"IQ Option connection failed: {reason}")
        self.client.change_balance(self.mode)
        self.connected = True
        self.logger.info("iqoption_connected", extra={"extra": {"mode": self.mode}})

    def get_candles(self, pair: str, timeframe_seconds: int, amount: int) -> List[Dict]:
        now = time.time()
        candles = self.client.get_candles(pair, timeframe_seconds, amount, now)
        return [
            {
                "timestamp": candle["from"],
                "open": candle["open"],
                "close": candle["close"],
                "high": candle["max"],
                "low": candle["min"],
                "volume": candle.get("volume", 0),
            }
            for candle in candles
        ]

    def buy_digital(self, pair: str, direction: str, amount: float, expiry_seconds: int) -> str:
        check, order_id = self.client.buy_digital_spot(pair, direction, amount, expiry_seconds)
        if not check:
            raise RuntimeError("Failed to place digital order")
        return str(order_id)

    def check_win(self, order_id: str) -> float:
        result = self.client.check_win_digital_v2(order_id)
        if result is None:
            return 0.0
        return float(result)


class PaperBroker:
    def __init__(self) -> None:
        self.logger = setup_logger("bot.paper")
        self.orders: Dict[str, Dict] = {}

    def get_candles(self, pair: str, timeframe_seconds: int, amount: int) -> List[Dict]:
        now = int(time.time())
        candles: List[Dict] = []
        price = 1.1
        for i in range(amount):
            base = price + random.uniform(-0.001, 0.001)
            high = base + random.uniform(0.0, 0.001)
            low = base - random.uniform(0.0, 0.001)
            close = base + random.uniform(-0.0005, 0.0005)
            candles.append(
                {
                    "timestamp": now - (amount - i) * timeframe_seconds,
                    "open": base,
                    "close": close,
                    "high": high,
                    "low": low,
                    "volume": random.randint(100, 200),
                }
            )
            price = close
        return candles

    def buy_digital(self, pair: str, direction: str, amount: float, expiry_seconds: int) -> str:
        order_id = f"paper-{int(time.time() * 1000)}"
        self.orders[order_id] = {
            "pair": pair,
            "direction": direction,
            "amount": amount,
            "expiry": expiry_seconds,
            "opened_at": datetime.utcnow(),
        }
        self.logger.info("paper_order_placed", extra={"extra": {"order_id": order_id}})
        return order_id

    def check_win(self, order_id: str) -> float:
        order = self.orders.get(order_id)
        if not order:
            return 0.0
        outcome = random.choice([True, False])
        payout = order["amount"] * (0.82 if outcome else -1)
        return payout
