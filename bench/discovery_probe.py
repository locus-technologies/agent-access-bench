"""Re-run the pre-registered 36-query tool-search eval (2026-09-07) against prod.

Discovery calls are free. Scores recall@1 and recall@5 on the dev and held-out
batteries, and reports match_quality / empty-reason on every query.
"""

import json
import os
import sys
import urllib.request

from bench.secrets import load_env_file

load_env_file()
BASE = "https://api.paywithlocus.com/api/credits"


def search(q: str) -> dict:
    req = urllib.request.Request(
        BASE + "/tools/search",
        data=json.dumps({"query": q, "limit": 5}).encode(),
        headers={"Authorization": "Bearer " + os.environ["LOCUS_PRO_API_KEY"], "content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main(out_path: str) -> None:
    spec = json.load(open("prereg/discovery/phrasing-eval-set.json"))
    rows = []
    for battery in ("dev", "heldout", "adjacent"):
        for item in spec.get(battery, []):
            res = search(item["q"])
            slugs = [r.get("slug") for r in res.get("results", [])]
            gold = set(item.get("gold", []))
            rows.append({
                "battery": battery, "q": item["q"], "gold": sorted(gold), "top5": slugs,
                "hit1": bool(slugs[:1] and slugs[0] in gold), "hit5": bool(gold & set(slugs)),
                "match_quality": [r.get("match_quality") for r in res.get("results", [])],
                "reason": res.get("reason"),
            })
    json.dump(rows, open(out_path, "w"), indent=1)
    for b in ("dev", "heldout", "adjacent"):
        rs = [r for r in rows if r["battery"] == b]
        if rs:
            print(f"{b:9s} n={len(rs):2d}  recall@1={sum(r['hit1'] for r in rs)}/{len(rs)}  recall@5={sum(r['hit5'] for r in rs)}/{len(rs)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/discovery-prod.json")
