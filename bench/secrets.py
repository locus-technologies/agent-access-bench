"""Load model and vendor keys into the process env.

Keys come from `.env` (see `.env.example`). Optionally, set BENCH_AWS_SECRET_ID (and
BENCH_AWS_REGION) to fill any key still missing from one AWS Secrets Manager JSON secret.
Only the fields listed in KEYS are copied from it; nothing is written to disk.
"""

import json
import os


KEYS = {
    # model providers
    "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY",
    "GEMINI_AI_API_KEY": "GOOGLE_API_KEY",
    "XAI_API_KEY": "XAI_API_KEY",
    "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
    "GROQ_API_KEY": "GROQ_API_KEY",
    "DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY",
    # vendors for the direct-wiring arm (D)
    "APOLLO_API_KEY": "APOLLO_API_KEY",
    "HUNTER_API_KEY": "HUNTER_API_KEY",
    "PROSPEO_API_KEY": "PROSPEO_API_KEY",
    "FIRECRAWL_API_KEY": "FIRECRAWL_API_KEY",
    "EXA_API_KEY": "EXA_API_KEY",
    "TAVILY_API_KEY": "TAVILY_API_KEY",
    "E2B_API_KEY": "E2B_API_KEY",
    # graders only (never given to agents)
    "ZEROBOUNCE_API_KEY": "ZEROBOUNCE_API_KEY",
    "DATAFORSEO_CREDENTIALS": "DATAFORSEO_CREDENTIALS",
    "X_API_BEARER_TOKEN": "X_API_BEARER_TOKEN",
    "DEEPGRAM_API_KEY": "DEEPGRAM_API_KEY",
}


def load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k, v)


def load_secrets() -> list[str]:
    """Populate os.environ; return the env names that were set."""
    load_env_file()
    secret_id = os.environ.get("BENCH_AWS_SECRET_ID")
    if not secret_id:
        return []
    import boto3

    region = os.environ.get("BENCH_AWS_REGION", "us-east-1")
    raw = boto3.client("secretsmanager", region_name=region).get_secret_value(SecretId=secret_id)
    config = json.loads(raw["SecretString"])
    loaded = []
    for src, dst in KEYS.items():
        if config.get(src) and not os.environ.get(dst):
            os.environ[dst] = config[src]
            loaded.append(dst)
    return loaded


if __name__ == "__main__":
    print("loaded:", " ".join(sorted(load_secrets())))
