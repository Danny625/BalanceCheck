# Working on BalanceCheck

The app is one Python process with three core files. Start with the [README](README.md) to run it locally.

| Change | Where to work |
| --- | --- |
| Labels, controls, report layout, source disclosures, downloads | `app.py` |
| Colors, spacing, typography | `.streamlit/config.toml`, `.streamlit/style.css` |
| CSV checks, metrics, expected roster, configurable policy, evidence tools | `data.py` |
| Model requests, tool dispatch, output validation, saved/exported reports | `agent.py` |
| Model task and evidence-handling instructions | `instructions.md` |
| Model evaluation and human scoring | `evaluate.py`, `evaluation/README.md` |

The UI calls `load_scenario(config=...)`, then `review(evidence, key, model)`. Python calculates metrics and eligibility; Gemini retrieves evidence and writes explanations. The validator accepts or rejects the original response. The screen renders that result against the saved evidence. Keep all stages on the same ReviewConfig; do not add separate thresholds to the UI or prompt.

## Make and check a change

1. Pull main and create a short task branch. Do not overwrite another teammate's work.
2. Make the smallest change in the relevant file. CSS never controls eligibility or analysis. Preserve original supplied data.
3. Run the offline software checks from the repository folder:

   ```bash
   python -m pip install -r requirements-dev.txt
   python -m pytest -q
   git diff --check
   ```

4. For UI changes, run Streamlit and check the first visit, settings/reset, report, source disclosures, and downloads. For model behavior changes, use **Practice review** and preserve rejected as well as accepted outputs. Do not tune on held-out evaluation cases.
5. Open a PR with what changed and what you verified. Review policy/prompt changes together before merging.

## Debug a review

- Input error: check the CSV schema and roster coverage before touching model code.
- API error: use the safe diagnostic shown in the app. Owner credentials live in ignored `.env.local` or private Streamlit secrets. Visitors never configure them.
- Invalid output: download the original run record and inspect validation errors, cited IDs, settings, and tool results. Never relabel an invalid run as accepted or silently substitute the statistics baseline.
- Changed settings/input: the old report deliberately remains visible with a warning. Run again to get a result for the new inputs.

Run records under `runs/` are ignored. Downloads are the portable record; server-local storage may disappear after redeployment. Do not commit credentials. Use only synthetic project data with the hosted model. Software tests and a successful practice run do not establish held-out model accuracy.
