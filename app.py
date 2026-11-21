"""Run locally with: streamlit run app.py."""
import json
import os

import pandas as pd
import streamlit as st

from agent import DEFAULT_MODEL, check_connection, report_markdown, review, save_run
from data import CURRENT, ROOT, DataError, load_scenario, records, scenarios, statistics_baseline

st.set_page_config(page_title="BalanceCheck", page_icon="⚖️", layout="wide")


def configured_secret(name):
    if os.environ.get(name):
        return os.environ[name]
    try:
        return st.secrets.get(name, "")
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ""


def metric_table(rows):
    frame = pd.DataFrame(rows)
    if frame.empty:
        return
    for col in ["win_rate", "pick_rate"]:
        if col in frame:
            frame[col] = frame[col].map(lambda x: "Unavailable" if pd.isna(x) else f"{x:.2%}")
    st.dataframe(frame, hide_index=True, width="stretch")


st.title("BalanceCheck")
st.write("Choose which characters deserve review before the next update.")
st.caption("Shardfall Arena · Synthetic data · Current update 3.2 · All investigations and game changes require designer approval.")

with st.sidebar:
    st.header("Model access")
    configured_key = configured_secret("GEMINI_API_KEY") or configured_secret("GOOGLE_API_KEY")
    if configured_key:
        st.success("A Gemini key is configured on this server.")
    supplied_key = st.text_input("Gemini API key", type="password", key="api_key_input",
                                 help="Used only for this session. Never included in reports or committed to GitHub. Leave blank when a server key is configured.")
    api_key = supplied_key.strip() or configured_key
    st.caption("Create a key at [Google AI Studio](https://aistudio.google.com/apikey). Free-tier quotas depend on your Google project. This app does not enable billing or guarantee zero cost on a billed project.")
    with st.expander("Model settings"):
        model = st.text_input("Gemini model", value=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
        st.caption("Use a model your project can access that supports function calling and structured output.")
    if st.button("Check Gemini connection", disabled=not api_key, key="check_connection"):
        with st.spinner("Checking available models…"):
            connection = check_connection(api_key, model)
        try:
            (ROOT / "runs").mkdir(exist_ok=True)
            (ROOT / "runs" / "connection_check.json").write_text(json.dumps(connection, indent=2))
        except OSError:
            pass
        if connection["ok"]:
            st.success("Google accepted the key and returned model metadata.")
            if not connection["selected_model_listed"]:
                st.warning("The selected model is not listed for this key. Choose an available model under Model settings; verify its free-tier pricing in AI Studio.")
            with st.expander("Available models", expanded=not connection["selected_model_listed"]):
                st.write(connection["available_models"])
        else:
            st.error(connection["error"])
            st.caption(f"Diagnostic: {connection['exception_type']} · {connection['status_code']}")
    mode = st.radio("Input source", ["Sample scenario", "Upload CSVs"])
    sample = st.selectbox("Scenario", scenarios(), disabled=mode == "Upload CSVs", key="scenario")
    stats_upload = feedback_upload = None
    if mode == "Upload CSVs":
        st.caption("Uploads use the bundled Shardfall Arena roster and guide. Custom games are outside this prototype.")
        stats_upload = st.file_uploader("Statistics CSV", type=["csv"])
        feedback_upload = st.file_uploader("Feedback CSV", type=["csv"])
    st.caption("Practice: 00_practice. Evaluation: freeze answer keys before running the other scenarios.")

if mode == "Upload CSVs" and (stats_upload is None or feedback_upload is None):
    st.info("Upload both files to begin. Expand the input format below for required columns.")
    with st.expander("Input format", expanded=True):
        st.code("stats.csv: character,update,skill_group,wins,appearances,picks,eligible_selections\nfeedback.csv: comment_id,author_id,character,update,skill_level,text")
        st.caption("Use UTF-8 CSVs, at most 2 MB and 10,000 rows each. Leave missing counts blank. Use Low, Mid, High skill groups and current update 3.2.")
    st.stop()

try:
    evidence = load_scenario(sample if mode == "Sample scenario" else "00_practice",
                             stats_bytes=stats_upload.getvalue() if stats_upload else None,
                             feedback_bytes=feedback_upload.getvalue() if feedback_upload else None)
except DataError as exc:
    st.error(str(exc))
    st.stop()

fingerprint = json.dumps(evidence.hashes, sort_keys=True)
if st.session_state.get("input_fingerprint") != fingerprint:
    st.session_state.pop("last_run", None)
    st.session_state["input_fingerprint"] = fingerprint

current = evidence.stats[evidence.stats["update"] == CURRENT]
c1, c2, c3 = st.columns(3)
c1.metric("Characters with current records", current.character.nunique())
c2.metric("Current performance records", len(current))
c3.metric("Player comments", len(evidence.feedback))
for warning in evidence.warnings:
    st.warning(warning)

if not api_key:
    st.info("Data is ready. Enter your Gemini key in the sidebar to enable the AI review. You can inspect inputs and the statistics-only baseline below without a key.")

key_status = json.loads((ROOT / "evaluation" / "answer_key.json").read_text())["status"]
held_out_locked = mode == "Sample scenario" and sample != "00_practice" and key_status != "frozen"
if held_out_locked:
    st.warning("This is a held-out evaluation scenario. The team must review, freeze, and commit evaluation/answer_key.json before running the AI on it. You can still inspect its inputs and baseline.")

if st.button("Run AI review", type="primary", disabled=not api_key or held_out_locked, key="run_review"):
    with st.status("Starting review", expanded=True) as status:
        last_message = st.empty()
        run = review(evidence, api_key, model, progress=last_message.write)
        try:
            path = save_run(run)
            run["local_record"] = str(path)
        except OSError:
            run["save_warning"] = "The run could not be saved on this server. Download the JSON record below."
        st.session_state["last_run"] = run
        status.update(label="Review complete" if run["status"] == "valid" else "Review needs attention",
                      state="complete" if run["status"] == "valid" else "error", expanded=False)

run = st.session_state.get("last_run")
if run:
    if run["status"] == "valid":
        report = run["report"]
        st.subheader("Review report")
        st.caption(f"Model: {run['model']} · Run: {run['run_id']} · {run['timestamp_utc']}")
        st.write(report["summary"])
        if not report["priorities"]:
            st.success("No priorities selected. See review notes for the agent's assessment.")
        index = evidence.metric_index()
        for rank, priority in enumerate(report["priorities"], 1):
            with st.container(border=True):
                st.subheader(f"{rank}. {priority['character']} · {priority['action']}")
                st.caption("Affected groups: " + ", ".join(priority["affected_skill_groups"]))
                st.write(priority["rationale"])
                metric_table([index[ref] for ref in priority["metric_refs"]])
                st.write("**Uncertainty:** " + priority["uncertainty"])
                st.write("**Next step:** " + priority["next_step"])
                st.caption("Comment IDs: " + (", ".join(priority["comment_ids"]) or "None") + " · Context IDs: " + (", ".join(priority["context_refs"]) or "None"))
        with st.expander("Review notes", expanded=True):
            for note in report["review_notes"]:
                st.write("• " + note)
    else:
        st.error(run.get("error", "The report failed validation and is not accepted as a recommendation."))
        if run.get("diagnostic"):
            st.caption("Connection diagnostic: " + json.dumps(run["diagnostic"]))
        for error in run["validation_errors"]:
            st.write("• " + error)
        with st.expander("Original model output (unaccepted)"):
            for output in run["raw_outputs"]:
                st.code(output["text"], language="text")
    if run.get("save_warning"):
        st.warning(run["save_warning"])
    d1, d2 = st.columns(2)
    d1.download_button("Download report", report_markdown(run, evidence), "balancecheck_report.md", "text/markdown")
    exported = {k: v for k, v in run.items() if k != "local_record"}
    d2.download_button("Download full run record", json.dumps(exported, indent=2), "balancecheck_run.json", "application/json")
    with st.expander("Evidence retrieval log"):
        st.caption("These are tool requests and their results, not private model reasoning.")
        for i, call in enumerate(run["tool_calls"], 1):
            st.write(f"{i}. {call['name']}")
            st.json(call)

with st.expander("Statistics-only baseline · no AI"):
    st.caption("Deterministic comparison using performance, sample eligibility, and player shares. Does not use comments, abilities, patch notes, or the model. This is not an AI review.")
    baseline = statistics_baseline(evidence)
    if baseline:
        st.dataframe(pd.DataFrame(baseline), hide_index=True, width="stretch")
    else:
        st.write("No statistical candidates under the guide's rules.")

with st.expander("Inspect input evidence"):
    performance, feedback, guide, context = st.tabs(["Performance", "Feedback", "Guide", "Character context"])
    with performance:
        metric_table(records(evidence.stats))
    with feedback:
        st.dataframe(evidence.feedback, hide_index=True, width="stretch")
    with guide:
        st.markdown(evidence.guide)
    with context:
        who = st.selectbox("Character", evidence.characters)
        st.json(evidence.get_character_context(who))
