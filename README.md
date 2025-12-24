# MLTradingBot

Robô de trading educacional para IQ Option com execução em papel (paper) e integração via `iqoptionapi`, mais API e dashboard web.

> ⚠️ **Uso educacional apenas**. Não é garantia de lucro. Teste sempre em **conta demo** antes de operar em conta real.

## Estrutura do projeto

```
/app
  /bot
    /core        # engine, sessão, risco
    /strategies  # ema_rsi_fractal.py, sma_confluence.py
    /brokers     # iqoption_client.py
    /backtest    # runner, métricas
    /utils       # helpers
    config.toml
  /api           # FastAPI
  /web           # Next.js dashboard
/tests
```

## Requisitos

* Python 3.11+
* Node.js 18+ (para o dashboard)

## Instalação rápida

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

* Copie `.env.example` para `.env` e preencha as credenciais.
* Ajuste o `app/bot/config.toml` conforme o ativo/timeframe/risco desejado.

### Variáveis principais (config.toml)

* `mode`: `paper` ou `real`
* `pair`: `EURUSD` (padrão)
* `timeframe`: `M15`
* `expiry_minutes`: `15`
* `risk.preset`: `flat | massaniello | martingale`

## Execução do robô

```bash
python -m app.bot --mode paper --strategy sma_confluence --pair EURUSD --timeframe M15 --expiry 15
```

### Backtest

```bash
python -m app.bot --backtest-csv data/eurusd_m15.csv --backtest-output logs/equity_curve.png
```

## API (FastAPI)

```bash
python -m uvicorn app.api.main:app --reload
```

Endpoints disponíveis:

* `GET /health`
* `GET /config`
* `GET /sessions`
* `GET /orders`
* `GET /stats`

## Dashboard Web (Next.js)

```bash
cd app/web
npm install
npm run dev
```

## Estratégias

### `ema_rsi_fractal`
* Tendência pela EMA(25).
* RSI(4) zonas 80/20.
* Fractal(3) como confirmação.

### `sma_confluence` (IQ Option)
* SMA20, SMA99, SMA200.
* Opera toques no conjunto das médias (suporte/resistência).
* Filtros de distância e cruzamentos.

## Risco

* Stake padrão: 2% do saldo (mín. $1)
* Máximo 1 posição aberta
* Stop diário e stop por perdas consecutivas

## Testes

```bash
pytest
```

## Makefile

```bash
make bot
make api
make web
make test
```

## Roadmap

* Integração completa com IQ Option (sessões e sincronismo de payout).
* Dashboard em tempo real conectado à API.
* Estratégias adicionais (S/R, RSI multi-TF).

## Aviso legal

Este projeto é estritamente educacional. Operações em mercados financeiros envolvem riscos significativos.
