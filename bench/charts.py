"""Publication charts (article + social) from an analysis directory.

    uv run python -m bench.charts results/core --out deliverables/charts
    uv run python -m bench.charts results/pilot-analysis --out deliverables/charts-pilot --titles titles.json

Reads <results_dir>/summary.json (and runs.csv when present) written by bench.analyze, plus
the tool-definition token file, the spend ledger and the harness-track JSONL files. Writes
PNGs at 2x (2400 px wide) and a 1200x675 social crop of the headline chart.

Every chart renders from whatever arms, models and harnesses are present and is skipped
(with the reason printed) only when it has no data at all.

Titles are data-driven placeholders. Override any text with --titles, a JSON file:

    {"source": "Source: ...",
     "01-success-by-arm": {"title": "...", "subtitle": "...", "xlabel": "...", "ylabel": "...", "note": "..."},
     "names": {"openai/gpt-6.1-sol": "GPT-6.1 Sol"}}

Harness track (chart 02): bench.analyze does not cover it, so this module computes the paired
task-level difference per harness (epochs averaged within task first) and its 95% CI with the
same clustered bootstrap analyze.py uses (bench.analyze.bootstrap_contrast, same seed).
Batteries are the H1 access set (structured split at task 12, as in analyze.py).
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import textwrap
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from bench.analyze import H1_BATTERIES, battery_of, bootstrap_contrast, load_ledger  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HARNESS_GLOB = str(ROOT / "results" / "raw" / "harness" / "full-*.jsonl")
DEFAULT_TOOL_TOKENS = ROOT / "results" / "tool-definition-tokens.json"
DEFAULT_LEDGER = ROOT / "results" / "raw" / "spend-ledger.jsonl"

# --- style: monochrome + one accent (Locus brand: white surface = violet) ----------------
SURFACE = "#FFFFFF"
INK = "#111114"
INK_2 = "#52525B"   # secondary text
MUTED = "#8A8A93"   # axis ticks, source line
GRID = "#E7E7EA"
BASELINE = "#C4C4CA"
ACCENT = "#6D28D9"
# Arm marks. C is the accent; the other arms step through grays (validated: adjacent
# separation and >= 3:1 contrast on white pass; they fail the categorical chroma check by
# design, since they are emphasis grays). Marker shape is the secondary encoding.
ARM_COLOR = {"A": "#8E8E96", "B": "#2B2B30", "C": ACCENT, "D": "#5E5E66", "C-mcp-only": "#8E8E96"}
ARM_MARKER = {"A": "o", "B": "s", "C": "D", "D": "^", "C-mcp-only": "o"}
ARM_LABEL = {"A": "No tools", "B": "Web search only", "C": "+ Locus Pro", "D": "+ 7 vendors wired directly",
             "C-mcp-only": "+ Locus MCP server only"}
ARM_ORDER = ("A", "B", "C", "D")
STOCK_GRAY = "#D4D4D8"
VENDOR_GRAYS = ("#3F3F46", "#71717A")

BATTERY_LABEL = {"gtm": "Contact research", "paiddata": "Paid data", "multistep": "Multi-step research",
                 "travel": "Flights", "structured-hostile": "Bot-hostile pages", "structured-public": "Public data APIs",
                 "control": "Control", "pilot": "Pilot", "spend": "Spend"}
HARNESS_LABEL = {"claude-code": "Claude Code", "codex": "Codex CLI", "gemini-cli": "Gemini CLI",
                 "openclaw": "OpenClaw", "hermes": "Hermes", "openai-agents": "OpenAI Agents SDK"}
VENDOR_LABEL = {"apollo": "Apollo", "hunter": "Hunter", "prospeo": "Prospeo", "firecrawl": "Firecrawl",
                "exa": "Exa", "tavily": "Tavily", "e2b_run_code": "E2B", "e2b": "E2B"}

W_IN = 8.0          # 8 in at 150 dpi = 1200 px logical; saved at 300 dpi = 2400 px (2x)
DPI_LOGICAL = 150
DPI_SAVE = 300
SIDE_IN = 0.4


def _pick_font() -> list[str]:
    have = {f.name for f in font_manager.fontManager.ttflist}
    return [n for n in ("Inter", "SF Pro Text", "Helvetica Neue", "Helvetica", "Arial") if n in have] + ["DejaVu Sans"]


plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": _pick_font(), "font.size": 13,
    "axes.edgecolor": BASELINE, "axes.linewidth": 1.0, "axes.labelcolor": INK_2, "axes.labelsize": 13,
    "axes.facecolor": SURFACE, "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK_2, "ytick.labelcolor": INK_2,
    "xtick.labelsize": 12.5, "ytick.labelsize": 12.5, "axes.grid": False, "legend.frameon": False,
    "legend.fontsize": 12, "lines.solid_capstyle": "round",
})


# --- text helpers ---------------------------------------------------------------------------


def short_model(model: str, names: dict) -> str:
    if model in names:
        return names[model]
    toks = model.split("/")[-1].split("-")
    out: list[str] = []
    for t in toks:
        if out and t.isdigit() and out[-1][-1].isdigit():
            out[-1] += "." + t  # claude-sonnet-5-5 -> 5.5
        elif t.lower() == "gpt":
            out.append("GPT")
        else:
            out.append(t if any(c.isdigit() for c in t) else t.capitalize())
    s = " ".join(out)
    return s.replace("GPT ", "GPT-")


def pp(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:+.0f}"


def wrap(s: str, width_in: float, size: float) -> str:
    chars = max(20, int(width_in * 72 / (size * 0.52)))
    return "\n".join(textwrap.wrap(s, chars)) if s else s


# --- layout: fixed bands, axes fitted between them -------------------------------------------


def new_fig(h_in: float, w_in: float = W_IN):
    fig = plt.figure(figsize=(w_in, h_in), dpi=DPI_LOGICAL)
    ax = fig.add_axes((0.1, 0.1, 0.8, 0.8))
    return fig, ax


def style_axes(ax, grid_axis: str = "x") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left" if grid_axis == "x" else "bottom"].set_visible(grid_axis != "x")
    ax.grid(True, axis=grid_axis, color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(length=0, pad=6)


def finish(fig, ax, text: dict, source: str, plot_h: float | None = None) -> None:
    """Lay out one chart. Title, subtitle and legend stack top-left; note and source sit
    bottom-left; the axes (with tick labels) fill the box between them.

    plot_h (inches): the figure height is grown or shrunk so the plot area gets this much
    height. None keeps the figure size exactly (used for the fixed 1200x675 social crop).
    Re-entrant: calling it again replaces the text it placed before."""
    for art in getattr(fig, "_chart_artists", []):
        art.remove()
    W = fig.get_size_inches()[0]
    width = W - 2 * SIDE_IN
    t = fig.text(0, 0, wrap(text.get("title", ""), width, 19), fontsize=19, fontweight="bold",
                 color=INK, va="top", ha="left", linespacing=1.15)
    sub = fig.text(0, 0, wrap(text.get("subtitle", ""), width, 12.5), fontsize=12.5, color=INK_2,
                   va="top", ha="left", linespacing=1.3)
    foot = "\n".join(x for x in (wrap(text.get("note", ""), width, 10.5), source) if x)
    f = fig.text(0, 0, foot, fontsize=10.5, color=MUTED, va="bottom", ha="left", linespacing=1.35)
    arts = [t, sub, f]
    handles, ncol = getattr(fig, "_legend_spec", (None, None))
    leg = None
    if handles:
        r = fig.canvas.get_renderer()
        for n in sorted({ncol or len(handles), 2, 1}, reverse=True):
            leg = fig.legend(handles=handles, loc="upper left", ncol=n, handletextpad=0.4, columnspacing=1.6,
                             borderaxespad=0, borderpad=0, labelcolor=INK_2, frameon=False)
            if leg.get_window_extent(r).width <= width * fig.dpi or n == 1:
                break
            leg.remove()
        arts.append(leg)
    fig._chart_artists = arts
    if text.get("xlabel") is not None:
        ax.set_xlabel(text["xlabel"])
    if text.get("ylabel") is not None:
        ax.set_ylabel(text["ylabel"])

    px = fig.dpi
    for _ in range(8):
        H = fig.get_size_inches()[1]
        Hp = H * px
        t.set_position((SIDE_IN / W, 1 - 0.3 / H))
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        y = t.get_window_extent(r).y0
        if text.get("subtitle"):
            sub.set_position((SIDE_IN / W, (y - 0.1 * px) / Hp))
            fig.canvas.draw()
            y = sub.get_window_extent(r).y0
        if leg is not None:
            leg.set_bbox_to_anchor((SIDE_IN / W, (y - 0.2 * px) / Hp), transform=fig.transFigure)
            fig.canvas.draw()
            y = leg.get_window_extent(r).y0
        top_px = y - 0.18 * px
        f.set_position((SIDE_IN / W, 0.22 / H))
        fig.canvas.draw()
        bot_px = f.get_window_extent(r).y1 + 0.25 * px
        pos, tight = ax.get_window_extent(r), ax.get_tightbbox(r)
        l_pad, r_pad = pos.x0 - tight.x0, tight.x1 - pos.x1
        b_pad, t_pad = pos.y0 - tight.y0, tight.y1 - pos.y1
        if plot_h is not None:
            need = (Hp - top_px) + t_pad + plot_h * px + b_pad + bot_px
            if abs(need - Hp) > 1:
                fig.set_size_inches(W, need / px)
                continue
        x0, y0 = SIDE_IN * px + l_pad, bot_px + b_pad
        x1, y1 = W * px - SIDE_IN * px - r_pad, top_px - t_pad
        ax.set_position((x0 / (W * px), y0 / Hp, max(1, x1 - x0) / (W * px), max(1, y1 - y0) / Hp))
        if plot_h is None or abs((y1 - y0) - plot_h * px) <= 2:
            fig.canvas.draw()
            pos, tight = ax.get_window_extent(r), ax.get_tightbbox(r)
            if abs((pos.x0 - tight.x0) - l_pad) <= 1 and abs((tight.x1 - pos.x1) - r_pad) <= 1:
                break
    # one last pass at the final size so tick-label changes from resizing are absorbed
    fig.canvas.draw()


def save(fig, path: Path, dpi: int = DPI_SAVE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path


def place_labels(ax, labels: list[tuple]) -> None:
    """Greedy direct labels: each (x, y, text, color) takes the first candidate offset whose box
    clears the labels already placed and every marker. Falls back to the first candidate."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    marks = [ax.transData.transform((x, y)) for x, y, _, _ in labels]
    for line in ax.get_lines():
        marks += [ax.transData.transform(xy) for xy in line.get_xydata()]
    placed = []
    cands = [((8, 6), "left"), ((8, -16), "left"), ((-8, 6), "right"), ((-8, -16), "right"), ((0, 12), "center"), ((0, -22), "center")]
    for x, y, txt, col in labels:
        chosen = None
        for off, ha in cands:
            a = ax.annotate(txt, (x, y), xytext=off, textcoords="offset points", ha=ha, fontsize=10.5, color=col,
                            annotation_clip=False)
            bb = a.get_window_extent(r).expanded(1.05, 1.15)
            hit = any(bb.overlaps(p) for p in placed) or any(
                bb.x0 - 6 < mx < bb.x1 + 6 and bb.y0 - 6 < my < bb.y1 + 6 for mx, my in marks)
            if not hit:
                chosen = (a, bb)
                break
            a.remove()
        if chosen is None:
            (off, ha) = cands[0]
            a = ax.annotate(txt, (x, y), xytext=off, textcoords="offset points", ha=ha, fontsize=10.5, color=col)
            chosen = (a, a.get_window_extent(r))
        placed.append(chosen[1])


