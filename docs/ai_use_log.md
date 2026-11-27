# AI use log

This log records assistance in this Codex chat; teammates should add their separate meaningful uses. Verify all entries before submission.

| Date | Use | Output and human review status |
| --- | --- | --- |
| 2026-11-20 | Codex analyzed the supplied proposal and midpoint assignment. | Explained required deliverables and separated planned tests from completed evidence. Team review pending. |
| 2026-11-20 | Codex read the supplied one-page spec and inspected the synthetic data archive. | Explained the file organization, agent tool loop, and repository plan. Data and spec were supplied by the team; their original creation history is not established by this log. |
| 2026-11-20 | Codex prepared the minimal architecture, build checklist, collaboration notes, ignore rules, and initial repository contents. | Original supplied inputs preserved. No agent implementation, model call, or evaluation performed. Team review pending. |

Add later implementation assistance, prompt changes, generated fixtures, actual runs, and human checks as they occur. Do not claim this covers AI use outside this chat.

## Gemini implementation assistance — November 20, 2026

Codex implemented the three-file Python/Streamlit app, data validation/calculations, read-only evidence functions, bounded Gemini tool loop, report checks, original-run logging, uploads/downloads, evaluation runner, draft answer keys, and setup notes. Codex wrote software tests using test doubles and mock HTTP. These checks do not measure model quality. A derived duplicate control removes repeated copies without changing original inputs. Statistics-only comparisons were run; no successful live model evaluation or hit rate is claimed. The team must review the code, guide interpretation, keys, and logs. Credential values are excluded from this log.

During live local setup, requests failed before evidence retrieval. Codex added safe exception/status diagnostics and identified an API-key-invalid response from Google. This setup failure is separate from the held-out evaluation; no key value or claimed successful recommendation is included.

Codex then added owner-only local setup, key validation via model metadata, explicit private local persistence, and hidden model/credential controls after configuration. Automated checks verify file permissions, preservation of other settings, refusal of symlink/unignored destinations, and the setup-to-reviewer screen transition. No live key is included in tests.

## Live model verification and repairs — November 20, 2026

Using the locally saved project credential without printing it, Codex ran small connection/generation probes and a controlled three-model comparison. Flash-Lite responded; Hydrogen and Flash returned server deadlines. An initial Flash-Lite practice output was rejected for missing context retrieval and invalid context references. Codex tightened mandatory retrieval before the final report, then obtained a valid fourteen-tool-call practice output. A UI rerun exposed a validator false positive for healthy comparison groups; Codex corrected affected-group validation and added a regression check. Original failed and valid practice outputs are preserved. These are development runs, not the held-out score. Codex also verified hosted-secret UI behavior with fake credentials and documented future cloud deployment; no cloud deployment or repo ownership transfer was performed.

Codex removed internal evaluation-readiness wording and the scenario lock from the interactive screen after user feedback. All sample scenarios can now run when model access is configured. Formal evaluation criteria and preregistration remain in the evaluation runner/docs, with the distinction between exploratory and held-out testing stated explicitly.

After the user reported a hosted Gemini quota error, one small request with the saved local key succeeded. That did not identify or rule out the hosted quota failure. Codex added safe structured quota/retry diagnostics, model-request counting, and a direct transition to final generation after required evidence retrieval, removing an unnecessary confirmation request. Offline tests cover short-term, daily, zero-allowance, and retry-delay responses, including actual SDK decoding over mock HTTP. No claim was made that quota had been increased or the hosted failure permanently resolved.

## Final product assistance — November 27, 2026

At the user's request, Codex implemented configurable review rules, roster/skill-group coverage checks, explicit missing records and partial-review warnings, numerical ranking enforcement, per-character report coverage, frozen run settings and stale-report handling, batched evidence tools, and a clean slate/teal Streamlit theme. Codex added regression tests and used the existing privately saved Gemini credential for practice-only default/custom-policy development checks, preserving failed outputs and obtaining accepted outputs. Codex inspected the live local interface, corrected report readability, and updated documentation. These are software/development checks, not held-out evaluation or measured designer time savings. The user/team still reviews the final product and logs their separate AI use. No credential values are included.

## Usability and visual polish — November 27, 2026

Codex audited the local first-visit/review experience using browser screenshots, looked at Figma's official UI3 design reference at the user's request, and refined the app into a Review/Evidence workspace with a charcoal/coral game-tool treatment. Codex added readable scenario labels, source text disclosures next to priorities, easier report downloads, accurate native upload-size controls, clearer progress messages, and a short contributor guide. Regression checks cover source text, preservation of original sources after input changes, API/invalid-output retry recovery, and invalid-rule reset recovery. Code and docs were checked; browser screenshots and final verification scope are recorded in usability_review.md. No claim of a held-out evaluation or full accessibility certification is made.
