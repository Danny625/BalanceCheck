# Build plan and midpoint completion criteria

Status: local implementation exists; no live-model pass rate is claimed. Team review, live practice verification, and formal evaluation remain outstanding.

## Stage 1 — Agree on rules and data

- [x] Import the supplied synthetic data and one-page spec without changing originals.
- [x] Choose a single-process Streamlit/Python architecture.
- [ ] Team reviews guide, thresholds, ranking rules, and metric denominators.
- [ ] Clarify the spec's wording about outdated feedback: the guide excludes it from current-patch evidence. Preserve historical context separately.
- [ ] Clarify acceptable ranking/actions when strong evidence competes with Collect data priorities; record in the guide and answer keys before evaluation.
- [ ] Confirm a model/provider and API access before API implementation.

## Stage 2 — Build one complete practice run

- [x] Implement `data.py`, validate schemas, preserve missing counts, and support scenario reference overrides.
- [x] Verify rates, group/overall handling, sample eligibility, patch filtering, and duplicate normalization with focused tests.
- [x] Implement four read-only evidence tools.
- [x] Implement `agent.py` and instructions with a bounded tool loop and structured report validation.
- [ ] Demonstrate a complete run on `00_practice`; save its actual evidence/tool trace.

Do not tune on held-out scenarios. Use additional clearly labeled practice fixtures if needed.

## Stage 3 — Give peers a usable interface

- [x] Build `app.py`: scenario picker, Run button, report, tool log, and report download.
- [x] Add statistics/feedback CSV upload for the bundled game, with visible schema requirements and useful errors.
- [x] Write exact tested dependencies and plain-language setup instructions.
- [ ] Arrange reviewer credentials/sandbox privately and verify a fresh setup using only the README.

## Stage 4 — Evaluate and preserve evidence

- [ ] Write and commit acceptable outcomes and pre-registered success criteria before held-out model runs.
- [ ] Freeze code/instructions/guide for the initial evaluation and record the Git commit.
- [ ] Run all twelve supplied evaluation folders, representing ten logical cases.
- [ ] Cases 4 and 7 pass only if both versions pass. Report the logical-case hit rate and execution count separately.
- [ ] Resolve the duplicate-case comparison: a derived unrepeated control for case 6 is included; review and freeze it before evaluation. Record extra executions separately.
- [ ] Target at least 9/10 passing logical cases, with zero invented evidence or instructions obeyed from comments. Report safety failures separately from the aggregate score.
- [ ] Two teammates score actual outputs against the frozen key and resolve disagreements.
- [ ] Preserve every original output and reproduce failed outputs verbatim. Document subsequent fixes and reruns separately; do not replace the original score.
- [ ] Compare with a deterministic statistics-only ranking using the same guide. Assess whether context adds a valid limitation or next step.

An individual case passes only if selections/order/actions are acceptable, evidence matches inputs, required limitations appear without unsupported conclusions, and next steps match the key.

## Stage 5 — Complete the midpoint package

- [ ] Runnable repository with reviewer access verified.
- [ ] One-page spec updated to match the actual implementation.
- [ ] At least ten realistic logical test cases with expected/actual results, pass rate, and verbatim failures.
- [ ] Known weaknesses grounded in observed behavior; distinguish untested risks.
- [ ] One-page status memo: changes, reasons, what broke, work left, instructor needs.
- [ ] Concrete final-three-weeks plan, updated sources, and accurate AI use log.
- [ ] Body around four pages; append detailed evidence and instructions.
- [ ] Book the 15-minute instructor meeting and prepare two hardest open questions. Confirm actual course dates in Canvas.

## Proposed responsibilities from the proposal

| Teammate | Primary responsibility |
| --- | --- |
| Danny | Data loading/calculations, model connection, interface, repository/setup. |
| Scott | Game guide, decision/ranking rules, scope, demonstration. |
| Elizabeth | Feedback cases, frozen answer keys, evaluation documentation, sources/AI log. |
| Everyone | Review one full trace, cross-check labels, score outputs, test instructions. |

## After the midpoint

Week 1: collect peer stress tests and record reproducible failures. Week 2: address supported weaknesses and expand to at least twenty frozen final cases. Week 3: run the final evaluation, complete the comparison and limitations, verify reviewer access, and finish the report/demo. Align these stages with actual Canvas deadlines.
