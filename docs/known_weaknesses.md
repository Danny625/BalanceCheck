# Known weaknesses and verification status

## Observed implementation limits

- Duplicate detection normalizes punctuation, whitespace, and case within the same author/character/update. It handles supplied punctuation variants but not general semantic paraphrases. Suspicious-comment labels also use heuristics.
- Uploads support the bundled game/roster, not arbitrary games. Thresholds, ranking, and roster scope are configurable; changes to game definitions or roster require reviewed code/reference updates. Synchronization checks confirm supported numeric values and guide tokens, not every sentence's meaning.
- Automated report validation checks references, sample eligibility, actions, and some prohibited wording. It cannot prove every claim, ranking, or next step is sound, or catch every numerical-change formulation. Human scoring is mandatory.
- Multiple model requests per review consume quota. Fixed round/tool limits may stop a repetitive model. API failures are preserved, not disguised as successful reports.
  The controller now moves directly to report generation once all required tools are complete, avoiding an extra model confirmation. This reduces requests but cannot remove Google's project limits. Quota errors preserve safe metric identifiers, limits, and retry delays when supplied; ambiguous errors remain explicitly ambiguous.
- Numeric evidence is rendered directly from Python records instead of copied by the model. Interpretation errors remain possible.
- The active policy places supported investigations ahead of data collection and monitoring. Python enforces this ordering. Player reach means the share of the player base in flagged skill groups, not observed character users or proven impact. The minimum appearance setting is an eligibility rule, not statistical confidence.
- No live prompt-injection resilience claim is justified by offline tests. Suspicious comments remain labeled untrusted evidence so real-model behavior can be evaluated.
- Raw runs contain synthetic comments and model outputs; local runs are ignored until selected for sharing. Keep uploaded inputs synthetic for this project.

## Software verification

Automated checks cover all supplied scenario loading, arithmetic/missing-count behavior, renamed-file overrides, normalized duplicates, allowlisted dispatch, invalid report rejection, bounded loops, failure handling, actual SDK serialization over mock HTTP, Streamlit interactions with a test double, and paired-case scoring. These are not real-model evaluation results.

## Still to verify

- Real-model consistency across the frozen held-out evaluation; the practice run alone is insufficient.
- Team-reviewed frozen answer keys, actual held-out outputs, hit rate, and verbatim failures.
- Fresh reviewer setup, sandbox credentials, Windows launch, cloud deployment, and real-model latency/quota behavior.
- Whether feedback/mechanics add better investigation steps or limitations than the statistics-only baseline.

No measured accuracy or effect on a live game's balance is claimed. Record observed live-model failures here as they occur.

## Initial live setup attempt

The first practice attempts failed before any evidence tool ran. The original generic error message was insufficient to identify the cause. Safe diagnostics were added; one fresh attempt returned Google HTTP 400 / API key invalid, and a subsequent attempt timed out before evidence retrieval. A separate metadata-only connection check and a longer review timeout were added. A subsequent Flash-Lite practice run succeeded, as documented below. These setup failures are not scored model recommendations. No key value is recorded here.

## Successful practice run and observed repairs

A controlled same-settings comparison found Flash-Lite responsive while Hydrogen and Flash returned HTTP 504. The full Flash-Lite practice run retrieved fourteen tools and passed validation. An earlier failed practice output skipped required context/comment retrieval and invented a patch reference; the controller now enforces those lookups. A later output correctly cited normal skill groups as comparisons but was rejected by an overly strict validator; eligibility checks now apply to affected groups, with regression coverage. Original model output is not silently repaired. See model_choice.md and examples/practice/ for evidence.

## Final product development checks — November 27, 2026

Whole-character and skill-group omissions are now detected against the selected expected roster. Default scope includes standard characters and observed test-queue characters; Entire roster also expects unobserved test-queue records. Reports remain partial when required counts are absent. Settings are isolated per browser session and copied into each run; they are not saved as shared studio defaults. Human approvals remain outside the app; there is no persistent approval audit trail. Streamlit server-local run files may not survive redeployment; download important records.

Live practice development runs exposed both a round-limit failure from repeated individual lookups and reports that ignored custom rules or put Quill ahead of supported investigations. Batched tools and an explicit Python-calculated shortlist were added; validation continues to reject unsupported output instead of silently repairing it. A too-strict validator also rejected explanations for healthy omitted characters; it now permits them. Original attempts remain under ignored runs/. Successful runs do not establish a model hit rate. See final_updates.md for verification scope.
