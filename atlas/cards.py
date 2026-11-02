"""Cell-card assembly and validation.

Integrity rule (enforced here AND structurally in schema/cell_card.schema.json):
only run_mode == "live" cards are evidential. Mock and synthetic-example cards
get transferability_score = null and an "N/A" grade, so nothing produced by this
prototype can be mistaken for evidence about silicon samples.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

HARNESS_VERSION = "0.1.0-stage1"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "cell_card.schema.json"

NON_ENDORSEMENT = (
    "An atlas grade is a statement about model behavior under this pinned configuration. "
    "It is not an endorsement of replacing human participants."
)


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text())


def validate_card(card: dict) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    v = Draft202012Validator(load_schema())
    return [f"{'/'.join(map(str, e.path)) or '<root>'}: {e.message}" for e in v.iter_errors(card)]


def grade_for_mode(run_mode: str) -> dict:
    if run_mode == "live":
        raise NotImplementedError(
            "Live grading requires the frozen pre-registration (prereg/) and is a Stage-2 milestone."
        )
    label = "mock demonstration" if run_mode == "mock" else "synthetic schema example"
    return {
        "evidential": False,
        "grade": f"N/A ({label}; no evidential value)",
        "transferability_score": None,
        "transferability_interval": None,
    }


def build_card(*, study: dict, runner, cfg: dict, results: dict, run_mode: str) -> dict:
    card_id = f"{study['registry_id']}__{runner.name}__{cfg['config_id']}"
    card = {
        "schema_version": "cell-card/0.4",
        "card_id": card_id,
        "run_mode": run_mode,
        "atlas_version": HARNESS_VERSION,
        "study": {
            "registry_id": study["registry_id"],
            "short_name": study["short_name"],
            "evidence_tier": study["evidence_tier"],
            "construct_domain": study["construct_domain"],
            "effect_type": study["effect_type"],
            "human_ground_truth": study.get("human_ground_truth", {}),
        },
        "configuration": {
            "model": {"name": runner.name, "weights_access": runner.weights_access},
            "decoding": {"temperature": cfg["temperature"]},
            "sample_sizes": {"matched_n_per_condition": cfg["n_per_condition"]},
            "seeds": {"base_seed": cfg["seed"], "policy": "base_seed_per_condition_stream"},
            "stimulus_variant": cfg.get("stimulus_variant", {}),
            "persona_scheme": {"id": "none_v1", "description": "no persona conditioning at Stage 1"},
        },
        "contamination": {"grade": None, "status": "probe battery designed (contamination/probes.md) but not yet run"},
        "results": results,
        "scores": {
            **grade_for_mode(run_mode),
            "admissible_uses": [],
            "inadmissible_uses": ["any evidential use whatsoever (non-live run)"],
        },
        "ethics": {"non_endorsement": NON_ENDORSEMENT},
        "provenance": {
            "harness_version": HARNESS_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "license": "CC-BY-4.0 (card); code MIT",
        },
    }
    errors = validate_card(card)
    if errors:
        raise RuntimeError("generated card failed schema validation:\n" + "\n".join(errors))
    return card
