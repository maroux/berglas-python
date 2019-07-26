#!/usr/bin/env bash

set -ex

options="-v -s --strict --cov=berglas --cov-report html --cov-report term"

if [ -z "${target}" ]; then
    target="tests"
fi

options="${target} ${options}"

mypy berglas

python3 -bb -m pytest -p no:berglas ${options}

black --check .

flake8

pip install -e .
