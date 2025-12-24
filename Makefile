PYTHON ?= python

up:
	@echo "Use docker-compose if disponível."

bot:
	$(PYTHON) -m app.bot --mode paper --strategy ema_rsi_fractal

web:
	cd app/web && npm install && npm run dev

api:
	$(PYTHON) -m uvicorn app.api.main:app --reload

test:
	pytest
