"""Load model and vendor keys from AWS Secrets Manager into the process env.

Keys are read at runtime and never written to disk. Only the fields listed in
KEYS are copied, so the rest of the prod config never enters the process.
"""

import json
import os

import boto3

SECRET_ID = "locus-wallet/prod/config"
REGION = "us-west-1"

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
    "DUFFEL_ACCESS_TOKEN": "DUFFEL_ACCESS_TOKEN",
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
    raw = boto3.client("secretsmanager", region_name=REGION).get_secret_value(SecretId=SECRET_ID)
    config = json.loads(raw["SecretString"])
    loaded = []
    for src, dst in KEYS.items():
        if config.get(src) and not os.environ.get(dst):
            os.environ[dst] = config[src]
            loaded.append(dst)
    return loaded


if __name__ == "__main__":
    print("loaded:", " ".join(sorted(load_secrets())))
