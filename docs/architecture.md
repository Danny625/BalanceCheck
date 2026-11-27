# Simplest architecture

Status: implemented locally with Gemini; a live practice run is verified; formal evaluation remains pending. Based on the supplied project material.

## One application

Use Python, Pandas, Streamlit, and Gemini through its API. Run everything except the model in a single Python process. Use CSV/Markdown files as storage. No database, separate frontend/backend, agent framework, vector database, live game integration, or model training is needed.

```text
Browser: scenario / CSV upload + review rules → Run review
                           |
                        app.py
                           |
              data.py loads and calculates
                           |
               agent.py runs model/tool loop
                     ↔ hosted model API
                           |
               validate report and save run
                           |
                 browser displays report
```

## Only three application files

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit controls, input errors, progress, report display, downloadable report, expandable tool/evidence log. Calls the other two modules. |
| `data.py` | Scenario loading, shared-file overrides, input validation, Pandas calculations, evidence IDs, feedback flags, and read-only evidence functions. Also supports the statistics-only comparison. |
| `agent.py` | Loads agent instructions, calls the model, executes only permitted evidence functions, returns tool results, validates the final structured report, and records the run. |

Keep the four read-only tools in `data.py`; separate files for every tool are unnecessary. Keep report validation in `agent.py` until complexity warrants extraction.

Supporting implementation files:

- `instructions.md`: agent task, guide-following behavior, untrusted-comment boundary, and report requirements.
- `requirements.txt`: exact tested dependencies.
- `.env.example`: empty configuration template; the real credential file remains ignored.
- `evaluate.py`: calls the same review function as the UI for each frozen scenario.
- `tests/test_data.py`: meaningful checks for calculations, missing records, overrides, and duplicate handling.
- `evaluation/answer_key.json`: draft acceptable outcomes and scoring rules awaiting human review, never model input.
- `evaluation/results/`: original outputs, tool logs, scoring, failures, baseline comparison, and run metadata. Save each run separately.

## Input loading

1. Load the files in `data/shared/`.
2. Load `stats.csv` and `feedback.csv` from the selected scenario.
3. Replace shared files with scenario-local copies of the same name when present. This is essential for `07b_renamed_reordered`.
4. Validate schemas and references. Preserve update identifiers such as `3.2` as strings; preserve missing values rather than filling them with zero.
5. Focus the review on update 3.2. Update 3.1 supplies historical context. Compare current records against the roster/scope and all three expected skill groups. Add explicitly missing derived rows without inventing counts or rates; warn before review and mark incomplete reports partial.

Upload mode accepts a statistics CSV and a feedback CSV for Shardfall Arena and uses the bundled guide/reference files. Explain this restriction in the UI. Uploaded data stays in memory and does not overwrite repository inputs. Support custom games only in later work.

## Deterministic calculations

Python calculates win rate as wins / appearances and pick rate as picks / eligible selections, per character/update/skill group. Overall win rate is total wins / total appearances, not an average of group percentages. Group-level evidence is always available. Do not calculate a complete overall rate when constituent required counts are missing without explicitly identifying it as partial; simplest is to omit it.

Default to the supplied machine-readable thresholds: expected win rate 46–54%, minimum 500 current-update appearances per group, pick watch outside 2–30%, and at most three priorities. Users may change the win-rate bounds, minimum appearances, pick-rate watch bounds, ranking policy, and roster scope. Python applies one immutable ReviewConfig to metrics, tools, ordering, validation, UI, and the saved report. Check original threshold CSVs against the original Markdown guide, then render the active policy into the guide so the model receives one consistent rule set. Numerical eligibility and ordering are calculated in Python; the model explains context, uncertainty, and next steps and may omit unsupported recommendations with reasons.

Preserve missing-count cases as analyzable data-quality issues that lead to Collect data. Reject impossible numeric values or malformed files with useful messages. Do not silently drop affected rows.

Identify statistics by a stable reference such as `stats:3.2:Vex:Low`; reject duplicate keys unless an explicit aggregation rule is agreed. Preserve supplied comment, patch, ability, and backlog IDs. Identify feedback duplicates within the same author, character, and update using normalized text for the initial implementation; flag punctuation/case variants. Broader paraphrase detection is a documented limitation until tested.

## Four read-only tools

| Tool | Returns |
| --- | --- |
| `get_review_rules()` | Guide, thresholds, and skill-group definitions/player shares. |
| `get_performance(character=None)` | Calculated current/historical metrics, raw counts, evidence references, sample and missing-data flags. |
| `get_character_context(character=None)` | Character, abilities, relevant patch notes, and design backlog. Proposed backlog changes are context, not approved recommendations. |
| `get_feedback(character=None)` | Comments with IDs, update, author, known skill group, and duplicate/outdated flags. |

Omit character to retrieve all in-scope context or feedback in a single batched call. Bind these functions to the selected scenario in application code. Do not expose arbitrary paths, shell execution, file writing, or evaluation documents as model tools. Use neutral scenario identifiers in the model conversation rather than descriptive test-folder names.

## One review, step by step

1. `app.py` loads and validates the selected inputs through `data.py`.
2. `app.py` calls the single review entry point in `agent.py` with the loaded evidence.
3. The model receives the task and tool definitions. Require rules, unfiltered performance, and context/feedback for every character with current records before a final report.
4. The model requests a tool. Python validates its arguments, executes the allowlisted function, and returns its result.
5. Repeat within a fixed call limit. Stop with an honest error on API failure or an exhausted limit; never substitute a fabricated AI report.
6. Request zero to three priorities in a structured report. Each has character, rank, affected groups, one action (Investigate / Monitor / Collect data), metric references, comment IDs where relevant, uncertainty, and next step.
7. Check schema, references, numeric claims where machine-verifiable, affected-group sample eligibility for Investigate (healthy groups may be cited for comparison), and priority count. Display a validation failure instead of silently accepting an invalid report. Semantic judgment still requires human evaluation.
8. Display the report, every-character coverage, its frozen configuration, and an expandable tool log. Keep a previous report visibly tied to its original inputs/settings after changes. Save the original output, validation results, model identifier, instructions version/hash, input hashes, timestamp, and tool calls. Do not save credentials.

Comments are untrusted evidence. Ignore embedded instructions. Outdated comments may supply historical context but cannot support current-patch claims. Duplicate copies count once; outdated feedback is excluded from current evidence rather than counted as a fresh complaint.

## Human control

The output is advisory. The human reads it and approves or rejects investigations outside the app. No approval database or game-change buttons are needed for this MVP.

## Reviewer access

Choose the assignment's repository option first. Before submission, provide tested plain-language installation/run instructions and privately arrange a working reviewer sandbox credential if credentials are needed. Never publish a credential in GitHub or require a peer to obtain access without guidance. Optional deployment can reuse the same app; it is not a prerequisite for building the agent.

## Build adjustments

Gemini supplies the hosted model. Its Interactions API uses stateless history (store=False), bounded tool calls, and a separate schema-constrained final response. Numeric evidence is rendered directly from Python records. Raw local runs are saved under ignored runs/; formal evaluation records use timestamped evaluation/results/ folders. These adjustments preserve the three-file design.
