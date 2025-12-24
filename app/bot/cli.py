from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.bot.backtest.runner import BacktestRunner
from app.bot.brokers.iqoption_client import IQOptionClient, PaperBroker
from app.bot.config import load_config
from app.bot.core.engine import TradingEngine
from app.bot.core.logger import setup_logger
from app.bot.core.risk import RiskManager
from app.bot.strategies.ema_rsi_fractal import EmaRsiFractalStrategy
from app.bot.strategies.sma_confluence import SmaConfluenceStrategy


STRATEGIES = {
    EmaRsiFractalStrategy.name: EmaRsiFractalStrategy,
    SmaConfluenceStrategy.name: SmaConfluenceStrategy,
}

TIMEFRAMES = {
    "M1": 60,
    "M5": 300,
    "M15": 900,
    "M30": 1800,
    "H1": 3600,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IQ Option trading bot")
    parser.add_argument("--mode", choices=["paper", "real"], default=None)
    parser.add_argument("--market", choices=["binary", "digital", "both"], default=None)
    parser.add_argument("--pair", default=None)
    parser.add_argument("--timeframe", default=None)
    parser.add_argument("--expiry", type=int, default=None)
    parser.add_argument("--strategy", choices=STRATEGIES.keys(), default=None)
    parser.add_argument("--risk", choices=["flat", "massaniello", "martingale"], default=None)
    parser.add_argument("--min-payout", type=float, default=None)
    parser.add_argument("--max-open", type=int, default=None)
    parser.add_argument("--daily-stop", type=float, default=None)
    parser.add_argument("--backtest-csv", type=Path, default=None)
    parser.add_argument("--backtest-output", type=Path, default=Path("logs/equity_curve.png"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config()
    logger = setup_logger("bot.cli")

    mode = args.mode or cfg.bot.mode
    pair = args.pair or cfg.bot.pair
    timeframe_label = args.timeframe or cfg.bot.timeframe
    timeframe_seconds = TIMEFRAMES.get(timeframe_label, 900)
    expiry_minutes = args.expiry or cfg.bot.expiry_minutes
    expiry_seconds = expiry_minutes * 60
    strategy_name = args.strategy or EmaRsiFractalStrategy.name

    risk = RiskManager(
        stake_pct=cfg.bot.risk.stake_pct,
        preset=args.risk or cfg.bot.risk.preset,
        martingale_factor=cfg.bot.risk.martingale_factor,
        massaniello_steps=cfg.bot.risk.massaniello_steps,
        massaniello_target=cfg.bot.risk.massaniello_target,
        daily_stop_loss_pct=cfg.bot.risk.daily_stop_loss_pct,
        daily_stop_gain_pct=cfg.bot.risk.daily_stop_gain_pct,
    )

    strategy_factory = STRATEGIES[strategy_name]

    if args.backtest_csv:
        candles = []
        with args.backtest_csv.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip().startswith("timestamp"):
                    continue
                parts = line.strip().split(",")
                if len(parts) < 6:
                    continue
                candles.append(
                    {
                        "timestamp": int(parts[0]),
                        "open": float(parts[1]),
                        "close": float(parts[2]),
                        "high": float(parts[3]),
                        "low": float(parts[4]),
                        "volume": float(parts[5]),
                    }
                )
        runner = BacktestRunner(strategy_factory, risk, initial_balance=1000.0)
        result = runner.run(candles, args.backtest_output)
        logger.info(
            "backtest_finished",
            extra={"extra": {"trades": result.trades, "winrate": result.winrate}},
        )
        return

    if mode == "paper":
        broker = PaperBroker()
        fetch_candles = broker.get_candles
        place_order = broker.buy_digital
        check_order = broker.check_win
    else:
        email = os.getenv("IQOPTION_EMAIL", "")
        password = os.getenv("IQOPTION_PASSWORD", "")
        if not email or not password:
            raise RuntimeError("IQOPTION_EMAIL and IQOPTION_PASSWORD must be set")
        client = IQOptionClient(email, password, mode="PRACTICE")
        client.connect()
        fetch_candles = client.get_candles
        place_order = client.buy_digital
        check_order = client.check_win

    engine = TradingEngine(
        strategy_name=strategy_name,
        strategy_factory=strategy_factory,
        fetch_candles=fetch_candles,
        place_order=place_order,
        check_order=check_order,
        pair=pair,
        timeframe_seconds=timeframe_seconds,
        expiry_seconds=expiry_seconds,
        risk=risk,
        initial_balance=1000.0,
    )
    logger.info(
        "bot_started",
        extra={"extra": {"pair": pair, "timeframe": timeframe_label, "strategy": strategy_name}},
    )
    engine.loop(sleep_seconds=timeframe_seconds)


if __name__ == "__main__":
    main()
