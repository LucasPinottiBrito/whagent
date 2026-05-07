#!/usr/bin/env bash
set -euo pipefail

docker stack deploy -c docker-stack.yml whagent --resolve-image never
