.PHONY: setup lint typecheck test

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e .

lint:
	ruff check src tests

format:
	ruff check src tests --fix
	black src tests

typecheck:
	mypy src tests

test:
	pytest