.PHONY: install build test test-compiled lint format clean

install:
	pip install -e ".[dev]"

build:
	mypyc hash_utils/_core.py

test:
	pytest -v

test-compiled: build test

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	rm -f hash_utils/*.so hash_utils/*.pyd
	find . -type d -name __pycache__ -exec rm -rf {} +
