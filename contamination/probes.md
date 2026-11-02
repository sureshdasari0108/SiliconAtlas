# Contamination probe battery — design (not yet run)

Purpose: grade every cell for training-data contamination before its results
are interpreted. Three levels are distinguished:

1. Stimulus memorization — verbatim-recall probes against the original text
   and against the isomorph actually used; match-score threshold set in the
   frozen pre-registration.
2. Finding-level knowledge — direct elicitation: does the model state the
   effect and predict its direction when asked about the paradigm?
3. Construct-level priors — paraphrased conceptual probes.

Grades: A (none detected) / B (construct-level only) / C (finding-level
knowledge; stimulus memorization mitigated by isomorph) / D (stimulus
memorization affecting the scored run). Tier-1 textbook effects are expected
to grade C; C-graded cells cannot support magnitude claims. A cutoff-based
natural experiment (pre- vs post-training-cutoff studies) complements probes
where applicable.

Status: DESIGN ONLY. No probes have been executed at Stage 1.
