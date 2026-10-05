"""Build the public trace bundle: copy the logs the analysis uses, with secrets and email
addresses removed.

    uv run python scripts/scrub_traces.py --out dist/traces

- Every secret value the benchmark loads (from .env and, if configured, AWS) is replaced with
  "[REDACTED]", along with anything shaped like a common API key or bearer token.
- Every email address keeps its domain and loses its local part ("•••@example.com"), as in
  the spot-check sample. Graders already logged only the domain and the ZeroBounce status.
- .eval files are zip archives of JSON; each member is rewritten and the archive rebuilt.
Nothing in a trace that the analysis reads (scores, usage, answers' numbers) is changed, so
`bench.analyze` on the bundle reproduces results/full.
"""

import argparse
import os
import re
from concurrent.futures import ProcessPoolExecutor
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench.secrets import KEYS, load_secrets  # noqa: E402
from inspect_ai._util import zipfile as _inspect_zip  # noqa: E402,F401  (adds zstd, which .eval files use)

LOG_DIRS = ["main", "main-a2", "main-bc", "main-gpro", "main-d", "main-d2", "main-d-gpro", "rerun", "spend"]
RAW = ["harness", "harness_traces", "spend-ledger.jsonl"]

# Mask the run of local-part characters before each "@" that starts a domain. A leading JSON
# escape (\n, \u00e9, ...) is kept intact so the JSON stays valid, and glued addresses
# ("a@x.comb@x.com") lose both local parts.
EMAIL = re.compile(r"(\\u[0-9a-fA-F]{4}|\\.)?[A-Za-z0-9._%+'-]+@(?=[A-Za-z0-9-]+\.[A-Za-z0-9.-]*[A-Za-z]{2,})")
KEY_SHAPES = re.compile(
    r"\b(?:lcr_(?:prod|stage|beta|test)_[A-Za-z0-9_-]{8,}|tvly-[A-Za-z0-9-]{12,}|sk-[A-Za-z0-9_-]{20,}"
    r"|AIza[0-9A-Za-z_-]{30,}|xai-[A-Za-z0-9]{20,}|claw_[A-Za-z0-9_-]{12,}|AKIA[0-9A-Z]{16})"
    r"|(?<=Bearer )[A-Za-z0-9._~+/=-]{16,}"
)
EXTRA_ENV = ["LOCUS_PRO_API_KEY", "LOCUS_PRO_ADMIN_KEY", "ZEROBOUNCE_API_KEY", "DATAFORSEO_CREDENTIALS",
             "GITHUB_TOKEN", "X_API_BEARER_TOKEN", "GEMINI_API_KEY"]


def secret_values() -> list[str]:
    load_secrets()
    names = set(KEYS.values()) | set(EXTRA_ENV)
    vals = {os.environ[n] for n in names if len(os.environ.get(n, "")) >= 12}
    for v in list(vals):  # credentials like "user:pass" also appear split or base64'd
        vals |= {p for p in v.split(":") if len(p) >= 12}
    return sorted(vals, key=len, reverse=True)


def scrub_text(s: str, secrets: list[str]) -> str:
    for v in secrets:
        if v in s:
            s = s.replace(v, "[REDACTED]")
    s = KEY_SHAPES.sub("[REDACTED]", s)
    return EMAIL.sub(lambda m: (m.group(1) or "") + "•••@", s)


def scrub_file(src: Path, dst: Path, secrets: list[str]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == ".eval":
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                data = scrub_text(data.decode("utf-8", "surrogateescape"), secrets).encode("utf-8", "surrogateescape")
                zout.writestr(item, data)
        return
    text = src.read_bytes().decode("utf-8", "surrogateescape")
    dst.write_bytes(scrub_text(text, secrets).encode("utf-8", "surrogateescape"))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out", default="dist/traces")
    a = p.parse_args()
    out = Path(a.out)
    secrets = secret_values()
    files = [f for d in LOG_DIRS for f in sorted(Path("logs", d).rglob("*")) if f.is_file()]
    for r in RAW:
        base = Path("results/raw", r)
        files += [base] if base.is_file() else [f for f in sorted(base.rglob("*")) if f.is_file()]
    with ProcessPoolExecutor() as pool:
        list(pool.map(scrub_file, files, [out / f for f in files], [secrets] * len(files), chunksize=4))
    # Self-check: no secret value survives anywhere in the bundle.
    leaks = []
    for f in out.rglob("*"):
        if not f.is_file():
            continue
        blobs = []
        if f.suffix == ".eval":
            with zipfile.ZipFile(f) as z:
                blobs = [z.read(n) for n in z.namelist()]
        else:
            blobs = [f.read_bytes()]
        for b in blobs:
            if any(v.encode() in b for v in secrets) or KEY_SHAPES.search(b.decode("utf-8", "ignore")):
                leaks.append(str(f))
                break
    print(f"wrote {len(files)} files to {out}; files with a surviving secret: {len(leaks)}")
    if leaks:
        print("\n".join(leaks[:20]))
        sys.exit(1)


if __name__ == "__main__":
    main()
