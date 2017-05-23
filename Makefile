# simple makefile to simplify repetitive build env management tasks under posix

PYTHON := $(shell which python)
NOSETESTS := $(shell which nosetests)

all: clean inplace

clean-pyc:
	@find . -name "*.pyc" -exec rm {} \;

clean-so:
	@find pyjet -name "*.so" -exec rm {} \;

clean-build:
	@rm -rf build

clean: clean-build clean-pyc clean-so

in: inplace # just a shortcut
inplace:
	@$(PYTHON) setup.py build_ext -i

test: inplace
	@$(NOSETESTS) -s -v pyjet
