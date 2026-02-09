all: format lint test

format:
	uv run ruff format *.py

lint:
	uv run ruff check *.py

test:
	uv run pytest
