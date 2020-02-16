#!/usr/bin/env bash

python setup.py sdist bdist_wheel

twine upload "dist/tmux_dash-$(cat version)-py3-none-any.whl"
