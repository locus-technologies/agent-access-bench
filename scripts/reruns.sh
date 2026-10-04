#!/bin/zsh
cd "$(dirname "$0")/.."
B=gtm,paiddata,structured,multistep,travel,control
uv run python - <<'PY' | while IFS='|' read -r m a ids ep; do
import json
for j in json.load(open("results/rerun-plan.json")):
    print(f'{j["model"]}|{j["arm"]}|{",".join(j["task_ids"])}|{j["epochs"]}')
PY
  extra=""; [ "$a" = "D" ] && extra="--d-only"
  uv run python -m bench.run --arm $a $extra --batteries $B --model $m --task-ids $ids --epochs $ep --log-dir logs/rerun --max-samples 3 --max-tasks 1 >> logs/full/reruns.txt 2>&1
  echo "done $m $a" >> logs/full/reruns.txt
done
echo RERUNS-DONE >> logs/full/reruns.txt
