# WP1 metric definitions — DRAFT (not frozen)

Status: draft for Stage-1 review. To be frozen on OSF, with timestamps, before
any live cell is scored. Until frozen, no card may carry a grade (enforced in
atlas/cards.py and schema/cell_card.schema.json).

Implementation of every metric: atlas/analysis.py (single source of truth,
unit-tested in tests/test_analysis.py).

1. Sign agreement — silicon effect direction matches human ground truth.
2. Magnitude equivalence — silicon d, with 95% CI (Hedges-Olkin SE), judged
   against a band of human d +/- h. Draft h = 0.20; frozen per stratum.
   "Within" requires the entire CI inside the band.
3. Distributional fidelity — normalized 1-Wasserstein distance between full
   silicon and human response distributions per condition (requires ingesting
   human distributions; Stage-2), plus pooled-SD ratio.
4. Robustness (WP2) — d range across prompt paraphrases, persona schemes, and
   temperatures; conclusion-stability classification.

Draft aggregation weights: sign .30, magnitude .30, distribution .25,
robustness .15. Grades: A / B / C / F tied to admissible uses. Tier-1 anchors
are scored against the multi-lab aggregate, never the single original.

---
## R1 additions (2026-11-02) — responding to the Stage-1 gate review

5. Inference framework for silicon statistics (gate cond. 3). The estimand of a
   silicon cell is the MODEL'S RESPONSE DISTRIBUTION under a pinned
   configuration (model snapshot, decoding, persona scheme, stimulus variant).
   Reported intervals quantify decoding and sampling variability around that
   distribution; they are NOT estimates of human population parameters, and no
   exchangeability between simulated and human respondents is assumed or
   implied. Every cell reports effective-dispersion diagnostics (SD ratio,
   distributional spread) alongside nominal n, because low decoding
   temperatures collapse variance and make nominal n overstate information.
   Frozen version will enumerate, per metric, exactly what the interval does
   and does not license.

6. Contamination x criterion dual-axis reporting and Tier 0 (gate cond. 2).
   Tier-1 anchors (strongest human ground truth) are by construction the most
   contaminated; post-cutoff studies (least contaminated) have the weakest
   human evidence. Every cell is therefore reported on a dual axis: criterion
   strength (Tier 0/1/2) x contamination grade (A-D). Tier 0 = post-cutoff
   findings paired with our own modest pre-registered human replications,
   providing cells that are simultaneously low-contamination and well-anchored.
   Tier-0 scope and replication power targets to be fixed in the frozen version.

7. Selection-aware two-stage rule for WP3 (gate cond. 4). Silicon outputs may
   inform WHICH conditions proceed to human confirmation, never the
   confirmatory estimate. Stage-two human studies are freshly pre-registered,
   powered without reference to silicon effect sizes, and reported with
   selection-aware adjusted estimates (winner's-curse correction) alongside
   naive ones. Silicon and human data are never pooled for inference.

8. Weight-sensitivity reporting (Editor E). Aggregation weights (draft .30
   sign / .30 magnitude / .25 distribution / .15 robustness) are provisional;
   every published grade is accompanied by its sensitivity band across a
   pre-registered neighborhood of weight vectors. A grade that flips within
   the neighborhood is reported as unstable.

9. Grade-caption standard (Editor D). Every cell card carries a mandated
   caption: grades describe MODEL TRANSFER UNDER A CONFIGURATION, never the
   quality or credibility of the underlying human finding. Enforced as a
   required ethics field at freeze.