def set_diff_xlim(ax, vals: list) -> None:
    """Difference axis: always shows 0, spans the data (CIs included) plus room for end labels."""
    vals = [v for v in vals if v is not None] + [0.0]
    lo, hi = min(vals), max(vals)
    span = max(hi - lo, 0.2)
    ax.set_xlim(max(-1.0, lo - 0.08 * span), min(1.0, hi + 0.08 * span) + 0.12 * span)


def ci_err(est: float, lo: float | None, hi: float | None) -> list[list[float]]:
    lo = est if lo is None else lo
    hi = est if hi is None else hi
    return [[max(0.0, est - lo)], [max(0.0, hi - est)]]


def legend_top(ax, handles, ncol: int | None = None) -> None:
    """Register the legend; finish() places it under the subtitle, left-aligned with the title,
    and drops to fewer columns if it would overflow the width."""
    ax.figure._legend_spec = (handles, ncol)


def arm_handle(arm: str, hollow: bool = False) -> Line2D:
    c = ARM_COLOR[arm]
    return Line2D([], [], marker=ARM_MARKER[arm], linestyle="", markersize=8, markerfacecolor=SURFACE if hollow else c,
                  markeredgecolor=c, markeredgewidth=1.6, label=ARM_LABEL[arm])


def dot_ci(ax, x, y, lo, hi, arm: str, horizontal: bool = True, size: float = 8, hollow: bool = False) -> None:
    c = ARM_COLOR[arm]
    if horizontal:
        ax.errorbar(x, y, xerr=ci_err(x, lo, hi), fmt="none", ecolor=c, elinewidth=2, capsize=0, alpha=0.55, zorder=2)
    else:
        ax.errorbar(x, y, yerr=ci_err(y, lo, hi), fmt="none", ecolor=c, elinewidth=2, capsize=0, alpha=0.55, zorder=2)
    ax.plot([x], [y], marker=ARM_MARKER[arm], markersize=size, markerfacecolor=SURFACE if hollow else c,
            markeredgecolor=SURFACE if not hollow else c, markeredgewidth=2 if not hollow else 1.6, linestyle="", zorder=3)


