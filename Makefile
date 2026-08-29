PY := .venv/bin/python

.PHONY: setup data analyze figure docs check-docs reference-run screenshots clean

setup:                ## create venv and install dependencies (uv)
	uv venv .venv --python 3.12
	uv pip install --python .venv -r requirements.txt

data:                 ## generate both datasets (randomised trial + 10 hospitals)
	$(PY) generate_imbrave150.py
	$(PY) generate_multihospital.py
	$(PY) harmonize_hospitals.py

analyze:              ## reproduce trial result + run PSM + TMLE
	$(PY) analyze_imbrave150.py
	$(PY) psm_imbrave150.py
	$(PY) tmle_demo.py

figure:               ## render the robustness multiverse figure
	$(PY) robustness_multiverse.py

docs:                 ## regenerate docs/PROMPTS.md and docs/FILE-TREE.md
	python3 scripts/extract_prompts.py
	python3 scripts/gen_file_tree.py

check-docs:           ## fail if the generated docs are stale (what CI runs)
	python3 scripts/extract_prompts.py --check
	python3 scripts/gen_file_tree.py --check

screenshots:          ## regenerate docs/img/ (needs Chrome; frames come from walk.cast)
	$(PY) scripts/make_screenshots.py

reference-run:        ## snapshot a finished live-demo run for others to diff against
	python3 scripts/make_reference_run.py

clean:                ## remove derived artifacts (keeps tracked inputs)
	rm -f _answer_key_pooled.csv imbrave150_pooled.csv \
	      robustness_multiverse_results.csv hospitals_10sites.zip
	rm -rf __pycache__
