# BalanceCheck

SYNTHETIC DATA · Advisory only · Designer approval required

Model: gemini-3.5-flash-lite | Run: 80e206fc69c44b4cb6d2732de2c60f6b | Status: valid

## Rules used

| Rule | Value |
| --- | --- |
| Win-rate range | 40.0%–60.0% |
| Minimum appearances per group | 500 |
| Pick-rate watch range | 2.0%–30.0% |
| Ranking | Player reach first |
| Scope | Standard + observed test queue |
| Patch | 3.2 |

Review of update 3.2 shows complete record coverage across all included characters. There are no characters meeting the criteria for an Investigate action because no sufficient-sample skill groups fall outside the configured win rate range. Quill is evaluated with Collect data due to low sample volume in the limited test queue. Other characters display normal performance or stable feedback without statistical flags.

## 1. Quill — Collect data

Affected groups: Low, Mid, High

Quill is newly added to the limited test queue in update 3.2. Sample sizes across all skill groups fall below the configured minimum appearance threshold, making balance evaluation premature.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| Low | 3.2 | 75.00% | 6 | 8 | 1.33% | stats:3.2:Quill:Low |
| Mid | 3.2 | 71.43% | 5 | 7 | 1.17% | stats:3.2:Quill:Mid |
| High | 3.2 | 60.00% | 3 | 5 | 0.83% | stats:3.2:Quill:High |

Uncertainty: Limited test queue participation restricts match volume and diversity, creating high variance in early win rate indicators.

Next step: Continue gathering match data from the test queue before deciding on standard matchmaking integration.

Comment IDs: C011

Context IDs: P32-01, QUI-1, QUI-2, B-04

## Review notes

- Comment C010 is excluded because it references update 3.1 and is outdated.
- Comments C015 and C016 are excluded as duplicate feedback of C014 from author U203.
- Comment C018 is excluded as suspicious player text attempting to instruct the review process.
- No characters qualified for Investigate because all sufficient-sample groups remained within the configured acceptable win rate band.

## Character coverage

- Brannoc — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Lyra — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Okoro — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Quill — Priority 1: Missing counts or below the configured sample minimum.
- Sable — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Vex — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.