# --- data loading -----------------------------------------------------------------------------


class Data:
    def __init__(self, results_dir: Path, a: argparse.Namespace, overrides: dict):
        self.dir = results_dir
        self.s = json.loads((results_dir / "summary.json").read_text())
        self.runs = []
        if (results_dir / "runs.csv").exists():
            with (results_dir / "runs.csv").open() as f:
                self.runs = list(csv.DictReader(f))
        inputs = self.s.get("inputs", {})
        self.tool_tokens_path = self._resolve(a.tool_tokens or inputs.get("tool_definition_tokens"), DEFAULT_TOOL_TOKENS)
        self.ledger_path = self._resolve(a.ledger or inputs.get("ledger"), DEFAULT_LEDGER)
        self.harness_files = sorted(glob.glob(a.harness_glob))
        self.names = overrides.get("names", {})
        self.pilot = bool(self.s.get("settings", {}).get("include_pilot"))

    @staticmethod
    def _resolve(p: str | None, default: Path) -> Path:
        if not p:
            return default
        path = Path(p)
        return path if path.is_absolute() else ROOT / path

    def epochs(self, scope_rows=None) -> int | None:
        rows = self.runs if scope_rows is None else scope_rows
        eps = {int(r["epoch"]) for r in rows if r.get("epoch")}
        return max(eps) if eps else None

    def h1_runs(self) -> list[dict]:
        bats = set(self.s.get("settings", {}).get("h1_batteries", H1_BATTERIES))
        return [r for r in self.runs if r.get("battery") in bats]

    def harness_rows(self) -> list[dict]:
        rows = []
        for f in self.harness_files:
            for line in Path(f).read_text().splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        return rows


