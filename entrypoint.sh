#!/bin/bash
echo "Loading user service..."
aerich upgrade
uvicorn app.main:app --host 0.0.0.0 --port 8000
