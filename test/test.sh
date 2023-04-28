#!/usr/bin/env bash

export PYTHONPATH=$(pwd)/..
pytest . $1