def source_line(base: str | None, n_tasks: int | None, epochs: int | str | None, pilot: bool) -> str:
    """`epochs` is an int, or a string such as "up to 3" when runs per task vary."""
    if base:
        return base
    parts = ["Source: agent-access-bench, pre-registered"]
    if n_tasks:
        runs = "" if not epochs else f" × {epochs} run{'' if epochs == 1 else 's'}"
        parts.append(f"{n_tasks} tasks{runs}")
    s = ", ".join(parts)
    return s + ". PILOT DATA, not a headline result." if pilot else s


# --- 01 success by arm -------------------------------------------------------------------------


def chart_success(d: Data, ov: dict, src: str | None, social: bool = False):
    cells = [c for c in d.s.get("cells", {}).values() if c["scope"] == "h1" and c.get("success_rate") is not None]
    if not cells:
        return None, "no h1 cells in summary.json"
    by = defaultdict(dict)
    for c in cells:
        by[c["model"]][c["arm"]] = c
    arms = [a for a in ARM_ORDER if any(a in v for v in by.values())]
    models = sorted(by, key=lambda m: (-(by[m].get("B", {}).get("success_rate") or -1), m))
    n_rows = len(models)
    step = 1.0
    off = {a: (i - (len(arms) - 1) / 2) * min(0.18, 0.7 / max(1, len(arms))) for i, a in enumerate(arms)}
    if social:
        fig, ax = new_fig(4.5)
    else:
        fig, ax = new_fig(2.6 + 0.62 * n_rows * max(1, len(arms) / 2.5))
    style_axes(ax, "x")
    for i, m in enumerate(models):
        y = -i * step
        for a in arms:
            c = by[m].get(a)
            if not c:
                continue
            dot_ci(ax, c["success_rate"], y - off[a], c["wilson_low"], c["wilson_high"], a)
            if a == "C":
                ax.annotate(f"{100 * c['success_rate']:.0f}%", (c["wilson_high"] if c["wilson_high"] is not None else c["success_rate"], y - off[a]),
                            xytext=(6, 0), textcoords="offset points", va="center", fontsize=11.5, color=INK, fontweight="bold")
    ax.set_yticks([-i * step for i in range(n_rows)], [short_model(m, d.names) for m in models])
    ax.set_ylim(-(n_rows - 1) * step - 0.55, 0.55)
    ax.set_xlim(0, 1.06)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    legend_top(ax, [arm_handle(a) for a in arms], ncol=len(arms) if social or len(arms) <= 4 else 2)

    h1 = d.s.get("H1", {}).get("pooled", {})
    n_tasks = max(c["n_tasks"] for c in cells)
    title = (f"Locus Pro vs a stock agent: {pp(h1.get('estimate'))} points on access tasks"
             if h1.get("estimate") is not None else "Success rate by arm on access tasks")
    text = {"title": title,
            "subtitle": "Share of runs graded correct on the pre-registered access batteries, by model. "
                        "Models ordered by stock-agent success.",
            "xlabel": "Success rate", "ylabel": None,
            "note": "Whiskers: Wilson 95% CI over runs."} | ov
    if social:  # the crop keeps title, legend and source; subtitle and note only if overridden
        text = text | {k: ov.get(k, "") for k in ("subtitle", "note")}
    finish(fig, ax, text, source_line(src, n_tasks, d.epochs(d.h1_runs()), d.pilot),
           plot_h=None if social else n_rows * (0.24 * len(arms) + 0.3))
    return fig, None


# --- 02 gain by harness ---------------------------------------------------------------------------


def harness_contrasts(rows: list[dict], n_boot: int) -> tuple[list[dict], int, int | str | None]:
    acc: dict[tuple, list] = defaultdict(list)
    for r in rows:
        if r.get("score") is None:
            continue
        b = battery_of(r["task_id"], r["battery"])
        if b not in H1_BATTERIES:
            continue
        acc[(r["harness"], r["arm"], r["task_id"])].append(float(r["score"]))
    tm = {k: sum(v) / len(v) for k, v in acc.items()}
    harnesses = sorted({k[0] for k in tm})
    model_of = {r["harness"]: r.get("model", "") for r in rows}
    out, all_tasks = [], set()
    per_cell = {len(v) for v in acc.values()}
    epochs = (max(per_cell) if len(per_cell) == 1 else f"up to {max(per_cell)}") if per_cell else None
    for h in harnesses:
        tasks = sorted({t for (hh, _, t) in tm if hh == h})
        res = {"harness": h, "model": model_of.get(h, "")}
        for arm in ("C", "C-mcp-only"):
            D = np.array([[tm[(h, arm, t)] - tm[(h, "B", t)]] for t in tasks
                          if (h, arm, t) in tm and (h, "B", t) in tm]).reshape(-1, 1)
            if D.size:
                res[arm] = bootstrap_contrast(D, n_boot)
                all_tasks.update(t for t in tasks if (h, arm, t) in tm and (h, "B", t) in tm)
        if "C" in res or "C-mcp-only" in res:
            out.append(res)
    return out, len(all_tasks), epochs


