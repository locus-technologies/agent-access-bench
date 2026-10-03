"""Phase 0 spike: one Inspect ReAct agent, Locus Pro MCP over HTTP, one task."""

import os

from inspect_ai import Task, eval, task
from inspect_ai.agent import react
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.tool import mcp_server_http

from bench.secrets import load_secrets

load_secrets()


@task
def spike() -> Task:
    locus = mcp_server_http(
        name="locus-pro",
        url=os.environ["LOCUS_PRO_MCP_URL"],
        headers={"Authorization": "Bearer " + os.environ["LOCUS_PRO_API_KEY"]},
    )
    return Task(
        dataset=[Sample(
            input="What is the domain name of the company Stripe's main website? Use your tools to confirm it, then answer with just the domain.",
            target="stripe.com",
        )],
        solver=react(tools=[locus]),
        scorer=includes(),
        message_limit=30,
    )


if __name__ == "__main__":
    eval(spike(), model="anthropic/claude-sonnet-5-5", log_dir="logs/spike")
