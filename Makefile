# simple makefile to simplify repetitive build env management tasks under posix

PYTHON := $(shell which python)
CYTHON := $(shell which cython)
NOSETESTS := $(shell which pytest)

CYTHON_PYX := pyjet/src/_libpyjet.pyx
CYTHON_CPP := $(CYTHON_PYX:.pyx=.cpp)

all: clean inplace

clean-pyc:
	@find . -name "*.pyc" -exec rm {} \;

clean-so:
	@find pyjet -name "*.so" -exec rm {} \;

clean-build:
	@rm -rf build

clean: clean-build clean-pyc clean-so

.SECONDEXPANSION:
%.cpp: %.pyx $$(filter-out $$@,$$(wildcard $$(@D)/*))
	@echo "compiling $< ..."
	$(CYTHON) -a --cplus --fast-fail --line-directives $<

cython: $(CYTHON_CPP)

clean-cython:
	@rm -f $(CYTHON_CPP)

in: inplace # just a shortcut
inplace:
	@$(PYTHON) setup.py build_ext -i

test: inplace
	@$(NOSETESTS) -v pyjet

sdist: clean
	@$(PYTHON) setup.py sdist

valgrind: inplace
	valgrind --log-file=valgrind.log --tool=memcheck --leak-check=full \
		 --suppressions=etc/valgrind-python.supp $(NOSETESTS) -s -v pyjet