def chart_harness(d: Data, ov: dict, src: str | None, n_boot: int):
    rows = d.harness_rows()
    if not rows:
        return None, "no harness-track files"
    res, n_tasks, epochs = harness_contrasts(rows, n_boot)
    if not res:
        return None, "no paired B/C harness runs on access batteries"
    res.sort(key=lambda r: -(r.get("C", {}).get("estimate") or -9))
    arms = [a for a in ("C", "C-mcp-only") if any(a in r for r in res)]
    off = {"C": -0.14, "C-mcp-only": 0.14} if len(arms) == 2 else {arms[0]: 0}
    fig, ax = new_fig(2.6 + 0.62 * len(res))
    style_axes(ax, "x")
    ax.axvline(0, color=BASELINE, linewidth=1.2, zorder=1)
    for i, r in enumerate(res):
        for a in arms:
            c = r.get(a)
            if not c or c["estimate"] is None:
                continue
            dot_ci(ax, c["estimate"], -i - off[a], c["ci_low"], c["ci_high"], a)
            if a == "C":
                ax.annotate(pp(c["estimate"]), (c["ci_high"], -i - off[a]), xytext=(6, 0), textcoords="offset points",
                            va="center", fontsize=11.5, color=INK, fontweight="bold")
    labels = [f"{HARNESS_LABEL.get(r['harness'], r['harness'])}, {short_model(r['model'], d.names)} (n={r.get('C', r.get('C-mcp-only'))['n_tasks']})"
              for r in res]
    ax.set_yticks([-i for i in range(len(res))], labels)
    ax.set_ylim(-len(res) + 0.45, 0.55)
    set_diff_xlim(ax, [v for r in res for a in arms if a in r for v in (r[a]["ci_low"], r[a]["ci_high"], r[a]["estimate"])])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{100 * v:+.0f}" if v else "0"))
    hs = [Line2D([], [], marker=ARM_MARKER[a], linestyle="", markersize=8, color=ARM_COLOR[a],
                 label="Locus Pro per the docs (MCP + skill) minus stock" if a == "C" else "Locus MCP only minus stock")
          for a in arms]
    legend_top(ax, hs, ncol=1)
    ests = [r["C"]["estimate"] for r in res if "C" in r]
    title = (f"Locus Pro changed success by {pp(min(ests))} to {pp(max(ests))} points across {len(ests)} agent harnesses"
             if ests else "Locus Pro gain over each harness's stock tools")
    text = {"title": title,
            "subtitle": "Paired difference in success rate versus the same harness with its built-in tools, access batteries.",
            "xlabel": "Difference in success rate (percentage points)", "ylabel": None,
            "note": "Whiskers: 95% CI, clustered bootstrap over tasks (10,000 resamples), computed in bench/charts.py. "
                    "Harness track, partial where runs are still in progress."} | ov
    finish(fig, ax, text, source_line(src, n_tasks, epochs, False), plot_h=0.62 * len(res))
    return fig, None


# --- 03 cost vs success -------------------------------------------------------------------------------


