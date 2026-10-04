#!/bin/zsh
# Full pre-registered run (prereg-v1). Every stream logs to logs/full/.
set -u
cd "$(dirname "$0")/.."
MODELS=$(uv run python -c "import json;print(','.join(m['id'] for m in json.load(open('prereg/models.json'))['models']))")
BATTERIES=gtm,paiddata,structured,multistep,travel,control
RUN_ID=full-$(date -u +%Y%m%dT%H%M%SZ)
echo "$RUN_ID" > logs/full/RUN_ID

# Deployed-commit watcher: one line per minute; any change marks a rerun window.
( while true; do
    c=$(curl -s -D - -o /dev/null https://api.paywithlocus.com/api/credits/balance -H "Authorization: Bearer $(grep ^LOCUS_PRO_API_KEY .env | cut -d= -f2)" | grep -i x-locus-commit | tr -d '\r' | awk '{print $2}')
    echo "$(date -u +%FT%TZ) ${c:-unknown}" >> logs/full/commit-watch.log
    sleep 60
  done ) &
WATCHER=$!

uv run python -m bench.run --arm A,B,C --batteries $BATTERIES --model $MODELS --epochs 3 \
  --log-dir logs/main --max-tasks 9 --max-samples 4 > logs/full/core.txt 2>&1 &
PIDS=($!)
uv run python -m bench.run --arm D --d-only --batteries $BATTERIES --model $MODELS --epochs 3 \
  --log-dir logs/main-d --max-tasks 3 --max-samples 4 > logs/full/arm-d.txt 2>&1 &
PIDS+=($!)
( for m in ${(s:,:)MODELS}; do
    uv run python -m bench.spend --arms B,C,D --model $m --epochs 3 --log-dir logs/spend --max-samples 2
  done ) > logs/full/spend.txt 2>&1 &
PIDS+=($!)
for hs in claude-code,codex gemini-cli,openclaw hermes,openai-agents; do
  uv run python -m bench.harness_track --harnesses $hs --arms B,C,C-mcp-only --epochs 3 \
    --batteries $BATTERIES --parallel 2 --run-id $RUN_ID-${hs//,/-} > logs/full/harness-${hs//,/-}.txt 2>&1 &
  PIDS+=($!)
done

for p in $PIDS; do wait $p; done
kill $WATCHER
echo "DONE $(date -u +%FT%TZ)" >> logs/full/commit-watch.log
