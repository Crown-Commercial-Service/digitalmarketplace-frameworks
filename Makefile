SHELL := /bin/bash
VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)

virtualenv:
	[ -z $$VIRTUAL_ENV ] && [ ! -d venv ] && python3 -m venv venv || true

requirements-dev: virtualenv requirements-dev.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements-dev.txt

test: show-environment test-flake8 test-python

test-flake8: virtualenv
	${VIRTUALENV_ROOT}/bin/flake8 .

test-python: virtualenv
	${VIRTUALENV_ROOT}/bin/py.test ${PYTEST-ARGS}

show-environment:
	@echo "Environment variables in use:"
	@env | grep DM_ || true

.PHONY: virtualenv requirements-for-test test-flake8 test-python show-environment
