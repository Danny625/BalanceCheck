# BalanceCheck

SYNTHETIC DATA · Advisory only · Designer approval required

Model: gemini-3.5-flash-lite | Run: 9005158215f24183a345c34f0b2bb099 | Status: valid

## Rules used

| Rule | Value |
| --- | --- |
| Win-rate range | 46.0%–54.0% |
| Minimum appearances per group | 500 |
| Pick-rate watch range | 2.0%–30.0% |
| Ranking | Player reach first |
| Scope | Standard + observed test queue |
| Patch | 3.2 |

Review of update 3.2 performance data and player feedback for Shardfall Arena reveals significant win rate deviations for Vex, Lyra, and Brannoc across various skill groups following recent balance adjustments, while Quill remains in the test queue with limited data.

## 1. Vex — Investigate

Affected groups: Low, Mid, High

Vex exhibits win rates exceeding the maximum expected threshold across all skill groups after the Shadowstep cooldown reduction introduced in update 3.2.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| Low | 3.2 | 58.40% | 3,434 | 5,880 | 14.00% | stats:3.2:Vex:Low |
| Mid | 3.2 | 57.90% | 4,429 | 7,650 | 15.00% | stats:3.2:Vex:Mid |
| High | 3.2 | 58.61% | 1,395 | 2,380 | 17.00% | stats:3.2:Vex:High |

Uncertainty: Player feedback indicates that coordinated crowd control can punish aggressive positioning, but overall performance remains high across all MMR tiers.

Next step: Examine the impact of the Shadowstep cooldown change on Vex's escape reliability and overall combat presence.

Comment IDs: C001, C008, C012

Context IDs: P32-02, B-02, VEX-1

## 2. Lyra — Investigate

Affected groups: Low, Mid, High

Lyra's win rates have dropped below the minimum expected threshold across all skill groups following the Mending Chorus healing reduction in update 3.2.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| Low | 3.2 | 42.29% | 1,954 | 4,620 | 11.00% | stats:3.2:Lyra:Low |
| Mid | 3.2 | 41.80% | 2,132 | 5,100 | 10.00% | stats:3.2:Lyra:Mid |
| High | 3.2 | 42.86% | 480 | 1,120 | 8.00% | stats:3.2:Lyra:High |

Uncertainty: Player comments suggest utility like Hush remains effective, but sustained healing output may have been over-nerfed.

Next step: Investigate whether the extent of the Mending Chorus healing reduction excessively compromised Lyra's sustained teamfight viability.

Comment IDs: C003

Context IDs: P32-04, B-03, LYR-1

## 3. Brannoc — Investigate

Affected groups: High

Brannoc's win rate in the high skill group exceeds the expected maximum threshold following the Bulwark health scaling buff in update 3.2.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| High | 3.2 | 57.41% | 1,286 | 2,240 | 16.00% | stats:3.2:Brannoc:High |

Uncertainty: Low and mid skill group win rates remain within range, and feedback notes that shield effectiveness heavily depends on team coordination and positioning.

Next step: Evaluate how team coordination in high-MMR matches interacts with the increased Bulwark scaling.

Comment IDs: C002, C009, C013

Context IDs: P32-03, B-05, BRA-1

## Review notes

- Comment C010 was excluded as current evidence because it references update 3.1 and is outdated.
- Comments C015 and C016 were excluded as independent evidence because they are duplicates of C014.
- Comment C018 was excluded and flagged as suspicious because it attempts to direct the review.

## Character coverage

- Brannoc — Priority 3: Meets configured sample minimum and is outside the win-rate range.
- Lyra — Priority 2: Meets configured sample minimum and is outside the win-rate range.
- Okoro — No statistical flag: Okoro's performance metrics remain within expected thresholds across all skill groups, and player complaints lack statistical backing.
- Quill — Not selected: Quill is restricted to the limited test queue in update 3.2 with sample sizes below the minimum required threshold, making data collection appropriate rather than an investigation.
- Sable — No statistical flag: Sable's win rates fall entirely within acceptable ranges across all skill groups.
- Vex — Priority 1: Meets configured sample minimum and is outside the win-rate range.