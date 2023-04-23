#!/usr/bin/env bash

export PYTHONPATH=$(pwd)/..
pytest test.py $1
