from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class StrategyContext:
    pair: str
    timeframe: int
    candles: pd.DataFrame


class Strategy:
    name = "base"

    def prepare(self, ctx: StrategyContext) -> None:
        raise NotImplementedError

    def should_enter(self, ctx: StrategyContext) -> str:
        raise NotImplementedError

    def should_exit(self, ctx: StrategyContext) -> bool:
        return False
