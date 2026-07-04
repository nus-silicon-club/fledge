#!/usr/bin/env bash
# One-command environment setup for new club members.
# Usage: ./infra/setup.sh
set -euo pipefail

cd "$(dirname "$0")"

echo "== Pulling the Fledge RTL + verification image (or building it locally) =="
docker compose pull fledge-dev || docker compose build fledge-dev

echo
echo "== Environment ready. To start a shell inside it: =="
echo "    cd infra && docker compose run --rm --pull never fledge-dev"
echo
echo "== Once inside the container, verify everything works: =="
echo "    cd hw/ip/example_counter/dv && make"
echo "You should see: TESTS=3 PASS=3 FAIL=0"
