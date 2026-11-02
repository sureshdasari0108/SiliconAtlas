.PHONY: demo test validate clean

demo:
	python -m atlas.run --study registry/S001_sunk_cost --runner mock --n 200 --seed 42 --out out/

test:
	python -m pytest tests/ -q

validate:
	python -c "import json,sys; from atlas.cards import validate_card; \
p='docs/example_cell_card_annotated.json'; e=validate_card(json.load(open(p))); \
print(p, 'VALID' if not e else 'INVALID'); [print(' -',m) for m in e]; sys.exit(1 if e else 0)"
	@ls out/*.json >/dev/null 2>&1 && python -c "import json,glob,sys; from atlas.cards import validate_card; \
p=sorted(glob.glob('out/*.json'))[-1]; e=validate_card(json.load(open(p))); \
print(p, 'VALID' if not e else 'INVALID'); [print(' -',m) for m in e]; sys.exit(1 if e else 0)" || echo "no generated cards yet (run make demo)"

clean:
	rm -rf out/ .pytest_cache atlas/__pycache__ tests/__pycache__