def chart_cost(d: Data, ov: dict, src: str | None):
    """Dumbbell per model: cost per successful task, web search only (B) -> + Locus Pro (C), on the
    access batteries, with the success gain printed at the right. Readable at phone width."""
    cells, cps = d.s.get("cells", {}), d.s.get("cost_per_success", {})
    by_model: dict[str, dict] = {}
    for k, c in cells.items():
        p = cps.get(k, {})
        if c["scope"] == "h1" and c["arm"] in ("B", "C") and p.get("estimate"):
            by_model.setdefault(c["model"], {})[c["arm"]] = (c, p)
    rows = [(m, v["B"], v["C"]) for m, v in by_model.items() if "B" in v and "C" in v]
    if not rows:
        return None, "no models with priced B and C cells"
    rows.sort(key=lambda r: r[2][1]["estimate"])
    fig, ax = new_fig(1.4 + 0.42 * len(rows))
    style_axes(ax, "x")
    ax.set_xscale("log")
    for i, (m, (cb, pb), (cc, pc)) in enumerate(rows):
        y = -i
        ax.plot([pb["estimate"], pc["estimate"]], [y, y], color=GRID, linewidth=3, zorder=1, solid_capstyle="round")
        for arm, p in (("B", pb), ("C", pc)):
            ax.plot([p["estimate"]], [y], marker=ARM_MARKER[arm], markersize=9, color=ARM_COLOR[arm],
                    markeredgecolor=SURFACE, markeredgewidth=2, linestyle="", zorder=3)
        gain = 100 * (cc["success_rate"] - cb["success_rate"])
        ax.annotate(f"{gain:+.0f} pts success", (1, y), xycoords=("axes fraction", "data"), xytext=(6, 0),
                    textcoords="offset points", va="center", ha="left", fontsize=10, color=INK_2, annotation_clip=False)
    ax.set_yticks([-i for i in range(len(rows))], [short_model(m, d.names) for m, _, _ in rows])
    ax.tick_params(axis="y", length=0)
    lo = min(min(r[1][1]["estimate"], r[2][1]["estimate"]) for r in rows)
    hi = max(max(r[1][1]["estimate"], r[2][1]["estimate"]) for r in rows)
    ax.set_xlim(lo / 1.5, hi * 1.5)
    ax.set_ylim(-len(rows) + 0.4, 0.6)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.2f}" if v < 1 else f"${v:,.0f}"))
    legend_top(ax, [arm_handle("B"), arm_handle("C")])
    n_tasks = max(r[1][0]["n_tasks"] for r in rows)
    text = {"title": "What each finished task costs, with and without Locus Pro",
            "subtitle": "Cost per successful task on data tasks: model tokens at list price plus Locus data fees.",
            "xlabel": "Cost per successful task (USD, log scale)", "ylabel": "",
            "note": "Point estimates; 95% intervals are in the results tables."} | ov
    finish(fig, ax, text, source_line(src, n_tasks, d.epochs(d.h1_runs()), d.pilot), plot_h=0.42 * len(rows))
    fig.subplots_adjust(right=0.80)
    return fig, None


# --- 04 tool-definition tokens ---------------------------------------------------------------------------


def chart_tokens(d: Data, ov: dict, src: str | None):
    if not d.tool_tokens_path.exists():
        return None, f"missing {d.tool_tokens_path}"
    tt = json.loads(d.tool_tokens_path.read_text())
    arms = [a for a in ("B", "C", "D") if a in tt.get("arms", {})]
    if not arms:
        return None, "no arms in tool-definition-tokens.json"
    fig, ax = new_fig(2.4 + 0.75 * len(arms))
    style_axes(ax, "x")
    totals = {a: tt["arms"][a]["total_tokens"] for a in arms}
    xmax = max(totals.values())
    ax.set_xlim(0, xmax * 1.22)
    h = 0.56
    segs_all = []  # (arm, label, x, w, colour, y)
    for i, a in enumerate(arms):
        info = tt["arms"][a]
        segs = [("Built-in tools", info.get("stock_tokens") or 0, STOCK_GRAY)]
        servers = sorted(info.get("servers", {}).items(), key=lambda kv: -kv[1].get("marginal_tokens", 0))
        for j, (name, sv) in enumerate(servers):
            col = ACCENT if "locus" in name else VENDOR_GRAYS[j % 2]
            segs.append(("Locus Pro" if "locus" in name else VENDOR_LABEL.get(name, name), sv.get("marginal_tokens", 0), col))
        x = 0
        for label, w, col in segs:
            if w > 0:
                ax.barh(-i, w, left=x, height=h, color=col, edgecolor=SURFACE, linewidth=1.5, zorder=2)
                segs_all.append((a, label, x, w, col, -i))
                x += w
        ax.text(x + xmax * 0.012, -i, f"{totals[a]:,}", va="center", ha="left", fontsize=11.5, color=INK, fontweight="bold")
    ax.set_yticks([-i for i in range(len(arms))], [ARM_LABEL[a] for a in arms])
    ax.set_ylim(-len(arms) + 0.4, 0.6)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:.0f}k" if v else "0"))
    if "C" in totals and "D" in totals and "B" in totals:
        title = (f"Locus Pro adds {totals['C'] - totals['B']:,} tool-definition tokens per request; "
                 f"wiring vendors directly adds {totals['D'] - totals['B']:,}")
    else:
        title = "Tool-definition tokens sent with every request"
    text = {"title": title,
            "subtitle": "Tokens the tool list occupies in the model's context on every request, by arm and server.",
            "xlabel": "Tool-definition tokens per request", "ylabel": None,
            "note": f"Measured with count_tokens on {tt.get('model', 'the reference model')}: "
                    "tokens with the arm's tools minus tokens without tools."} | ov
    source = src or "Source: agent-access-bench, pre-registered"
    finish(fig, ax, text, source, plot_h=0.62 * len(arms))
    # Segment labels go in only once the axes have their final width, and only where they fit.
    r = fig.canvas.get_renderer()
    unlabeled: dict[str, list] = defaultdict(list)
    for a, label, x, w, col, y in segs_all:
        t = ax.text(x + w / 2, y, label, ha="center", va="center", fontsize=10.5,
                    color=INK if col == STOCK_GRAY else SURFACE, zorder=3)
        seg_px = ax.transData.transform((x + w, y))[0] - ax.transData.transform((x, y))[0]
        if t.get_window_extent(r).width + 10 > seg_px:
            t.remove()
            if label not in ("Built-in tools", "Locus Pro"):
                unlabeled[a].append(label)
    if unlabeled.get("D") and "note" not in ov:
        text["note"] = f"Smaller D segments, left to right: {', '.join(unlabeled['D'])}. " + text["note"]
        finish(fig, ax, text, source, plot_h=0.62 * len(arms))
    return fig, None


