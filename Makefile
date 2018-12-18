all: flake8 test

test:
	pytest

flake8:
	flake8
