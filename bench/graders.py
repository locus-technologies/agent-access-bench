"""Graders. Deterministic checks first; a cross-family LLM judge only where a claims rubric is
unavoidable. Every scorer returns value 1 (pass) or 0 (fail) plus a JSON-able explanation."""

import json
import os
import re
import unicodedata

import httpx
from inspect_ai.model import ChatMessageUser, GenerateConfig, get_model
from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState

from bench import truth
from bench.task_schema import Task

# Judges are pinned. The judge is always from a different model family than the agent.
JUDGE_FOR_ANTHROPIC = "openai/gpt-5.5"
JUDGE_DEFAULT = "anthropic/claude-opus-5-5"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ZEROBOUNCE_URL = "https://api.zerobounce.net/v2/validate"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def contains(answer: str, phrase: str) -> bool:
    return f" {norm(phrase)} " in f" {norm(answer)} "


def numbers_in(answer: str) -> list[float]:
    out = []
    for m in re.finditer(r"-?\d[\d,]*\.?\d*", answer):
        try:
            out.append(float(m.group().replace(",", "")))
        except ValueError:
            pass
    return out


def judge_model_for(agent_model: str) -> str:
    return JUDGE_FOR_ANTHROPIC if agent_model.startswith("anthropic/") else JUDGE_DEFAULT


async def judge_claims(answer: str, claims: list[str], agent_model: str) -> list[bool]:
    prompt = (
        "You are grading an assistant's final answer against a fixed list of claims. For each "
        "claim, decide whether the ANSWER satisfies it. Be strict: a claim is satisfied only if "
        "the answer clearly states it or provides the required item. Do not use outside "
        "knowledge to fill gaps, but you may judge whether stated facts are consistent with the "
        "claim's wording.\n\n"
        f"ANSWER:\n{answer}\n\nCLAIMS:\n"
        + "\n".join(f"{i + 1}. {c}" for i, c in enumerate(claims))
        + '\n\nReply with JSON only: {"verdicts": [true|false, ...]} in claim order.'
    )
    model = get_model(judge_model_for(agent_model), config=GenerateConfig(temperature=0))
    out = await model.generate([ChatMessageUser(content=prompt)])
    match = re.search(r"\{.*\}", out.completion, re.S)
    verdicts = json.loads(match.group())["verdicts"] if match else []
    return [bool(v) for v in verdicts][: len(claims)] + [False] * max(0, len(claims) - len(verdicts))


async def zerobounce(email: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(ZEROBOUNCE_URL, params={"api_key": os.environ["ZEROBOUNCE_API_KEY"], "email": email})
    return resp.json().get("status", "unknown")


async def grade(task: Task, answer: str, agent_model: str) -> tuple[bool, dict]:
    g = task.grader
    if g.type == "exact":
        hit = next((x for x in g.gold if contains(answer, x)), None)
        return hit is not None, {"matched": hit}

    if g.type == "number":
        gold = g.gold if g.capture is None else getattr(truth, g.capture)(**g.capture_args)
        tol = max(g.abs_tol, abs(gold) * g.rel_tol)
        nums = numbers_in(answer)
        return any(abs(n - gold) <= tol for n in nums), {"gold": gold, "tol": tol, "found": nums[:20]}

    if g.type == "set":
        gold = g.gold if g.capture is None else getattr(truth, g.capture)(**g.capture_args)
        hits = [x for x in gold if contains(answer, x)]
        recall = len(hits) / len(gold) if gold else 0.0
        return recall >= g.min_recall, {"gold": gold, "hits": hits, "recall": recall}

    if g.type == "person_email":
        person = next((n for n in g.person_names if contains(answer, n)), None)
        emails = [e for e in EMAIL_RE.findall(answer) if e.split("@")[1].lower() in {d.lower() for d in g.email_domains}]
        statuses = {}
        for e in emails[:3]:
            statuses[e.split("@")[1]] = statuses.get(e.split("@")[1]) or []
            statuses[e.split("@")[1]].append(await zerobounce(e) if g.require_deliverable else "skipped")
        ok_status = {"valid"} | ({"catch-all"} if g.allow_catch_all else set())
        email_ok = any(s in ok_status or s == "skipped" for ss in statuses.values() for s in ss)
        # Only domains and verifier statuses are logged, never the address itself.
        return bool(person) and email_ok, {"person": person, "email_statuses_by_domain": statuses}

    if g.type == "claims":
        verdicts = await judge_claims(answer, g.claims, agent_model)
        share = sum(verdicts) / len(verdicts)
        return share >= g.pass_share, {"verdicts": verdicts, "share": share}

    if g.type == "flight":
        # Constraint checks here; "cheapest within X% of the best offer any arm found in the
        # same window" is applied in analysis, where all arms' offers are visible.
        verdicts = await judge_claims(
            answer,
            [
                f"Departs from one of {g.origin}",
                f"Arrives at one of {g.destination}",
                f"Departs on {g.date}",
                *(["The flight is nonstop"] if g.nonstop else []),
                "States a specific airline and flight number (or itinerary) and a total price",
                *([f"The stated total price is at most {g.max_price_usd} USD"] if g.max_price_usd else []),
            ],
            agent_model,
        )
        return all(verdicts), {"verdicts": verdicts, "price_candidates": numbers_in(answer)[:10]}

    if g.type == "spend":
        # Spend is scored from the trace in analysis (sum of usd_charged); this records outcome.
        if g.outcome:
            verdicts = await judge_claims(answer, g.outcome.claims, agent_model)
            return sum(verdicts) / len(verdicts) >= g.outcome.pass_share, {"verdicts": verdicts}
        return True, {}

    raise ValueError(f"unknown grader {g.type}")


@scorer(metrics=[accuracy(), stderr()])
def task_scorer():
    async def score(state: TaskState, target: Target) -> Score:
        task = Task.model_validate(state.metadata["task"])
        answer = state.output.completion or ""
        try:
            ok, detail = await grade(task, answer, str(state.model))
        except Exception as e:  # grader failure is recorded, never silently passed
            return Score(value=0, explanation=json.dumps({"grader_error": repr(e)[:300]}))
        return Score(value=1 if ok else 0, answer=answer[:2000], explanation=json.dumps(detail, default=str))

    return score
