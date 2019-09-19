#!/usr/bin/env bash

pip install -r requirements/publish.txt

python setup.py sdist bdist_wheel

twine upload dist/*
