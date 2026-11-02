"""Response generators.

MockRunner exists to prove the pipeline end to end. It is NOT a model: it draws
from a seeded, discretized normal distribution whose parameters live in the
study's `mock_demo_params` block and are explicitly arbitrary. Cards produced
with it are stamped run_mode="mock" and can never carry a transferability grade
(see atlas/cards.py).

Live adapters (API-served and local open-weight models) are the first Stage-2
milestone and intentionally do not exist yet.
"""
from __future__ import annotations

import random


class MockRunner:
    name = "mock-demo-runner"
    weights_access = "mock"

    def __init__(self, study: dict, seed: int, temperature: float = 0.7):
        params = study.get("mock_demo_params")
        if not params:
            raise ValueError("study.yaml lacks mock_demo_params; mock runs need them")
        self.params = params
        self.seed = seed
        self.temperature = temperature  # recorded for card provenance; mock ignores it
        lo, hi = study["design"]["dv_scale_range"]
        self.lo, self.hi = int(lo), int(hi)

    def sample(self, condition: str, n: int, stimulus_text: str) -> list[int]:
        # stimulus_text is accepted (and logged upstream) so the mock runner has
        # the same interface a live adapter will have; it does not influence output.
        p = self.params[condition]
        rng = random.Random(f"{self.seed}:{condition}")
        out = []
        for _ in range(n):
            x = round(rng.gauss(p["mean"], p["sd"]))
            out.append(min(self.hi, max(self.lo, x)))
        return out


class LiveRunnerStub:
    """Placeholder so the CLI surface is honest about what exists."""

    def __init__(self, *_, **__):
        raise NotImplementedError(
            "Live model adapters are a Stage-2 milestone and are not implemented. "
            "No live silicon-sample runs have been executed with this repository."
        )


def get_runner(kind: str, study: dict, seed: int, temperature: float):
    if kind == "mock":
        return MockRunner(study, seed, temperature)
    if kind == "live":
        return LiveRunnerStub()
    raise ValueError(f"unknown runner: {kind!r} (choose: mock, live)")
