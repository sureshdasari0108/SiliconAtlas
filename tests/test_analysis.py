"""Unit tests for atlas.analysis.

Fixture histograms are the synthetic S001 worked example
(docs/example_cell_card_annotated.json); every published number in that card
must recompute exactly from these histograms via this module.
"""
import math

import pytest

from atlas import analysis

PAID = [0, 0, 0, 2, 6, 18, 52, 78, 44]   # n=200
FREE = [0, 1, 2, 7, 22, 50, 72, 36, 10]  # n=200


def expand(hist):
    return [i + 1 for i, c in enumerate(hist) for _ in range(c)]


def test_summarize_matches_worked_example():
    p = analysis.summarize(expand(PAID))
    f = analysis.summarize(expand(FREE))
    assert p["n"] == f["n"] == 200
    assert p["histogram"] == PAID and f["histogram"] == FREE
    assert round(p["mean"], 2) == 7.65 and round(p["sd"], 2) == 1.07
    assert round(f["mean"], 2) == 6.64 and round(f["sd"], 2) == 1.24


def test_effect_size_ci_and_t_match_worked_example():
    p = analysis.summarize(expand(PAID))
    f = analysis.summarize(expand(FREE))
    d = analysis.cohen_d(p["mean"], p["sd"], p["n"], f["mean"], f["sd"], f["n"])
    assert round(d, 2) == 0.87
    lo, hi = analysis.d_ci95(d, p["n"], f["n"])
    assert round(lo, 2) == 0.66 and round(hi, 2) == 1.07
    tt = analysis.pooled_t(p["mean"], p["sd"], p["n"], f["mean"], f["sd"], f["n"])
    assert tt["df"] == 398
    assert round(tt["t"], 2) == 8.69
    assert tt["p"] < 1e-10


def test_equivalence_relation_above_band():
    # silicon d=0.87 CI [0.67, 1.08] vs human band 0.37 +/- 0.20 -> entirely above
    eq = analysis.equivalence_check(0.87, (0.66, 1.07), (0.17, 0.57))
    assert eq["relation"] == "above" and eq["passed"] is False


def test_wasserstein_properties():
    assert analysis.wasserstein_normalized(PAID, PAID) == 0.0
    base = [10, 20, 30, 40, 50, 30, 15, 5, 0]      # empty top bin
    shifted = [0] + base[:-1]                       # clean one-step shift up
    w = analysis.wasserstein_normalized(base, shifted)
    assert w == pytest.approx(1 / 8)                # one-step shift on a 9-point scale
    # symmetry and bounds
    assert analysis.wasserstein_normalized(PAID, FREE) == pytest.approx(
        analysis.wasserstein_normalized(FREE, PAID)
    )
    assert 0 <= analysis.wasserstein_normalized(PAID, FREE) <= 1


def test_input_validation():
    with pytest.raises(ValueError):
        analysis.summarize([1])
    with pytest.raises(ValueError):
        analysis.summarize([0, 5, 5])  # off-scale
    with pytest.raises(ValueError):
        analysis.wasserstein_normalized([1, 2], [1, 2, 3])


def test_pooled_sd_hand_value():
    sp = analysis.pooled_sd(1.07, 200, 1.24, 200)
    assert sp == pytest.approx(math.sqrt((1.07**2 + 1.24**2) / 2), rel=1e-9)
