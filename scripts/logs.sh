#!/usr/bin/env bash
set -euo pipefail

service_name="${1:-backend}"
docker service logs -f "whagent_${service_name}"
