"""Statistics layer for the Silicon Sample Atlas.

Every metric emitted into a cell card is computed here, and only here, so the
definitions in prereg/wp1_metrics_DRAFT.md have exactly one implementation.
Unit tests: tests/test_analysis.py.
"""
from __future__ import annotations

import math
from typing import Sequence

from scipy import stats as _sps


# ---------- summaries ----------

def summarize(responses: Sequence[int], scale: tuple[int, int] = (1, 9)) -> dict:
    """n, mean, sample SD (ddof=1), and a full response histogram over the scale."""
    lo, hi = scale
    n = len(responses)
    if n < 2:
        raise ValueError("need at least 2 responses")
    mean = sum(responses) / n
    var = sum((x - mean) ** 2 for x in responses) / (n - 1)
    hist = [0] * (hi - lo + 1)
    for x in responses:
        if not (lo <= x <= hi):
            raise ValueError(f"response {x} outside scale {scale}")
        hist[int(x) - lo] += 1
    return {"n": n, "mean": mean, "sd": math.sqrt(var), "histogram": hist, "scale": [lo, hi]}


# ---------- effect size ----------

def pooled_sd(s1: float, n1: int, s2: float, n2: int) -> float:
    return math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))


def cohen_d(m1: float, s1: float, n1: int, m2: float, s2: float, n2: int) -> float:
    """Cohen's d with pooled SD; positive when group 1 > group 2."""
    return (m1 - m2) / pooled_sd(s1, n1, s2, n2)


def d_ci95(d: float, n1: int, n2: int) -> tuple[float, float]:
    """Approximate 95% CI for d (Hedges & Olkin large-sample SE)."""
    se = math.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return (d - 1.96 * se, d + 1.96 * se)


def pooled_t(m1: float, s1: float, n1: int, m2: float, s2: float, n2: int) -> dict:
    """Student's two-sample t with pooled variance (matches cell-card reporting)."""
    sp = pooled_sd(s1, n1, s2, n2)
    t = (m1 - m2) / (sp * math.sqrt(1 / n1 + 1 / n2))
    df = n1 + n2 - 2
    p = 2 * _sps.t.sf(abs(t), df)
    return {"t": t, "df": df, "p": p}


# ---------- distributional metrics ----------

def wasserstein_normalized(hist_a: Sequence[int], hist_b: Sequence[int]) -> float:
    """1-Wasserstein distance between two histograms on the same ordinal scale,
    normalized to [0, 1] by the scale range. For unit-spaced bins this is the
    mean absolute difference of the two CDFs over the first k-1 support points,
    divided by (k-1)."""
    if len(hist_a) != len(hist_b):
        raise ValueError("histograms must share support")
    k = len(hist_a)
    na, nb = sum(hist_a), sum(hist_b)
    if na == 0 or nb == 0:
        raise ValueError("empty histogram")
    ca = cb = 0.0
    acc = 0.0
    for i in range(k - 1):  # CDF at the last support point is 1 for both
        ca += hist_a[i] / na
        cb += hist_b[i] / nb
        acc += abs(ca - cb)
    return acc / (k - 1)


def sd_ratio(silicon_pooled: float, human_pooled: float) -> float:
    return silicon_pooled / human_pooled


# ---------- equivalence ----------

def equivalence_check(d_silicon: float, ci: tuple[float, float], band: tuple[float, float]) -> dict:
    """Position of the silicon estimate relative to a pre-registered band around
    the human effect. 'within' requires the whole CI inside the band."""
    lo, hi = ci
    blo, bhi = band
    if lo >= blo and hi <= bhi:
        relation = "within"
    elif lo > bhi:
        relation = "above"
    elif hi < blo:
        relation = "below"
    else:
        relation = "overlapping"
    return {"band": [blo, bhi], "ci": [lo, hi], "relation": relation, "passed": relation == "within"}
