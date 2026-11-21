# Known weaknesses and verification status

## Observed implementation limits

- Duplicate detection normalizes punctuation, whitespace, and case within the same author/character/update. It handles supplied punctuation variants but not general semantic paraphrases. Suspicious-comment labels also use heuristics.
- Uploads support the bundled game/roster, not arbitrary games. Guide/threshold changes require reviewed code/rules updates. Synchronization checks confirm supported numeric values and guide tokens, not every sentence's meaning.
- Automated report validation checks references, sample eligibility, actions, and some prohibited wording. It cannot prove every claim, ranking, or next step is sound, or catch every numerical-change formulation. Human scoring is mandatory.
- Multiple model requests per review consume quota. Fixed round/tool limits may stop a repetitive model. API failures are preserved, not disguised as successful reports.
- Numeric evidence is rendered directly from Python records instead of copied by the model. Interpretation errors remain possible.
- The baseline places supported investigations ahead of data collection and monitoring. That mixed-action ordering is an explicit MVP interpretation for team review before evaluation.
- No live prompt-injection resilience claim is justified by offline tests. Suspicious comments remain labeled untrusted evidence so real-model behavior can be evaluated.
- Raw runs contain synthetic comments and model outputs; local runs are ignored until selected for sharing. Keep uploaded inputs synthetic for this project.

## Software verification

Automated checks cover all supplied scenario loading, arithmetic/missing-count behavior, renamed-file overrides, normalized duplicates, allowlisted dispatch, invalid report rejection, bounded loops, failure handling, actual SDK serialization over mock HTTP, Streamlit interactions with a test double, and paired-case scoring. These are not real-model evaluation results.

## Still to verify

- Successful live Gemini practice run using a replacement private key and available project quota/model.
- Team-reviewed frozen answer keys, actual held-out outputs, hit rate, and verbatim failures.
- Fresh reviewer setup, sandbox credentials, Windows launch, cloud deployment, and real-model latency/quota behavior.
- Whether feedback/mechanics add better investigation steps or limitations than the statistics-only baseline.

No measured accuracy or effect on a live game's balance is claimed. Record observed live-model failures here as they occur.

## Initial live setup attempt

The first practice attempts failed before any evidence tool ran. The original generic error message was insufficient to identify the cause. Safe diagnostics were added; one fresh attempt returned Google HTTP 400 / API key invalid, and a subsequent attempt timed out before evidence retrieval. A separate metadata-only connection check and a longer review timeout were added. A successful live practice run remains outstanding. These setup failures are not scored model recommendations. No key value is recorded here.
