import copy
import json
from types import SimpleNamespace

import pytest

from agent import Report, dispatch, review, save_run, validate_report
from data import DataError, load_scenario


def example_report():
    return {"summary": "Review Vex's current performance.", "review_notes": ["Player comments are context, not proof of a cause."],
            "priorities": [{"character": "Vex", "affected_skill_groups": ["Low", "Mid", "High"],
                            "action": "Investigate", "metric_refs": [f"stats:3.2:Vex:{g}" for g in ["Low", "Mid", "High"]],
                            "comment_ids": ["C012"], "context_refs": ["P32-02"], "rationale": "Performance is outside the expected range across skill groups.",
                            "uncertainty": "Comments do not establish the cause.", "next_step": "Review matches involving Shadowstep before deciding on a change."}]}


class Response:
    def __init__(self, steps=None, output_text=""):
        self.steps = steps or []
        self.output_text = output_text
        self.usage = None

    def model_dump(self, **kwargs):
        return {"steps": self.steps}


class FakeClient:
    """A protocol test double. Never counted as a real model evaluation."""
    def __init__(self, report=None, fail=False):
        self.requests = []
        self.interactions = self
        self.report = report or example_report()
        self.fail = fail

    def create(self, **kwargs):
        self.requests.append(copy.deepcopy(kwargs))
        if self.fail:
            raise Exception("sensitive provider exception should never be shown")
        if "response_format" in kwargs:
            return Response(output_text=json.dumps(self.report))
        if len(self.requests) == 1:
            calls = [("get_review_rules", {}), ("get_performance", {}), ("get_character_context", {"character": "Vex"}), ("get_feedback", {"character": "Vex"})]
            return Response([{"type": "function_call", "id": f"call-{i}", "name": name, "arguments": args} for i, (name, args) in enumerate(calls)])
        return Response(output_text="READY")


def test_complete_tool_loop_preserves_evidence_and_validates(tmp_path):
    client = FakeClient()
    e = load_scenario("00_practice")
    run = review(e, "fake-test-key", client=client)
    assert run["status"] == "valid", run
    assert len(run["tool_calls"]) == 4
    second = client.requests[1]
    results = [s for s in second["input"] if s["type"] == "function_result"]
    assert len(results) == 4
    assert json.loads(results[1]["result"][0]["text"])["rows"]
    assert "00_practice" not in json.dumps(client.requests)
    assert "answer_key" not in json.dumps(client.requests)
    saved = save_run(run, tmp_path)
    assert "fake-test-key" not in saved.read_text()
    assert json.loads(saved.read_text())["raw_outputs"][-1]["text"]


def calls_for(e):
    return [{"name": name, "arguments": args, "result": dispatch(e, name, args)} for name, args in
            [("get_review_rules", {}), ("get_performance", {}), ("get_character_context", {"character": "Vex"}), ("get_feedback", {"character": "Vex"})]]


@pytest.mark.parametrize("change", ["invented_ref", "outdated_comment", "wrong_character", "missing_tool", "exact_change"])
def test_bad_evidence_and_actions_rejected(change):
    e = load_scenario("00_practice")
    body = example_report()
    calls = calls_for(e)
    if change == "invented_ref": body["priorities"][0]["metric_refs"].append("made-up")
    if change == "outdated_comment": body["priorities"][0]["comment_ids"] = ["C010"]
    if change == "wrong_character": body["priorities"][0]["character"] = "Okoro"
    if change == "missing_tool": calls = calls[:-1]
    if change == "exact_change": body["priorities"][0]["next_step"] = "Reduce cooldown to 7 seconds."
    assert validate_report(Report.model_validate(body), e, calls)


def test_low_sample_cannot_be_investigation():
    e = load_scenario("03_small_sample")
    body = example_report()
    p = body["priorities"][0]
    p.update(character="Quill", metric_refs=[f"stats:3.2:Quill:{g}" for g in ["Low", "Mid", "High"]], comment_ids=[], context_refs=[])
    assert any("insufficient" in error for error in validate_report(Report.model_validate(body), e, calls_for(e)))


def test_failure_does_not_substitute_baseline_or_expose_exception():
    run = review(load_scenario(), "fake-test-key", client=FakeClient(fail=True))
    assert run["status"] == "error" and run["report"] is None
    assert "sensitive provider" not in json.dumps(run)


def test_tool_limit_stops_unbounded_requests():
    run = review(load_scenario(), "fake-test-key", client=FakeClient(), max_calls=1)
    assert run["status"] == "error" and "limit" in run["error"]


def test_unknown_tools_and_arbitrary_paths_rejected():
    e = load_scenario()
    with pytest.raises(DataError): dispatch(e, "read_file", {"path": "/etc/passwd"})
    with pytest.raises(DataError): dispatch(e, "get_performance", {"path": "evaluation/answer_key.json"})
