from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import tomllib


@dataclass
class RiskConfig:
    preset: str
    stake_pct: float
    martingale_factor: float
    massaniello_steps: int
    massaniello_target: float
    daily_stop_loss_pct: float
    daily_stop_gain_pct: float


@dataclass
class BotConfig:
    mode: str
    market: str
    pair: str
    timeframe: str
    expiry_minutes: int
    min_payout: float
    max_open: int
    allow_otc: bool
    risk: RiskConfig


@dataclass
class ApiConfig:
    host: str
    port: int


@dataclass
class AppConfig:
    bot: BotConfig
    api: ApiConfig


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.toml"


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)
    risk = raw.get("risk", {})
    bot = raw.get("bot", {})
    api = raw.get("api", {})
    return AppConfig(
        bot=BotConfig(
            mode=bot.get("mode", "paper"),
            market=bot.get("market", "digital"),
            pair=bot.get("pair", "EURUSD"),
            timeframe=bot.get("timeframe", "M15"),
            expiry_minutes=int(bot.get("expiry_minutes", 15)),
            min_payout=float(bot.get("min_payout", 0.82)),
            max_open=int(bot.get("max_open", 1)),
            allow_otc=bool(bot.get("allow_otc", False)),
            risk=RiskConfig(
                preset=risk.get("preset", "flat"),
                stake_pct=float(risk.get("stake_pct", 0.02)),
                martingale_factor=float(risk.get("martingale_factor", 2.0)),
                massaniello_steps=int(risk.get("massaniello_steps", 12)),
                massaniello_target=float(risk.get("massaniello_target", 0.06)),
                daily_stop_loss_pct=float(risk.get("daily_stop_loss_pct", -0.05)),
                daily_stop_gain_pct=float(risk.get("daily_stop_gain_pct", 0.03)),
            ),
        ),
        api=ApiConfig(
            host=api.get("host", "0.0.0.0"),
            port=int(api.get("port", 8000)),
        ),
    )


def parse_pair_list(raw: str | None) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]
