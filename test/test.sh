#!/usr/bin/env bash

PYTHONPATH=$(pwd)/..
export PYTHONPATH
pytest . "$1"
