"""Core matrix: one Inspect task per (arm, batteries). The model is chosen at eval time.

    uv run inspect eval bench/eval.py@access_bench -T arm=C -T batteries=pilot \
        --model anthropic/claude-sonnet-5-5 --epochs 1
"""

import json
from pathlib import Path

from inspect_ai import Epochs, Task, task
from inspect_ai.agent import react
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.solver import generate, system_message

from bench.arms import SYSTEM_PROMPT, tools_for
from bench.server_instructions import instructions_for
from bench.graders import task_scorer
from bench.secrets import load_secrets
from bench.task_schema import Task as BenchTask

load_secrets()

TASK_DIR = Path(__file__).resolve().parent.parent / "tasks"
MESSAGE_LIMIT = 30
TIME_LIMIT_S = 900


def load_tasks(batteries: list[str], d_only: bool = False, harness_only: bool = False) -> list[BenchTask]:
    tasks = []
    for b in batteries:
        for line in (TASK_DIR / f"{b}.jsonl").read_text().splitlines():
            if line.strip():
                t = BenchTask.model_validate_json(line)
                if (not d_only or t.d_eligible) and (not harness_only or t.harness_track):
                    tasks.append(t)
    return tasks


@task
def access_bench(arm: str = "B", batteries: str = "pilot", d_only: bool = False, epochs: int = 3) -> Task:
    tasks = load_tasks(batteries.split(","), d_only=d_only)
    dataset = MemoryDataset([
        Sample(id=t.id, input=t.prompt, metadata={"task": json.loads(t.model_dump_json()), "arm": arm})
        for t in tasks
    ])
    tools = tools_for(arm)
    # Each arm gets the official instructions of the servers it mounts, as MCP clients do.
    servers = {"C": ["locus-pro"], "D": ["apollo", "hunter", "firecrawl", "exa", "tavily", "prospeo"]}.get(arm, [])
    prompt = SYSTEM_PROMPT + instructions_for(servers)
    solver = (
        [system_message(SYSTEM_PROMPT), generate()]
        if arm == "A"
        else react(prompt=prompt, tools=tools)
    )
    return Task(
        dataset=dataset,
        solver=solver,
        scorer=task_scorer(),
        epochs=Epochs(epochs),
        message_limit=MESSAGE_LIMIT,
        time_limit=TIME_LIMIT_S,
        sandbox="docker" if arm != "A" else None,
        metadata={"arm": arm, "batteries": batteries},
    )
