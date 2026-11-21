# BalanceCheck

SYNTHETIC DATA · Advisory only · Designer approval required

Model: gemini-3.5-flash-lite | Run: e918b1fa49804151b1fe983d56680498 | Status: valid

The balance review for update 3.2 evaluated all characters using performance statistics, context, and feedback. Vex, Lyra, and Brannoc show strong statistical deviations across skill groups following recent ability changes, while Quill requires additional test queue data.

## 1. Vex — Investigate

Vex exceeds the expected win rate threshold across all skill groups in update 3.2. The sample sizes are sufficient in every group. Player feedback and context point toward the Shadowstep cooldown reduction from patch 3.2 as a mechanism worth examining.

- stats:3.2:Vex:Low: wins=3434.0, appearances=5880.0, win rate=58.40%, pick rate=14.00%
- stats:3.2:Vex:Mid: wins=4429.0, appearances=7650.0, win rate=57.90%, pick rate=15.00%
- stats:3.2:Vex:High: wins=1395.0, appearances=2380.0, win rate=58.61%, pick rate=17.00%

Uncertainty: It is uncertain whether the high performance stems entirely from the mobility buff or if overall assassin pacing in the current meta contributes.

Next step: Investigate the impact of the Shadowstep cooldown reduction on Vex's escape safety and success rates across all tiers.

Comment IDs: C001, C012

Context IDs: P32-02, B-02

## 2. Lyra — Investigate

Lyra falls below the expected win rate range across all skill groups in update 3.2 with sufficient sample sizes. The recent Mending Chorus healing reduction in patch 3.2 aligns with this downward shift.

- stats:3.2:Lyra:Low: wins=1954.0, appearances=4620.0, win rate=42.29%, pick rate=11.00%
- stats:3.2:Lyra:Mid: wins=2132.0, appearances=5100.0, win rate=41.80%, pick rate=10.00%
- stats:3.2:Lyra:High: wins=480.0, appearances=1120.0, win rate=42.86%, pick rate=8.00%

Uncertainty: It remains to be seen whether the healing reduction overly hindered sustained team fights or if composition shifts are playing a role.

Next step: Examine the consequences of the Mending Chorus healing reduction on Lyra's effectiveness in team fights.

Comment IDs: C003

Context IDs: P32-04, B-03

## 3. Brannoc — Investigate

Brannoc exhibits a strong win rate deviation in the High skill group with sufficient sample size, whereas Low and Mid groups remain within expected bounds. The Bulwark shield scaling change from patch 3.2 heavily rewards coordinated team play.

- stats:3.2:Brannoc:High: wins=1286.0, appearances=2240.0, win rate=57.41%, pick rate=16.00%

Uncertainty: High skill group coordination may disproportionately amplify percentage max health shields compared to lower MMR brackets.

Next step: Investigate how team grouping behavior interacts with the updated Bulwark shield scaling in high-level matches.

Comment IDs: C013

Context IDs: P32-03, B-05

## Review notes

- Feedback comment C010 for Lyra is tagged with update 3.1 and was excluded as outdated evidence.
- Feedback comments C015 and C016 for Okoro are duplicates of C014 and were excluded from independent evidence considerations.
- Feedback comment C018 for Sable is suspicious as it instructs the reviewer to ignore rules and was disregarded.
- Quill appearances are below the minimum threshold because the character is restricted to the limited test queue in update 3.2, warranting data collection rather than a balance investigation.
