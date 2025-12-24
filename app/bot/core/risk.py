from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class RiskState:
    balance: float
    wins: int = 0
    losses: int = 0
    consecutive_losses: int = 0
    daily_pnl: float = 0.0


class RiskManager:
    def __init__(
        self,
        stake_pct: float,
        preset: str,
        martingale_factor: float,
        massaniello_steps: int,
        massaniello_target: float,
        daily_stop_loss_pct: float,
        daily_stop_gain_pct: float,
    ) -> None:
        self.stake_pct = stake_pct
        self.preset = preset
        self.martingale_factor = martingale_factor
        self.massaniello_steps = massaniello_steps
        self.massaniello_target = massaniello_target
        self.daily_stop_loss_pct = daily_stop_loss_pct
        self.daily_stop_gain_pct = daily_stop_gain_pct
        self.massaniello_schedule = self._build_massaniello_schedule()

    def _build_massaniello_schedule(self) -> List[float]:
        if self.massaniello_steps <= 0:
            return []
        target_per_step = self.massaniello_target / self.massaniello_steps
        return [target_per_step for _ in range(self.massaniello_steps)]

    def can_trade(self, state: RiskState) -> bool:
        if state.consecutive_losses >= 3:
            return False
        stop_loss_value = state.balance * self.daily_stop_loss_pct
        stop_gain_value = state.balance * self.daily_stop_gain_pct
        if state.daily_pnl <= stop_loss_value:
            return False
        if state.daily_pnl >= stop_gain_value:
            return False
        return True

    def position_size(self, state: RiskState) -> float:
        base = max(1.0, state.balance * self.stake_pct)
        if self.preset == "martingale" and state.consecutive_losses > 0:
            return base * (self.martingale_factor ** state.consecutive_losses)
        if self.preset == "massaniello":
            step = min(state.wins + state.losses, len(self.massaniello_schedule) - 1)
            if step >= 0:
                return max(1.0, state.balance * self.massaniello_schedule[step])
        return base

    def update_after_trade(self, state: RiskState, pnl: float) -> None:
        state.daily_pnl += pnl
        if pnl >= 0:
            state.wins += 1
            state.consecutive_losses = 0
        else:
            state.losses += 1
            state.consecutive_losses += 1
        state.balance += pnl
