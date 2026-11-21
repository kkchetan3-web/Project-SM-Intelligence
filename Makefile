# Convenience targets. Every target is a thin wrapper around the CLI so that the
# documented commands and the ones people actually run cannot drift apart.
PYTHON ?= python
DATASET ?= synthetic_null
MARKET ?= kalyan

.PHONY: help install init synthetic validate analyse backtest cross predict report test lint clean

help:
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install:  ## install runtime + dev dependencies
	$(PYTHON) -m pip install -r requirements.txt && $(PYTHON) -m pip install -e . --no-deps

init:  ## create the per-market databases
	$(PYTHON) -m src.cli.main --dataset $(DATASET) init

synthetic:  ## regenerate the synthetic control world
	$(PYTHON) -m src.cli.main --dataset $(DATASET) synthetic --rebuild

validate:  ## run data-quality checks
	$(PYTHON) -m src.cli.main --dataset $(DATASET) validate

analyse:  ## run the 100-method suite for every market and target
	$(PYTHON) -m src.cli.main --dataset $(DATASET) analyse

backtest:  ## walk-forward backtest with baselines
	$(PYTHON) -m src.cli.main --dataset $(DATASET) backtest --market $(MARKET)

cross:  ## cross-market dependency analysis
	$(PYTHON) -m src.cli.main --dataset $(DATASET) cross-market

predict:  ## forecast the next draw for one market
	$(PYTHON) -m src.cli.main --dataset $(DATASET) predict --market $(MARKET) --target open

report:  ## build the Section 22 report
	$(PYTHON) -m src.cli.main --dataset $(DATASET) report

test:  ## run the test suite
	$(PYTHON) -m pytest -q

lint:  ## ruff
	ruff check src tests scripts

clean:  ## remove caches (never touches databases or raw data)
	find . -name '__pycache__' -type d -prune -exec rm -rf {} + ; rm -rf .pytest_cache .ruff_cache
