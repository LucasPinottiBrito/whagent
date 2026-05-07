#!/usr/bin/env bash
set -euo pipefail

docker build -t whagent-backend:latest ./backend
docker build -t whagent-worker:latest ./workers
docker build -t whagent-frontend:latest ./frontend
docker build -t whagent-crm-mock:latest ./crm-mock
