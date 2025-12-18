#!/bin/bash
set -e
exec uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8001
