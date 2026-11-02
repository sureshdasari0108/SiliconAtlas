# Before you push / submit (Stage 1)

1. Set real authors: LICENSE copyright line, CITATION.cff, README license note.
2. `git init && git add -A && git commit -m "Stage-1 prototype: schemas, mock-mode harness, S001 registry entry"`
   (history then carries YOUR identity, not a tool's).
3. Push to a public repository; put the URL into the proposal where [URL] appears.
4. Run and confirm locally: `pip install -r requirements.txt && make test && make demo && make validate`.
5. Verify Klein et al. (2014) numbers; update registry/S001_sunk_cost/study.yaml
   and flip verification_status to "verified" only after checking the paper.
6. Add your AI-assistance disclosure per journal policy (this repository and the
   proposal were drafted with AI assistance).
7. ManuscriptCentral (mc.manuscriptcentral.com/orgsci): upload proposal (3-5 pp),
   technical appendix, and this repository URL as the research artifact.