# --- 05 spend vs budget ---------------------------------------------------------------------------


def chart_spend(d: Data, ov: dict, src: str | None):
    by_task: dict[str, dict] = defaultdict(lambda: {"budget": None, "C": [], "D": []})
    c_from_ledger = False
    for rec in load_ledger(d.ledger_path):
        t = str(rec.get("task_id", ""))
        if t.startswith("spend-") and rec.get("spent_usd") is not None and rec.get("arm") == "C":
            by_task[t]["budget"] = float(rec["budget_usd"])
            by_task[t]["C"].append(float(rec["spent_usd"]))
            c_from_ledger = True
    for v in d.s.get("H4", {}).get("from_logs", {}).values():
        if v["arm"] not in ("C", "D") or (v["arm"] == "C" and c_from_ledger):
            continue
        for run in v["runs"]:
            by_task[run["task"]]["budget"] = float(run["budget_usd"])
            by_task[run["task"]][v["arm"]].append(float(run["spent_usd"]))
    tasks = sorted(t for t, v in by_task.items() if v["budget"] is not None and (v["C"] or v["D"]))
    if not tasks:
        return None, "no spend-battery runs in ledger or summary"
    arms = [a for a in ("C", "D") if any(by_task[t][a] for t in tasks)]
    off = {"C": -0.13, "D": 0.13} if len(arms) == 2 else {arms[0]: 0.0}
    fig, ax = new_fig(5.2)
    style_axes(ax, "y")
    ax.spines["bottom"].set_visible(True)
    n_runs, breaches = 0, 0
    for i, t in enumerate(tasks):
        v = by_task[t]
        ax.hlines(v["budget"], i - 0.38, i + 0.38, color=INK, linewidth=2.5, zorder=2)
        for a in arms:
            vals = v[a]
            k = len(vals)
            xs = i + off[a] + (np.arange(k) - (k - 1) / 2) * min(0.05, 0.22 / max(1, k))
            ax.plot(xs, vals, marker=ARM_MARKER[a], linestyle="", markersize=8,
                    markerfacecolor=ARM_COLOR[a] if a == "C" else SURFACE, markeredgecolor=ARM_COLOR[a] if a == "D" else SURFACE,
                    markeredgewidth=1.6 if a == "D" else 1.5, zorder=3, alpha=0.9, clip_on=False)
            if a == "C":
                n_runs += k
                breaches += sum(x > v["budget"] + 1e-9 for x in vals)
    ax.set_xticks(range(len(tasks)), [t.replace("spend-", "Task ") for t in tasks])
    top = max([by_task[t]["budget"] for t in tasks] + [x for t in tasks for a in arms for x in by_task[t][a]])
    ax.set_ylim(0, top * 1.12)
    ax.set_xlim(-0.6, len(tasks) - 0.4)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:,.2f}"))
    hs = [Line2D([], [], color=INK, linewidth=2.5, label="Budget")]
    if "C" in arms:
        hs.append(Line2D([], [], marker=ARM_MARKER["C"], linestyle="", markersize=8, color=ACCENT,
                         label="+ Locus Pro, funded with exactly the budget"))
    if "D" in arms:
        hs.append(arm_handle("D", hollow=True))
        hs[-1].set_label("+ 7 vendors wired directly (estimated)")
    legend_top(ax, hs, ncol=len(hs) if len(hs) <= 2 else 2)
    title = (f"Capped Locus Pro runs stayed within budget in {n_runs - breaches} of {n_runs} runs"
             if "C" in arms else "Spend against budget on the spend-safety tasks")
    text = {"title": title,
            "subtitle": "Each mark is one run. Each Locus run gets its own sub-account funded with exactly the task budget.",
            "xlabel": None, "ylabel": "Spend per run (USD)",
            "note": " ".join(x for x in (
                "C spend of record is the Locus ledger (allocated minus settled balance), all models pooled."
                if c_from_ledger else "", "D spend is estimated from vendor usage at list prices." if "D" in arms else "") if x)} | ov
    finish(fig, ax, text, source_line(src, len(tasks), None, d.pilot and not c_from_ledger), plot_h=3.0)
    return fig, None


# --- 06 by battery ---------------------------------------------------------------------------------


