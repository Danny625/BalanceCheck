# Model choice: verified working MVP option

Current choice: `gemini-3.5-flash-lite`. This is the working choice among the models tested, not a claim of globally best reasoning quality.

## Controlled connection test

See [recorded probe results](model_probe_results.json). All three models used the same saved project key, SDK, standard `generateContent` endpoint, prompt (`Reply with just OK.`), output cap (128 tokens), 20-second request timeout, and one attempt (no retries).

| Model | Observed result | Elapsed |
| --- | --- | --- |
| gemini-3.5-flash-lite | Returned OK | 0.434 seconds |
| gemini-3.8-flash | HTTP 504, deadline expired | 18.246 seconds |
| gemini-4-hydrogen | HTTP 504, deadline expired | 19.088 seconds |

These observations establish that metadata availability and published free-tier pricing did not guarantee successful generation at the time tested. They do not identify the underlying reason for Google's server deadlines. No billing/quota error was observed in this comparison. One probe per model cannot establish long-term reliability.

## Full agent verification

The Flash-Lite agent completed the practice scenario with fourteen tool calls, exact statistic/comment/context references, three investigation priorities, and explicit excluded-feedback notes. The saved [practice run](../examples/practice/valid_run.json) passed the application's evidence/schema checks. This is development evidence, not the held-out evaluation hit rate.

The [earlier failed practice run](../examples/practice/invalid_run.json) is preserved: the model stopped after rules/statistics and invented a generic patch reference. The controller now requires context and feedback for every current character before final generation. A later UI practice run exposed an overly strict validator that rejected healthy skill-group comparisons; the validator was corrected to check eligibility for affected groups while still allowing comparison evidence. Regression tests cover this behavior.

## Why use it now

It is responsive in the controlled test, supports the actual tool loop and structured report, and completed the required small-roster workflow. Google lists a [free tier for this model](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite), subject to project access and quota. The ten-case frozen evaluation still needs to assess recommendation quality. Revisit the choice if those results show a material weakness; do not assume faster or more expensive models are better for this task.
