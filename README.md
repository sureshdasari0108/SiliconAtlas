# The Silicon Sample Atlas — Stage-1 Prototype

Research artifact accompanying the proposal (Stage-2 development, Revision R1 of 2026-11-02; see CHANGELOG.md) *"The Silicon Sample Atlas: Mapping the
Boundary Conditions of LLM-Simulated Respondents in Organizational Research"*, submitted to the
*Organization Science* special issue **AI-Enabled Frontiers in Organizational Science**.

---

## Status — read this first

**This is a Stage-1 proof of concept of the *pipeline*, not of the *findings*.**

| Component | Status |
|---|---|
| Cell-card JSON Schema (`schema/cell_card.schema.json`) | **Real.** Validates every card in this repo; intended for CI. |
| Analysis code (`atlas/analysis.py`) | **Real.** Effect sizes, CIs, equivalence tests, distributional metrics; unit-tested (`make test`). |
| Harness + CLI (`atlas/run.py`) | **Real code, mock data.** Runs the full pipeline end to end using a seeded synthetic "mock model". |
| Registry entry S001 (`registry/S001_sunk_cost/`) | **Real schema, approximate ground truth.** Human statistics are flagged `approximate_pending_verification` against Klein et al. (2014). |
| Stimulus isomorph (`registry/.../isomorph_v2.txt`) | **Real, original text** authored for this project. The Many Labs original is *not* redistributed here (license check pending). |
| Example card (`docs/example_cell_card_annotated.json`) | **Synthetic schema illustration.** Internally consistent numbers; not from any model run. |
| Live model runs, pilot results, contamination probes, pre-registration | **Do not exist yet.** First live pilot cells are the first Stage-2 milestone. Metric definitions are a *draft* (`prereg/`), to be frozen on OSF before any live cell is scored. |

**No empirical claim about silicon samples is made at Stage 1.** As an integrity-by-design rule,
the scoring module refuses to emit a transferability grade for any non-live run: mock cards carry
`"grade": "N/A (mock demonstration; no evidential value)"`.

## Quickstart

```bash
pip install -r requirements.txt

# Run the full pipeline on S001 with the mock model (deterministic, seeded)
make demo          # = python -m atlas.run --study registry/S001_sunk_cost --runner mock --n 200 --seed 42 --out out/

# Unit tests for the statistics layer
make test

# Validate any card against the schema
make validate      # validates docs/example_cell_card_annotated.json and the freshly generated mock card
```

`make demo` executes: load registry entry -> render stimulus isomorph per condition -> simulate
respondents (mock runner) -> compute effect size, CI, pooled t, equivalence-band check, SD ratio,
distributional metrics where ground-truth distributions exist -> emit a schema-valid cell card to
`out/`, stamped `run_mode: "mock"`.

## Repository layout

```
schema/cell_card.schema.json      JSON Schema (draft 2020-12) for atlas cell cards
registry/S001_sunk_cost/          study.yaml + stimuli/ (isomorph only; see stimuli/NOTICE.md)
atlas/                            the harness: run.py (CLI), runners.py, analysis.py, cards.py
cards/                            real atlas cells will live here; EMPTY at Stage 1 by design
docs/example_cell_card_annotated.json   synthetic worked example documenting the schema
prereg/wp1_metrics_DRAFT.md       draft metric definitions and weights (to be frozen pre-scoring)
contamination/probes.md           design of the contamination probe battery (not yet run)
envs/snapshot_manifest.example.yaml     format for pinning model snapshots in live runs
tests/                            unit tests for atlas/analysis.py
```

## Roadmap (maps to proposal work packages)

- **GATE (by Feb 1, 2027)** — >=5 pre-registered live cells (>=2 model families, >=1
  post-cutoff study), OSF pre-registration frozen first. Until then `cards/` stays empty.
- **WP1** — live adapters (API + local open-weight), human ground-truth distributions,
  200-paper frame-feasibility screen, dual-axis (criterion x contamination) reporting,
  **Tier-0** post-cutoff findings with our own modest human replications.
- **WP2** — paraphrase / persona / temperature robustness sweeps; robustness intervals per cell.
- **WP3** — the two-stage standard with the selection-aware rule: silicon picks conditions,
  never the confirmatory estimate (see prereg §7).
- **WP4** — cross-cultural cells (contingent on the editor-required consolidation meeting).

## Ethics

An atlas grade is a statement about model behavior under a pinned configuration — never an
endorsement of replacing human participants. See the `ethics` block required in every cell card.

## License

Code: MIT (`LICENSE`). Data and cards: CC-BY-4.0. Authors: [team placeholder — set before pushing].
