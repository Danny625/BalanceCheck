# Final product updates — November 27, 2026

## Using the product

1. Choose a scenario or upload the two supported synthetic CSVs.
2. Optionally expand **Review rules**. Defaults are 46–54% win rate, 500 appearances per group, 2–30% pick-rate watch, player reach first, and standard plus observed test-queue characters. Reset restores these defaults.
3. Inspect **Review rules & data coverage**. Missing characters, skill groups, or counts produce warnings. Malformed/impossible data is rejected. Missing values remain unavailable; a report with gaps is explicitly partial.
4. On **Review**, run the AI review. Read up to three priority cards, calculated evidence, uncertainty, and next steps. The coverage table explains each character's disposition. Cited comments and patch changes open under **Sources for this priority**; technical logs stay collapsed. **Evidence** contains the current input tables, guide, context, and statistics baseline.
5. Download the report and complete run record. Designer approval happens outside this app. Server-local files are not durable shared storage.

Settings belong to the current browser session, not everyone visiting the hosted app. They are copied into every report and JSON run. Changing inputs/settings preserves the old report with a warning and its original evidence; rerun to apply changes. Visitors continue to use the owner's configured Gemini access without key or model selection.

## What decides the priorities

Python calculates rates, eligibility, and numerical ordering. Supported investigations come first, then data collection, then monitoring. Within an evidence class, **Player reach first** uses the sum of fixed player shares in affected groups, followed by maximum deviation beyond the expected win-rate range. **Largest deviation first** reverses those two criteria. Reach is a proxy based on skill-group shares (Low 40%, Mid 45%, High 15%), not a count of affected character users. A configured minimum sample is not a statistical confidence claim.

The model retrieves rules, metrics, context, and feedback through four read-only tools. It receives the calculated shortlist, explains mechanisms and limitations, proposes next steps, and can return fewer priorities with explanations. It cannot silently change eligibility or put a low-sample request ahead of an omitted supported investigation. Python validates the output; invalid original outputs are preserved and visibly unaccepted. A validation pass does not prove semantic correctness.

The default scope expects every standard character plus test-queue characters observed in current records. **Standard only** excludes the test queue; **Entire roster** expects even unobserved test-queue characters. All expected characters require Low/Mid/High records. Absent rows are explicitly marked as derived missing records, with no invented rates. Uploads remain limited to Shardfall Arena and patches 3.1/3.2.

## Verification

- 54 automated checks pass. Coverage includes arithmetic, reference validation, missing complete characters/groups, configurable metrics/order/actions, scope, batched retrieval, rejected outputs, stale-report snapshots, reset behavior, isolated user settings, uploads, and API failures using mock HTTP.
- Live **practice-only** default review passed: Vex, Lyra, Brannoc, all Investigate, in that order. Brannoc is included; Quill does not displace a supported investigation. Two model requests.
- Live practice review with a wider **40–60%** win-rate range passed: Quill / Collect data; no Investigate priority. Two model requests. This checks that settings change actual behavior.
- A preceding live report selected Quill while omitting supported investigations. Validation rejected it. The original rejected output is included beside successful runs; it was not silently rewritten.
- The refreshed local Streamlit interface was inspected in a browser, including report cards, rule controls, and every-character explanations. UI tests verify old reports retain original rules when settings change.

Original synthetic inputs and evaluation keys are unchanged. These development checks do not establish a held-out hit rate, designer time savings, live-game effectiveness, or guaranteed Gemini availability. No held-out cases were used for prompt development. The existing three-file architecture remains; no database, extra service, or agent framework was added.

See [actual default report](../examples/final_checks/default_report.md), [custom-rule report](../examples/final_checks/custom_report.md), and [rejected original run](../examples/final_checks/rejected_run.json). These records identify the code hashes used; UI-only readability refinements followed the model runs. No approval audit system or persistent shared settings were added.
