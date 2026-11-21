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
