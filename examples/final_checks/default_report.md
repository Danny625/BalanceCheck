# BalanceCheck

SYNTHETIC DATA · Advisory only · Designer approval required

Model: gemini-3.5-flash-lite | Run: 7977e3eee8f34826b35b528c3229b41a | Status: valid

## Rules used

| Rule | Value |
| --- | --- |
| Win-rate range | 46.0%–54.0% |
| Minimum appearances per group | 500 |
| Pick-rate watch range | 2.0%–30.0% |
| Ranking | Player reach first |
| Scope | Standard + observed test queue |
| Patch | 3.2 |

Review of update 3.2 performance data and player feedback reveals significant balance outliers across multiple skill groups. Vex and Lyra show widespread win-rate deviations across all tiers following recent changes, while Brannoc exhibits a high-tier win-rate spike. Quill remains in the test queue with insufficient sample volume.

## 1. Vex — Investigate

Affected groups: Low, Mid, High

Vex exceeds the upper win-rate threshold across all skill groups after receiving a cooldown reduction on Shadowstep. Player comments indicate that escaping after dives feels much easier and consistent.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| Low | 3.2 | 58.40% | 3,434 | 5,880 | 14.00% | stats:3.2:Vex:Low |
| Mid | 3.2 | 57.90% | 4,429 | 7,650 | 15.00% | stats:3.2:Vex:Mid |
| High | 3.2 | 58.61% | 1,395 | 2,380 | 17.00% | stats:3.2:Vex:High |

Uncertainty: It is uncertain whether the elevated performance stems entirely from mobility frequency or broader map and meta shifts in update 3.2.

Next step: Examine Shadowstep cooldown adjustments and overall assassin impact.

Comment IDs: C001, C008, C012

Context IDs: P32-02, B-02

## 2. Lyra — Investigate

Affected groups: Low, Mid, High

Lyra falls below the lower win-rate threshold across all skill groups following the healing reduction applied to Mending Chorus in update 3.2.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| Low | 3.2 | 42.29% | 1,954 | 4,620 | 11.00% | stats:3.2:Lyra:Low |
| Mid | 3.2 | 41.80% | 2,132 | 5,100 | 10.00% | stats:3.2:Lyra:Mid |
| High | 3.2 | 42.86% | 480 | 1,120 | 8.00% | stats:3.2:Lyra:High |

Uncertainty: Player perception remains mixed, with some comments suggesting utility remains strong despite reduced sustain.

Next step: Investigate the impact of Mending Chorus healing adjustments on sustained teamfight success.

Comment IDs: C003

Context IDs: P32-04, B-03

## 3. Brannoc — Investigate

Affected groups: High

Brannoc exceeds the upper win-rate threshold in high-tier matches following the Bulwark maximum health scaling buff, supported by feedback highlighting strong coordination around shields.

| Skill group | Patch | Win rate | Wins | Appearances | Pick rate | Evidence reference |
| --- | --- | --- | --- | --- | --- | --- |
| High | 3.2 | 57.41% | 1,286 | 2,240 | 16.00% | stats:3.2:Brannoc:High |

Uncertainty: Performance varies significantly based on team coordination and positioning, remaining within normal ranges in lower skill groups.

Next step: Review high-tier synergy with Bulwark scaling and potential stacking mechanics.

Comment IDs: C002, C013

Context IDs: P32-03, B-05

## Review notes

- Excluded comment C010 because it references update 3.1 and is outdated.
- Excluded comments C015 and C016 because they are duplicates of C014.
- Excluded comment C018 because it is suspicious and attempts to direct review rules.

## Character coverage

- Brannoc — Priority 3: Meets configured sample minimum and is outside the win-rate range.
- Lyra — Priority 2: Meets configured sample minimum and is outside the win-rate range.
- Okoro — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Quill — Not selected: Quill is restricted to the limited test queue with sample counts below the minimum threshold, requiring data collection rather than an investigation priority.
- Sable — No statistical flag: Current metrics meet the configured checks; this is not proof that no issue exists.
- Vex — Priority 1: Meets configured sample minimum and is outside the win-rate range.