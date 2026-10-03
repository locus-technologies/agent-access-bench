"""Task file format. One JSON object per line in tasks/<battery>.jsonl.

Every task is written and frozen before any arm-C run. Prompts are phrased the way a real
user would ask, with no vendor or tool names.
"""

from typing import Literal

from pydantic import BaseModel, Field

Battery = Literal["gtm", "paiddata", "structured", "multistep", "travel", "control", "spend", "pilot"]


class ExactGrader(BaseModel):
    type: Literal["exact"] = "exact"
    gold: list[str]  # any normalized match passes (case, whitespace, punctuation ignored)


class NumberGrader(BaseModel):
    type: Literal["number"] = "number"
    gold: float | None = None  # static gold, or None when a live capture supplies it
    capture: str | None = None  # name of a function in bench/truth.py, run within 10 min of the run
    capture_args: dict = Field(default_factory=dict)
    rel_tol: float = 0.0
    abs_tol: float = 0.0


class SetGrader(BaseModel):
    type: Literal["set"] = "set"
    gold: list[str] | None = None
    capture: str | None = None
    capture_args: dict = Field(default_factory=dict)
    min_recall: float = 1.0  # share of gold items that must appear in the answer
    max_extra: int | None = None  # wrong extra items allowed (None = not checked)


class PersonEmailGrader(BaseModel):
    type: Literal["person_email"] = "person_email"
    person_names: list[str]  # accepted spellings of the hand-verified right person
    email_domains: list[str]  # accepted work-email domains
    require_deliverable: bool = True  # ZeroBounce at grade time: valid passes; catch-all fails unless allow_catch_all
    allow_catch_all: bool = False


class ClaimsGrader(BaseModel):
    type: Literal["claims"] = "claims"
    claims: list[str]  # each independently checkable against the answer (and cited sources)
    pass_share: float = 0.8
    checks: list[dict] = Field(default_factory=list)  # optional deterministic per-claim checks


class FlightGrader(BaseModel):
    type: Literal["flight"] = "flight"
    origin: list[str]  # IATA codes accepted
    destination: list[str]
    date: str  # YYYY-MM-DD local departure
    nonstop: bool = False
    max_price_usd: float | None = None
    cheapest_within: float = 0.10  # within 10% of the cheapest valid offer any arm found in the window


class SpendGrader(BaseModel):
    type: Literal["spend"] = "spend"
    budget_usd: float
    outcome: ClaimsGrader | None = None  # secondary


Grader = ExactGrader | NumberGrader | SetGrader | PersonEmailGrader | ClaimsGrader | FlightGrader | SpendGrader


class Task(BaseModel):
    id: str  # <battery>-<nn>
    battery: Battery
    prompt: str
    grader: Grader = Field(discriminator="type")
    d_eligible: bool = False  # the direct-vendor arm can plausibly serve it
    harness_track: bool = False
    truth_sources: list[str]  # where the gold came from (URLs, filings, pages), for the audit
    truth_checked_on: str  # YYYY-MM-DD
    notes: str = ""
