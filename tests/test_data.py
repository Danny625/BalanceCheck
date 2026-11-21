from io import StringIO

import pandas as pd
import pytest

from data import DATA, CURRENT, DataError, load_scenario, scenarios, statistics_baseline


def test_supplied_scenarios_load_and_serialize_without_nan():
    import json
    for name in scenarios():
        evidence = load_scenario(name)
        json.dumps(evidence.get_performance(), allow_nan=False)
        json.dumps(evidence.get_feedback(evidence.characters[0]), allow_nan=False)


def test_weighted_rates_and_skill_specific_issue():
    evidence = load_scenario("00_practice")
    metrics = evidence.metric_index()
    assert metrics["stats:3.2:Vex:Low"]["win_rate"] == pytest.approx(3434 / 5880)
    overall = next(r for r in evidence.get_performance("Vex")["overall"] if r["update"] == CURRENT)
    assert overall["win_rate"] == pytest.approx((3434 + 4429 + 1395) / (5880 + 7650 + 2380))
    issue = load_scenario("08_misleading_average")
    baseline = statistics_baseline(issue)
    assert baseline[0]["character"] == "Brannoc"
    assert baseline[0]["affected_skill_groups"] == ["High"]


def test_missing_denominators_never_become_zero_or_an_invented_rate():
    e = load_scenario("05_missing_records")
    rows = [r for r in e.get_performance("Vex")["rows"] if r["update"] == CURRENT]
    assert all(r["appearances"] is None and r["win_rate"] is None for r in rows)
    assert all(not r["sample_sufficient"] for r in rows)
    overall = next(r for r in e.get_performance("Vex")["overall"] if r["update"] == CURRENT)
    assert overall["win_rate"] is None
    assert statistics_baseline(e)[0]["action"] == "Collect data"


def test_feedback_duplicates_outdated_and_instructions():
    e = load_scenario("00_practice")
    comments = e.feedback.set_index("comment_id")
    assert comments.loc["C015", "duplicate_of"] == "C014"
    assert comments.loc["C016", "duplicate_of"] == "C014"
    assert bool(comments.loc["C010", "outdated"])
    assert bool(comments.loc["C018", "suspicious"])


def test_renamed_scenario_uses_all_overrides_and_preserves_ranking():
    original = load_scenario("07a_original_names")
    renamed = load_scenario("07b_renamed_reordered")
    assert "Vex" not in renamed.characters and "Nyra" in renamed.characters
    assert all(row["character"] in ["Nyra", "All"] for rows in renamed.get_character_context("Nyra").values() for row in rows)
    assert [r["character"] for r in statistics_baseline(original)] == ["Vex", "Lyra"]
    assert [r["character"] for r in statistics_baseline(renamed)] == ["Nyra", "Isk"]


def upload_frames():
    folder = DATA / "scenarios" / "00_practice"
    return pd.read_csv(folder / "stats.csv", dtype=str, keep_default_na=False), (folder / "feedback.csv").read_bytes()


@pytest.mark.parametrize("column,value", [("wins", "-1"), ("wins", "100000"), ("appearances", "2.5"), ("wins", "inf"), ("picks", "not a number")])
def test_invalid_uploads_rejected(column, value):
    stats, feedback = upload_frames()
    stats.loc[0, column] = value
    with pytest.raises(DataError):
        load_scenario(stats_bytes=stats.to_csv(index=False).encode(), feedback_bytes=feedback)


def test_deleted_group_is_explicit_missing_evidence():
    stats, feedback = upload_frames()
    stats = stats[~((stats.character == "Vex") & (stats["update"] == CURRENT) & (stats.skill_group == "High"))]
    e = load_scenario(stats_bytes=stats.to_csv(index=False).encode(), feedback_bytes=feedback)
    assert e.metric_index()["stats:3.2:Vex:High"]["win_rate"] is None
    assert e.warnings


def test_pick_denominator_zero_is_not_infinite():
    stats, feedback = upload_frames()
    stats.loc[0, ["picks", "eligible_selections"]] = ["0", "0"]
    e = load_scenario(stats_bytes=stats.to_csv(index=False).encode(), feedback_bytes=feedback)
    assert e.metric_index()["stats:3.1:Vex:Low"]["pick_rate"] is None
