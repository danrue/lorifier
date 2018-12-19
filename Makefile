all: black flake8 test

black:
	black *.py

flake8:
	flake8

test:
	pytest
