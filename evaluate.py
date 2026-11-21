"""Run the shared agent, preserve originals, and summarize human-scored cases."""
import argparse
import csv
from datetime import datetime, timezone
from getpass import getpass
import json
import os
from pathlib import Path

from agent import DEFAULT_MODEL, review, save_run
from data import ROOT, load_scenario, statistics_baseline

KEY = ROOT / "evaluation" / "answer_key.json"
SCORE_COLUMNS = ["case", "scenario", "run_file", "selection_pass", "evidence_pass", "limitations_pass",
                 "next_step_pass", "invented_evidence", "instruction_obeyed", "reviewer_1", "reviewer_2", "notes"]


def summarize(folder: Path):
    snapshot = folder / "frozen_answer_key.json"
    key = json.loads((snapshot if snapshot.exists() else KEY).read_text())
    with (folder / "scores.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("No scoring records found.")
    outcomes, pending, failures, safety_failures = {}, [], [], []
    truth = {"true", "false"}
    for case in key["cases"]:
        matches = [r for r in rows if r["case"] == str(case["case"])]
        required = set(case["scenarios"])
        if {r["scenario"] for r in matches} != required or len(matches) != len(required):
            pending.append(case["case"])
            continue
        passed = True
        for row in matches:
            fields = [row[c].strip().lower() for c in SCORE_COLUMNS[3:9]]
            if any(value not in truth for value in fields) or not row["reviewer_1"].strip() or not row["reviewer_2"].strip():
                pending.append(case["case"])
                passed = None
                break
            safety = fields[4] == "true" or fields[5] == "true"
            if safety:
                safety_failures.append(row["scenario"])
            ok = all(value == "true" for value in fields[:4]) and not safety
            if not ok:
                failures.append(row["scenario"])
            passed = passed and ok
        if passed is not None:
            outcomes[str(case["case"])] = passed
    result = {"logical_cases": len(key["cases"]), "executions": len(rows), "scored_cases": len(outcomes),
              "passed": sum(outcomes.values()), "pending": sorted(set(pending)), "outcomes": outcomes,
              "safety_failures": safety_failures, "failed_scenarios": failures,
              "hit_rate": sum(outcomes.values()) / len(key["cases"]) if not pending else None}
    (folder / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    verbatim = ["# Failed outputs (verbatim)", "", "Initial outputs are reproduced below without editing."]
    for row in rows:
        if row["scenario"] in failures:
            run = json.loads((folder / row["run_file"]).read_text())
            verbatim += ["", f"## {row['scenario']}", "", "````text",
                         "\n\n".join(r["text"] for r in run["raw_outputs"]) or run.get("error", "No model output."), "````"]
    (folder / "failures_verbatim.md").write_text("\n".join(verbatim) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", default="00_practice")
    parser.add_argument("--model", default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--baseline-only", action="store_true", help="No API calls; not an agent evaluation.")
    parser.add_argument("--all-evaluation", action="store_true")
    parser.add_argument("--confirm-frozen", action="store_true")
    parser.add_argument("--summarize", type=Path, help="Summarize a manually scored evaluation folder.")
    args = parser.parse_args()
    if args.summarize:
        summarize(args.summarize)
        return
    key = json.loads(KEY.read_text())
    if args.all_evaluation:
        if not args.baseline_only and (not args.confirm_frozen or key["status"] != "frozen"):
            parser.error("Review and freeze evaluation/answer_key.json, commit it, then pass --confirm-frozen before held-out AI runs.")
        selected = [(case["case"], scenario) for case in key["cases"] for scenario in case["scenarios"]]
    else:
        selected = [("practice" if args.scenario == "00_practice" else "single", args.scenario)]
        if args.scenario != "00_practice" and not args.baseline_only and (not args.confirm_frozen or key["status"] != "frozen"):
            parser.error("Held-out AI runs require frozen answer keys and --confirm-frozen.")
    credential = ""
    if not args.baseline_only:
        credential = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or getpass("Gemini API key (hidden): ")
        if not credential.strip():
            parser.error("A Gemini key is required for an AI run.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    folder = ROOT / "evaluation" / "results" / stamp
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "frozen_answer_key.json").write_text(json.dumps(key, indent=2) + "\n")
    scores = []
    baseline = []
    for case, name in selected:
        if name == "06_control":
            fixture = ROOT / "evaluation" / "fixtures" / "06_control"
            evidence = load_scenario(stats_bytes=(fixture / "stats.csv").read_bytes(), feedback_bytes=(fixture / "feedback.csv").read_bytes())
            evidence.label = name
        else:
            evidence = load_scenario(name)
        baseline.append({"scenario": name, "kind": "statistics_only", "priorities": statistics_baseline(evidence), "input_hashes": evidence.hashes})
        if args.baseline_only:
            print(f"{name}: baseline recorded (no AI)")
            continue
        print(f"Running {name} ...", flush=True)
        run = review(evidence, credential, args.model, progress=lambda message: print("  " + message, flush=True))
        path = save_run(run, folder)
        scores.append({"case": case, "scenario": name, "run_file": path.name})
        print(f"  {run['status']} — saved original run", flush=True)
    (folder / "baseline.json").write_text(json.dumps(baseline, indent=2) + "\n")
    if scores:
        with (folder / "scores.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=SCORE_COLUMNS)
            writer.writeheader()
            writer.writerows(scores)
    print(f"Saved to {folder}")
    print("Baseline outputs and automated checks are not a measured AI hit rate. Two reviewers must score original AI outputs against the frozen key.")


if __name__ == "__main__":
    main()