def chart_battery(d: Data, ov: dict, src: str | None):
    s = d.s
    rows = []  # (label, contrast, group)
    h1 = s.get("H1", {})
    if h1.get("pooled", {}).get("estimate") is not None:
        rows.append(("All data tasks", h1["pooled"], "h1-pooled"))
    for b, c in h1.get("per_battery", {}).items():
        if c.get("estimate") is not None:
            rows.append((BATTERY_LABEL.get(b, b), c, "h1"))
    sp = s.get("structured_public", {}).get("pooled", {})
    if sp.get("estimate") is not None:
        rows.append(("Public data APIs", sp, "other"))
    h2 = s.get("H2", {}).get("pooled", {})
    if h2.get("estimate") is not None:
        rows.append(("Search is enough (control)", h2, "other"))
    if not rows:
        return None, "no C-B contrasts in summary.json"
    ys, y = [], 0.0
    prev = None
    for _, _, g in rows:
        if prev is not None and g != prev and not (prev == "h1-pooled" and g == "h1"):
            y -= 0.6  # gap before the separately reported group
        elif prev == "h1-pooled":
            y -= 0.3
        ys.append(y)
        y -= 1
        prev = g
    fig, ax = new_fig(2.4 + 0.55 * len(rows))
    style_axes(ax, "x")
    ax.axvline(0, color=BASELINE, linewidth=1.2, zorder=1)
    for (label, c, g), yy in zip(rows, ys):
        arm = "C" if g.startswith("h1") else "A"
        dot_ci(ax, c["estimate"], yy, c["ci_low"], c["ci_high"], arm, size=10 if g == "h1-pooled" else 8)
        ax.annotate(pp(c["estimate"]), (c["ci_high"] if c["ci_high"] is not None else c["estimate"], yy), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=11.5, color=INK,
                    fontweight="bold" if g == "h1-pooled" else "normal")
    ax.set_yticks(ys, [f"{lab} (n={c['n_tasks']})" for lab, c, _ in rows])
    for tl, (_, _, g) in zip(ax.get_yticklabels(), rows):
        if g == "h1-pooled":
            tl.set_fontweight("bold")
            tl.set_color(INK)
    ax.set_ylim(min(ys) - 0.55, 0.55)
    set_diff_xlim(ax, [v for _, c, _ in rows for v in (c["ci_low"], c["ci_high"], c["estimate"])])
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{100 * v:+.0f}" if v else "0"))
    hs = [Line2D([], [], marker="D", linestyle="", markersize=8, color=ACCENT, label="Tasks that need data")]
    if any(g == "other" for _, _, g in rows):
        hs.append(Line2D([], [], marker="o", linestyle="", markersize=8, color=ARM_COLOR["A"], label="Reported separately"))
    legend_top(ax, hs)
    n_tasks = max(c["n_tasks"] for _, c, _ in rows)
    text = {"title": "Where Locus Pro helps: gain over a stock agent, by battery",
            "subtitle": "Difference in success rate, C minus B, models weighted equally. "
                        "Control and public structured tasks are not part of H1.",
            "xlabel": "Difference in success rate (percentage points)", "ylabel": None,
            "note": "Whiskers: 95% CI, paired clustered bootstrap over tasks (10,000 resamples)."} | ov
    finish(fig, ax, text, source_line(src, n_tasks, d.epochs(), d.pilot), plot_h=0.45 * (abs(min(ys)) + 1))
    return fig, None


# --- main --------------------------------------------------------------------------------------------


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("results_dir", help="directory with summary.json (and runs.csv) from bench.analyze")
    p.add_argument("--out", required=True)
    p.add_argument("--titles", help="JSON with per-chart text overrides (see module doc)")
    p.add_argument("--harness-glob", default=DEFAULT_HARNESS_GLOB)
    p.add_argument("--tool-tokens", default=None)
    p.add_argument("--ledger", default=None)
    p.add_argument("--n-boot", type=int, default=10_000)
    a = p.parse_args()

    overrides = json.loads(Path(a.titles).read_text()) if a.titles else {}
    d = Data(Path(a.results_dir), a, overrides)
    out = Path(a.out)
    src = overrides.get("source")
    ov = lambda k: overrides.get(k, {})  # noqa: E731

    jobs = [
        ("01-success-by-arm", lambda: chart_success(d, ov("01-success-by-arm"), src)),
        ("02-gain-by-harness", lambda: chart_harness(d, ov("02-gain-by-harness"), src, a.n_boot)),
        ("03-cost-vs-success", lambda: chart_cost(d, ov("03-cost-vs-success"), src)),
        ("04-tool-definition-tokens", lambda: chart_tokens(d, ov("04-tool-definition-tokens"), src)),
        ("05-spend-vs-budget", lambda: chart_spend(d, ov("05-spend-vs-budget"), src)),
        ("06-by-battery", lambda: chart_battery(d, ov("06-by-battery"), src)),
    ]
    for name, fn in jobs:
        fig, why = fn()
        if fig is None:
            print(f"skipped {name}: {why}")
            continue
        print(f"wrote {save(fig, out / f'{name}.png')}")
        if name == "01-success-by-arm":
            soc = overrides.get("01-success-by-arm-social", ov("01-success-by-arm"))
            fig, _ = chart_success(d, soc, src, social=True)
            print(f"wrote {save(fig, out / f'{name}-social.png', dpi=DPI_LOGICAL)}  (1200x675)")


if __name__ == "__main__":
    main()
