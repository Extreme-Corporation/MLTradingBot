import pandas as pd

from app.bot.strategies.base import StrategyContext
from app.bot.strategies.sma_confluence import SmaConfluenceStrategy


def test_sma_confluence_bullish_cross_call():
    closes = [1.0] * 199 + [1.0001]
    data = {
        "close": closes,
        "open": closes,
        "high": [c + 0.0002 for c in closes],
        "low": [c - 0.0002 for c in closes],
        "volume": [120] * 197 + [100, 90, 80],
    }
    df = pd.DataFrame(data)
    strategy = SmaConfluenceStrategy()
    ctx = StrategyContext(pair="EURUSD", timeframe=900, candles=df)
    signal = strategy.should_enter(ctx)
    assert signal == "CALL"
