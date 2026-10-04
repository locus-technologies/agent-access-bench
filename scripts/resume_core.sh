#!/bin/zsh
set -u
cd "$(dirname "$0")/.."
( while true; do
    c=$(curl -s -D - -o /dev/null https://api.paywithlocus.com/api/credits/balance -H "Authorization: Bearer $(grep ^LOCUS_PRO_API_KEY .env | cut -d= -f2)" | grep -i x-locus-commit | tr -d '\r' | awk '{print $2}')
    echo "$(date -u +%FT%TZ) ${c:-unknown}" >> logs/full/commit-watch-core.log
    sleep 60
  done ) &
W=$!
uv run python -m bench.resume logs/main --max-tasks 9 --max-samples 4 > logs/full/core-resume.txt 2>&1 &
P1=$!
uv run python -m bench.resume logs/main-d --max-tasks 3 --max-samples 4 > logs/full/arm-d-resume.txt 2>&1 &
P2=$!
wait $P1; wait $P2; kill $W
echo "DONE $(date -u +%FT%TZ)" >> logs/full/commit-watch-core.log
