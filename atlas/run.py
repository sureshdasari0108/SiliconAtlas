"""Run one atlas cell end to end.

    python -m atlas.run --study registry/S001_sunk_cost --runner mock --n 200 --seed 42 --out out/

At Stage 1 only the mock runner exists; the command demonstrates the full
pipeline (registry -> stimuli -> respondents -> metrics -> schema-valid card)
without making any empirical claim.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from . import analysis
from .cards import build_card
from .runners import get_runner

BANNER = "=" * 72


def load_study(study_dir: Path) -> dict:
    study = yaml.safe_load((study_dir / "study.yaml").read_text())
    study["_dir"] = study_dir
    return study


def render_stimulus(study: dict, condition: str) -> str:
    stim = study["stimulus"]
    template = (study["_dir"] / stim["template"]).read_text()
    return template.replace("{{TICKET_CLAUSE}}", stim["condition_clauses"][condition])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlas.run", description=__doc__)
    ap.add_argument("--study", required=True, type=Path, help="registry directory, e.g. registry/S001_sunk_cost")
    ap.add_argument("--runner", default="mock", choices=["mock", "live"])
    ap.add_argument("--n", type=int, default=200, help="simulated respondents per condition")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--out", type=Path, default=Path("out"))
    a = ap.parse_args(argv)

    study = load_study(a.study)
    runner = get_runner(a.runner, study, a.seed, a.temperature)
    cond_hi, cond_lo = study["design"]["conditions"]  # [expected-higher, expected-lower]

    print(BANNER)
    print(f"ATLAS {a.runner.upper()} RUN — {study['registry_id']} {study['short_name']}")
    if a.runner == "mock":
        print("MOCK MODE: synthetic seeded responses. Pipeline demonstration only —")
        print("this run has NO evidential value and its card cannot carry a grade.")
    print(BANNER)

    sums, raw = {}, {}
    for cond in (cond_hi, cond_lo):
        stimulus = render_stimulus(study, cond)
        responses = runner.sample(cond, a.n, stimulus)
        raw[cond] = responses
        sums[cond] = analysis.summarize(responses, tuple(study["design"]["dv_scale_range"]))
        s = sums[cond]
        print(f"{cond:>12}: n={s['n']}  mean={s['mean']:.2f}  sd={s['sd']:.2f}  hist={s['histogram']}")

    s1, s2 = sums[cond_hi], sums[cond_lo]
    d = analysis.cohen_d(s1["mean"], s1["sd"], s1["n"], s2["mean"], s2["sd"], s2["n"])
    ci = analysis.d_ci95(d, s1["n"], s2["n"])
    tt = analysis.pooled_t(s1["mean"], s1["sd"], s1["n"], s2["mean"], s2["sd"], s2["n"])

    hgt = study.get("human_ground_truth", {})
    comparison = {"status": "human ground truth not ingested"}
    if "effect_size_d_approx" in hgt:
        band_half = study.get("equivalence_band_halfwidth", 0.20)
        hd = hgt["effect_size_d_approx"]
        eq = analysis.equivalence_check(d, ci, (hd - band_half, hd + band_half))
        sil_pooled = analysis.pooled_sd(s1["sd"], s1["n"], s2["sd"], s2["n"])
        hum_pooled = analysis.pooled_sd(
            hgt["paid_condition"]["sd_approx"], 2, hgt["free_condition"]["sd_approx"], 2
        )
        comparison = {
            "sign_agreement": (d > 0) == (hd > 0),
            "human_d_approx": hd,
            "equivalence": eq,
            "sd_ratio_silicon_over_human_approx": round(analysis.sd_ratio(sil_pooled, hum_pooled), 2),
            "caveat": hgt.get("verification_status", "unknown"),
        }

    results = {
        "primary_matched_n": {
            cond_hi: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s1.items()},
            cond_lo: {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s2.items()},
            "effect_size_d": round(d, 3),
            "d_ci95": [round(ci[0], 3), round(ci[1], 3)],
            "test_statistic": f"t({tt['df']}) = {tt['t']:.2f}, p = {tt['p']:.2e}",
            "direction": f"{cond_hi} > {cond_lo}" if d > 0 else f"{cond_lo} >= {cond_hi}",
        },
        "comparison_to_human": comparison,
        "distributional_fidelity": {
            "status": "unavailable — human response distributions not yet ingested (Stage-2 milestone)"
        },
    }

    cfg = {
        "config_id": "cfgA",
        "temperature": a.temperature,
        "n_per_condition": a.n,
        "seed": a.seed,
        "stimulus_variant": {"id": study["stimulus"]["variant_id"], "type": "paraphrase_isomorph"},
    }
    card = build_card(study=study, runner=runner, cfg=cfg, results=results, run_mode=a.runner)

    a.out.mkdir(parents=True, exist_ok=True)
    out_path = a.out / f"{card['card_id']}.json"
    out_path.write_text(json.dumps(card, indent=2) + "\n")
    print(BANNER)
    print(f"d = {d:.2f}  CI95 {ci[0]:.2f}..{ci[1]:.2f}   {results['primary_matched_n']['test_statistic']}")
    print(f"card: {out_path}  (schema-valid; run_mode={card['run_mode']}; grade: {card['scores']['grade']})")
    print(BANNER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
