import csv
import json
from pathlib import Path

from evaluate import KEY, SCORE_COLUMNS, summarize


def test_paired_case_requires_both_versions_and_pending_is_not_a_hit_rate(tmp_path, capsys):
    key = json.loads(KEY.read_text())
    rows = []
    for case in key["cases"]:
        for scenario in case["scenarios"]:
            row = dict.fromkeys(SCORE_COLUMNS, "")
            row.update(case=case["case"], scenario=scenario, run_file="run.json", selection_pass="true",
                       evidence_pass="true", limitations_pass="true", next_step_pass="true",
                       invented_evidence="false", instruction_obeyed="false", reviewer_1="One", reviewer_2="Two")
            rows.append(row)
    (tmp_path / "run.json").write_text(json.dumps({"raw_outputs": [{"text": "original failure"}]}))
    rows[4]["selection_pass"] = "false"  # angry version of case 4

    def write():
        with (tmp_path / "scores.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=SCORE_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)

    write()
    summarize(tmp_path)
    result = json.loads((tmp_path / "summary.json").read_text())
    assert result["passed"] == 9 and result["hit_rate"] == .9
    assert result["outcomes"]["4"] is False
    assert "original failure" in (tmp_path / "failures_verbatim.md").read_text()
    rows[0]["reviewer_2"] = ""
    write()
    summarize(tmp_path)
    assert json.loads((tmp_path / "summary.json").read_text())["hit_rate"] is None
