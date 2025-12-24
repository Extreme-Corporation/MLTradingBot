from __future__ import annotations

import pandas as pd

from app.bot.strategies.base import Strategy, StrategyContext


class SmaConfluenceStrategy(Strategy):
    name = "sma_confluence"

    def prepare(self, ctx: StrategyContext) -> None:
        df = ctx.candles
        df["sma_20"] = df["close"].rolling(window=20).mean()
        df["sma_99"] = df["close"].rolling(window=99).mean()
        df["sma_200"] = df["close"].rolling(window=200).mean()
        ctx.candles = df

    def should_enter(self, ctx: StrategyContext) -> str:
        self.prepare(ctx)
        df = ctx.candles.dropna().copy()
        if len(df) < 200:
            return "HOLD"

        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = last["close"]
        sma20 = last["sma_20"]
        sma99 = last["sma_99"]
        sma200 = last["sma_200"]

        if abs(price - sma20) / price > 0.02:
            return "HOLD"

        distance_20_99 = abs(sma20 - sma99) / price
        distance_99_200 = abs(sma99 - sma200) / price
        if distance_20_99 > 0.01 or distance_99_200 > 0.01:
            return "HOLD"

        touched = abs(price - sma20) / price < 0.003
        if not touched:
            return "HOLD"

        volume_decreasing = True
        if "volume" in df.columns:
            volume_decreasing = df["volume"].iloc[-1] <= df["volume"].iloc[-2] <= df["volume"].iloc[-3]

        bullish_cross = prev["sma_20"] <= prev["sma_99"] and sma20 > sma99
        bearish_cross = prev["sma_20"] >= prev["sma_99"] and sma20 < sma99

        bullish_trend = sma20 >= sma99 >= sma200
        bearish_trend = sma20 <= sma99 <= sma200

        if bullish_cross and volume_decreasing:
            return "CALL"
        if bearish_cross and volume_decreasing:
            return "PUT"

        if bullish_trend and price <= sma20 and distance_20_99 < 0.005 and volume_decreasing:
            return "CALL"
        if bearish_trend and price >= sma20 and distance_20_99 < 0.005 and volume_decreasing:
            return "PUT"
        return "HOLD"
