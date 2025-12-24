from app.bot.core.risk import RiskManager, RiskState


def test_martingale_position_size_increases():
    risk = RiskManager(
        stake_pct=0.02,
        preset="martingale",
        martingale_factor=2.0,
        massaniello_steps=0,
        massaniello_target=0.0,
        daily_stop_loss_pct=-0.05,
        daily_stop_gain_pct=0.03,
    )
    state = RiskState(balance=1000.0)
    base = risk.position_size(state)
    state.consecutive_losses = 2
    doubled = risk.position_size(state)
    assert doubled == base * 4
