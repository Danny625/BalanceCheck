# Sources

## Team-supplied material

- BalanceCheck proposal and midpoint assignment, pasted in this chat: scope, ten logical test situations, planned criterion, responsibilities, deliverables, and rubric. Confirm actual course dates in Canvas.
- [Supplied spec](BalanceCheck_Spec.pdf), November 20, 2026.
- [Original synthetic data inventory](../data/README.md) and [game guide](../data/shared/game_guide.md), supplied November 20, 2026. Original inputs preserved; the derived duplicate control is documented in evaluation/README.md.

## Implementation references

Accessed November 20, 2026:

- [Google function calling](https://ai.google.dev/gemini-api/docs/function-calling): tool declarations and stateless interaction history.
- [Google structured outputs](https://ai.google.dev/gemini-api/docs/structured-output): JSON schema report generation.
- [Google API keys](https://ai.google.dev/gemini-api/docs/api-key): project credentials and key replacement.
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing): selected-model free tier; quotas and availability vary by project.
- [Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/models/gemini-4-hydrogen): configurable default model identifier.
- Installed `google-genai` 3.6.1 source: request fields and SDK serialization checked with mock HTTP, without a live credential.

## Proposal references to retain and verify

- [Riot balance framework](https://www.leagueoflegends.com/en-us/news/dev/dev-balance-framework-update/), June 30, 2020: industry context, not validation of synthetic thresholds.
- [Pandas tabular data tutorial](https://pandas.pydata.org/docs/getting_started/intro_tutorials/02_read_write.html).
- [Streamlit documentation](https://docs.streamlit.io/).

The final three references came from the proposal and were not independently re-reviewed in full during implementation.
