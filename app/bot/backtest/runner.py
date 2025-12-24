from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from app.bot.core.logger import setup_logger
from app.bot.core.risk import RiskManager, RiskState
from app.bot.strategies.base import StrategyContext


@dataclass
class BacktestResult:
    trades: int
    wins: int
    losses: int
    winrate: float
    equity_curve_path: Path


class BacktestRunner:
    def __init__(
        self,
        strategy_factory: Callable[[], "Strategy"],
        risk: RiskManager,
        initial_balance: float,
    ) -> None:
        self.strategy = strategy_factory()
        self.risk = risk
        self.state = RiskState(balance=initial_balance)
        self.logger = setup_logger("bot.backtest")

    def run(self, candles: List[Dict], output_path: Path) -> BacktestResult:
        df = pd.DataFrame(candles)
        equity = [self.state.balance]
        wins = 0
        losses = 0
        for i in range(200, len(df)):
            window = df.iloc[: i + 1]
            ctx = StrategyContext(pair="EURUSD", timeframe=900, candles=window)
            signal = self.strategy.should_enter(ctx)
            if signal == "HOLD" or not self.risk.can_trade(self.state):
                equity.append(self.state.balance)
                continue
            amount = self.risk.position_size(self.state)
            pnl = amount * 0.82 if signal == "CALL" else amount * -1
            self.risk.update_after_trade(self.state, pnl)
            if pnl >= 0:
                wins += 1
            else:
                losses += 1
            equity.append(self.state.balance)

        trades = wins + losses
        winrate = (wins / trades) if trades else 0.0
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(10, 4))
        plt.plot(equity, label="Equity")
        plt.title("Equity Curve")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        self.logger.info("backtest_complete", extra={"extra": {"trades": trades, "winrate": winrate}})
        return BacktestResult(
            trades=trades,
            wins=wins,
            losses=losses,
            winrate=winrate,
            equity_curve_path=output_path,
        )
