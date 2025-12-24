from app.bot.core.engine import TradingEngine
from app.bot.core.risk import RiskManager
from app.bot.strategies.base import Strategy, StrategyContext


class AlwaysCallStrategy(Strategy):
    name = "always_call"

    def prepare(self, ctx: StrategyContext) -> None:
        return None

    def should_enter(self, ctx: StrategyContext) -> str:
        return "CALL"


def test_engine_places_order():
    def fetch_candles(pair: str, timeframe: int, amount: int):
        return [
            {
                "open": 1.0,
                "close": 1.0,
                "high": 1.0,
                "low": 1.0,
                "volume": 100,
            }
        ] * amount

    def place_order(pair: str, direction: str, amount: float, expiry: int) -> str:
        return "order-1"

    def check_order(order_id: str) -> float:
        return 1.0

    risk = RiskManager(
        stake_pct=0.02,
        preset="flat",
        martingale_factor=2.0,
        massaniello_steps=0,
        massaniello_target=0.0,
        daily_stop_loss_pct=-0.05,
        daily_stop_gain_pct=0.03,
    )

    engine = TradingEngine(
        strategy_name="always_call",
        strategy_factory=AlwaysCallStrategy,
        fetch_candles=fetch_candles,
        place_order=place_order,
        check_order=check_order,
        pair="EURUSD",
        timeframe_seconds=900,
        expiry_seconds=900,
        risk=risk,
        initial_balance=1000.0,
    )
    engine.run_once()
    assert engine.session.orders[0].order_id == "order-1"
