#!/bin/bash

# Start the backend
uvicorn main:app --proxy-headers --host 0.0.0.0 --port 8808 &

# Start the frontend
cd /code/frontend && trunk serve --release --address 0.0.0.0 --port 8001

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
