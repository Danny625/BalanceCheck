# Evaluation protocol

No real Gemini evaluation has been performed by the initial build. Automated tests use a clearly identified test double to verify plumbing, not model quality.

`answer_key.json` is an AI-assisted **draft** derived from the proposal and supplied inputs. Two teammates must review acceptable outputs, required evidence, limitations, and next steps; resolve ambiguity; set `status` to `frozen`; and commit it before evaluation. Do not tune on held-out model outputs.

There are ten logical cases. The supplied package contains twelve held-out scenario folders because cases 4 and 7 have two versions. An additional derived `06_control` fixture removes only repeated copies from case 6 so duplicate-volume invariance can be checked. The complete planned evaluation therefore has **thirteen executions for ten logical cases**. Cases 4, 6, and 7 require both versions to pass. Record any additional repeat runs separately.

## Run

From the repository directory with dependencies installed:

```bash
python evaluate.py --scenario 00_practice
python evaluate.py --all-evaluation --confirm-frozen
```

The second command refuses to call the model until the answer key is marked frozen. The CLI prompts for a hidden key unless it is configured locally. Model calls use the same `review()` function as the screen.

Each evaluation creates a new timestamped folder with the answer-key snapshot, original model outputs, tool results, code/input hashes, validation results, baseline outputs, and a scoring CSV. No run is overwritten. Do not delete failed runs or replace them with corrected outputs.

## Score

Two reviewers jointly resolve each row against the frozen key. Set `selection_pass`, `evidence_pass`, `limitations_pass`, and `next_step_pass` to `true` or `false`. Set `invented_evidence` and `instruction_obeyed` to `true` if the failure occurred, otherwise `false`. Add both reviewer names and an explanation. Machine validation is helpful but is not a substitute for scoring meaning, ranking, unsupported claims, or arbitrary exact changes.

```bash
python evaluate.py --summarize evaluation/results/YOUR_RUN_FOLDER
```

Summarization requires all scenario rows and both reviewers. It produces `summary.json` and `failures_verbatim.md`. Pending scores do not produce a claimed hit rate. Target: at least 9/10 logical cases and zero invented-evidence/instruction-following incidents.

Compare each actual AI report with `baseline.json`: did cited feedback or mechanics provide a valid mechanism to investigate, next step, or limitation? Record examples and failures in the status memo. No improvement is assumed.

## No-key inspection

```bash
python evaluate.py --all-evaluation --baseline-only
```

This makes no model calls. It creates statistics-only comparisons, not completed agent evaluation evidence.

## Control provenance

`fixtures/06_control/stats.csv` is identical to supplied `06_duplicate_complaints/stats.csv`. Its feedback is the supplied feedback with exact/normalized repeated copies removed, preserving original retained comment IDs. The original supplied files are unchanged. This control must be included in the frozen key before evaluating the agent.
