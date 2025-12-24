from __future__ import annotations

import pandas as pd

from app.bot.strategies.base import Strategy, StrategyContext


class EmaRsiFractalStrategy(Strategy):
    name = "ema_rsi_fractal"

    def prepare(self, ctx: StrategyContext) -> None:
        df = ctx.candles
        df["ema_25"] = df["close"].ewm(span=25, adjust=False).mean()
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=4).mean()
        avg_loss = loss.rolling(window=4).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        df["rsi_4"] = 100 - (100 / (1 + rs))
        df["support"] = df["low"].rolling(window=20).min()
        df["resistance"] = df["high"].rolling(window=20).max()
        ctx.candles = df

    def _fractal_bullish(self, df: pd.DataFrame) -> bool:
        if len(df) < 5:
            return False
        window = df.tail(5)
        middle = window.iloc[2]
        return middle["low"] == window["low"].min()

    def _fractal_bearish(self, df: pd.DataFrame) -> bool:
        if len(df) < 5:
            return False
        window = df.tail(5)
        middle = window.iloc[2]
        return middle["high"] == window["high"].max()

    def should_enter(self, ctx: StrategyContext) -> str:
        self.prepare(ctx)
        df = ctx.candles.dropna().copy()
        if len(df) < 30:
            return "HOLD"
        last = df.iloc[-1]
        trend_up = last["close"] >= last["ema_25"]
        trend_down = last["close"] <= last["ema_25"]
        support = last["support"]
        resistance = last["resistance"]
        price = last["close"]
        near_support = abs(price - support) / price < 0.002
        near_resistance = abs(price - resistance) / price < 0.002
        rsi = last["rsi_4"]

        if trend_up and rsi <= 20 and near_support and self._fractal_bullish(df):
            return "CALL"
        if trend_down and rsi >= 80 and near_resistance and self._fractal_bearish(df):
            return "PUT"
        return "HOLD"
