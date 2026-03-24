.PHONY: install install-release build test test-compiled bench style clean

install:
	MYPYC_OPT_LEVEL=0 pip install -e ".[dev]"

install-release:
	MYPYC_OPT_LEVEL=3 pip install -e ".[dev]"

build:
	mypyc hash_utils/_core.py

test:
	pytest -v

test-compiled: build test

bench:
	python benchmarks/bench.py

style:
	ruff check --fix .
	ruff format .

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache
	rm -f hash_utils/*.so hash_utils/*.pyd
	find . -type d -name __pycache__ -exec rm -rf {} +
