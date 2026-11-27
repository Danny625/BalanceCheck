"""Run locally with: streamlit run app.py."""
import json
import os
from hashlib import sha256

import pandas as pd
import streamlit as st
from dotenv import dotenv_values

from agent import DEFAULT_MODEL, check_connection, report_markdown, review, save_local_configuration, save_run
from data import CURRENT, ROOT, DataError, load_scenario, records, scenarios, statistics_baseline, ReviewConfig, review_candidates

st.set_page_config(page_title="BalanceCheck", page_icon="⚖️", layout="wide")


def configured_secret(name):
    # Read on every rerun so saving local setup takes effect without a restart.
    local = dotenv_values(ROOT / ".env.local")
    if local.get(name):
        return local[name]
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
    if "record_missing" in frame and not frame.record_missing.any():
        frame = frame.drop(columns="record_missing")
    columns = [c for c in ["character", "skill_group", "update", "win_rate", "appearances", "pick_rate", "record_missing", "evidence_id"] if c in frame]
    frame = frame[columns].copy()
    for col in ["win_rate", "pick_rate"]:
        if col in frame:
            frame[col] = frame[col].map(lambda x: "Unavailable" if pd.isna(x) else f"{x:.2%}")
    frame = frame.rename(columns={"character": "Character", "skill_group": "Skill group", "update": "Patch", "win_rate": "Win rate", "appearances": "Appearances", "pick_rate": "Pick rate", "evidence_id": "Evidence reference", "record_missing": "Record absent"})
    st.dataframe(frame, hide_index=True, width="stretch")


st.markdown("""<style>
.block-container {max-width:1280px; padding-top:2.4rem;}
h1 {letter-spacing:-.045em; font-weight:750!important;}
h2,h3 {letter-spacing:-.025em;}
[data-testid="stSidebar"] {border-right:1px solid #dae4eb;}
[data-testid="stMetric"] {background:var(--secondary-background-color);border:1px solid #8096a52b;border-radius:12px;padding:16px 20px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px;}
.stButton button[kind="primary"] {border-radius:8px;font-weight:650;}
</style>""", unsafe_allow_html=True)
st.caption("BALANCE OPERATIONS  /  SHARDFALL ARENA")
st.title("BalanceCheck")
st.write("Choose which characters deserve review before the next update.")
st.caption("Patch 3.2 · Synthetic playtest data · Investigations and game changes require designer approval.")

with st.sidebar:
    st.header("Review workspace")
    configured_key = configured_secret("GEMINI_API_KEY") or configured_secret("GOOGLE_API_KEY")
    api_key = configured_key
    model = configured_secret("GEMINI_MODEL") or DEFAULT_MODEL
    local_setup = os.environ.get("BALANCECHECK_LOCAL_SETUP") == "1"
    if not configured_key and local_setup:
        with st.expander("App setup · once per computer", expanded=True):
            api_key = st.text_input("Gemini API key", type="password", key="api_key_input",
                                    help="Enter the full active replacement key. Save below to keep it in an ignored private local file.").strip()
            st.caption("Create a key at [Google AI Studio](https://aistudio.google.com/apikey). The app does not enable billing. Verify your project's free tier before use.")
            key_fingerprint = sha256(api_key.encode()).hexdigest()
            if st.button("Check Gemini connection", disabled=not api_key, key="check_connection"):
                with st.spinner("Checking key and available models…"):
                    result = check_connection(api_key, model)
                st.session_state["connection_check"] = {"key_fingerprint": key_fingerprint, "result": result}
            checked = st.session_state.get("connection_check", {})
            connection = checked.get("result", {}) if checked.get("key_fingerprint") == key_fingerprint else {}
            if connection.get("ok"):
                st.success("Google accepted the key.")
                options = connection["available_models"]
                if options:
                    chosen_model = st.selectbox("Model for this app", options,
                                               index=options.index(model) if model in options else None,
                                               placeholder="Choose a free text model verified in AI Studio", key="setup_model")
                    model = chosen_model or model
                    st.caption("Owner setup only. Choose a text model with tools/structured output and confirm its free-tier availability in AI Studio. Reviewers will not see this setting.")
                    if st.button("Save setup on this computer", key="save_setup", disabled=not chosen_model):
                        try:
                            save_local_configuration(api_key, model)
                        except (ValueError, OSError) as exc:
                            st.error(str(exc) if isinstance(exc, ValueError) else "Could not write the private local setup file. Check folder permissions.")
                        else:
                            st.rerun()
            elif connection:
                st.error(connection["error"])
                st.caption(f"Diagnostic: {connection['exception_type']} · {connection['status_code']}")
    elif not configured_key:
        st.info("The app owner needs to configure model access. Reviewers do not need their own key.")
    mode = st.radio("Input source", ["Sample scenario", "Upload CSVs"])
    sample = st.selectbox("Scenario", scenarios(), disabled=mode == "Upload CSVs", key="scenario")
    stats_upload = feedback_upload = None
    if mode == "Upload CSVs":
        st.caption("Use synthetic data for the bundled Shardfall Arena roster and patches 3.1/3.2. Evidence is sent to the configured Gemini model; do not upload private player data.")
        stats_upload = st.file_uploader("Statistics CSV", type=["csv"])
        feedback_upload = st.file_uploader("Feedback CSV", type=["csv"])

    with st.expander("Review rules", expanded=False):
        st.caption("These settings apply only to your review. Investigation candidates always precede data collection and monitoring.")
        lower = st.number_input("Win-rate lower bound (%)", min_value=0.0, max_value=99.9, value=46.0, step=.5, key="rule_low")
        upper = st.number_input("Win-rate upper bound (%)", min_value=.1, max_value=100.0, value=54.0, step=.5, key="rule_high")
        minimum = st.number_input("Minimum appearances per skill group", min_value=1, max_value=1000000, value=500, step=100, key="rule_sample")
        pick_low = st.number_input("Pick-rate lower watch bound (%)", min_value=0.0, max_value=99.9, value=2.0, step=1.0, key="rule_pick_low")
        pick_high = st.number_input("Pick-rate upper watch bound (%)", min_value=.1, max_value=100.0, value=30.0, step=1.0, key="rule_pick_high")
        ranking = st.selectbox("Investigation ranking", ["Player reach first", "Largest deviation first"], key="rule_ranking")
        scope = st.selectbox("Review scope", ["Standard + observed test queue", "Standard only", "Entire roster"], key="rule_scope")
        st.caption("Standard characters are always expected. Observed test-queue characters are included by default; Entire roster also requires test-queue records even if absent. Patch and skill groups remain fixed for this prototype.")
        def reset_rules():
            defaults = {"rule_low": 46.0, "rule_high": 54.0, "rule_sample": 500,
                        "rule_pick_low": 2.0, "rule_pick_high": 30.0,
                        "rule_ranking": "Player reach first", "rule_scope": "Standard + observed test queue"}
            for key, value in defaults.items():
                st.session_state[key] = value
        st.button("Reset rules to defaults", on_click=reset_rules, key="reset_rules")
    try:
        config = ReviewConfig(lower/100, upper/100, int(minimum), pick_low/100, pick_high/100, ranking, scope)
    except DataError as exc:
        st.error(str(exc))
        st.stop()
    if minimum < 500:
        st.warning("A lower sample minimum admits weaker evidence. Meeting this setting does not establish statistical certainty.")

if mode == "Upload CSVs" and (stats_upload is None or feedback_upload is None):
    st.info("Upload both files to begin. Expand the input format below for required columns.")
    with st.expander("Input format", expanded=True):
        st.code("stats.csv: character,update,skill_group,wins,appearances,picks,eligible_selections\nfeedback.csv: comment_id,author_id,character,update,skill_level,text")
        st.caption("Use UTF-8 CSVs, at most 2 MB and 10,000 rows each. Leave missing counts blank. Use Low, Mid, High skill groups and current update 3.2.")
    st.stop()

try:
    evidence = load_scenario(sample if mode == "Sample scenario" else "00_practice",
                             stats_bytes=stats_upload.getvalue() if stats_upload else None,
                             feedback_bytes=feedback_upload.getvalue() if feedback_upload else None, config=config)
except DataError as exc:
    st.error(str(exc))
    st.stop()

fingerprint = json.dumps({"inputs": evidence.hashes, "configuration": config.snapshot()}, sort_keys=True)
previous = st.session_state.get("last_run")
stale = bool(previous and st.session_state.get("review_fingerprint") != fingerprint)
if stale:
    st.warning("Inputs or review rules changed. The report below belongs to the previous review. Run a new review to apply your changes.")

current = evidence.stats[evidence.stats["update"] == CURRENT]
c1, c2, c3 = st.columns(3)
c1.metric("Characters", current.character.nunique())
c2.metric("Records received", int((~current.record_missing).sum()))
c3.metric("Comments", len(evidence.feedback))
if evidence.warnings:
    st.warning("Incomplete data · this will be a partial review. Missing records are not evidence of ordinary performance.")
    with st.expander("Data gaps to resolve", expanded=True):
        for warning in evidence.warnings:
            st.write("• " + warning)
with st.expander("How priorities are decided", expanded=False):
    st.write(f"Investigation candidates need at least {minimum:,} appearances per affected group and win rates outside {lower:g}–{upper:g}%. Eligible investigations come before data collection and monitoring. Ranking: {ranking.lower()}; the other numerical criterion breaks ties. Player feedback explains possible mechanisms, not causal proof.")
    st.write(f"Pick-rate watch: below {pick_low:g}% or above {pick_high:g}%. Scope: {scope}. Maximum three priorities; a statistical flag is a reason to review, not a prescription to change the game.")
    st.caption("Player reach is the share of the player base in the flagged skill groups: Low 40%, Mid 45%, High 15%. It is a ranking proxy, not a count of players who used the character. Deviation is the largest distance beyond the configured win-rate range.")
with st.expander("Roster coverage before review", expanded=bool(evidence.warnings)):
    st.dataframe(pd.DataFrame(evidence.coverage), hide_index=True, width="stretch")

if not configured_key:
    st.info("Data is ready. The app owner must complete model setup to enable AI reviews. You can inspect inputs and the statistics-only baseline below without a key.")

if st.button("Run AI review", type="primary", disabled=not configured_key, key="run_review"):
    with st.status("Starting review", expanded=True) as status:
        last_message = st.empty()
        with st.spinner("Waiting for the model and checking evidence…", show_time=True):
            run = review(evidence, api_key, model, progress=last_message.write)
        try:
            path = save_run(run)
            run["local_record"] = str(path)
        except OSError:
            run["save_warning"] = "The run could not be saved on this server. Download the JSON record below."
        st.session_state["last_run"] = run
        st.session_state["run_evidence"] = evidence
        st.session_state["review_fingerprint"] = fingerprint
        stale = False
        status.update(label="Review complete" if run["status"] == "valid" else "Review needs attention",
                      state="complete" if run["status"] == "valid" else "error", expanded=False)

run = st.session_state.get("last_run")
if run:
    report_evidence = st.session_state.get("run_evidence", evidence)
    with st.expander("Rules used for this report", expanded=stale):
        used = run.get("configuration", {})
        if used:
            st.table(pd.DataFrame([
                {"Rule": "Expected win-rate range", "Value": f"{used['win_rate_min']:.1%} – {used['win_rate_max']:.1%}"},
                {"Rule": "Minimum appearances per group", "Value": str(used['min_appearances'])},
                {"Rule": "Pick-rate watch range", "Value": f"{used['pick_rate_min']:.1%} – {used['pick_rate_max']:.1%}"},
                {"Rule": "Ranking policy", "Value": used['ranking']},
                {"Rule": "Review scope", "Value": used['scope']},
                {"Rule": "Patch", "Value": used['current_update']},
            ]))
    if run.get("coverage_warnings"):
        st.warning("Partial review: this report has data gaps. Resolve the missing records before treating it as complete.")
    if run["status"] == "valid":
        report = run["report"]
        st.subheader("Previous review" if stale else "Review priorities")
        st.caption("Evidence checks passed. Recommendations still require human judgment.")
        with st.expander("Run details"):
            st.caption(f"Model: {run['model']} · Run: {run['run_id']} · {run['timestamp_utc']}")
        st.write(report["summary"])
        if not report["priorities"]:
            st.success("No priorities selected. See review notes for the agent's assessment.")
        index = report_evidence.metric_index()
        for rank, priority in enumerate(report["priorities"], 1):
            with st.container(border=True):
                st.subheader(f"{rank}. {priority['character']} · {priority['action']}")
                st.caption("Affected groups: " + ", ".join(priority["affected_skill_groups"]))
                st.write(priority["rationale"])
                candidate = next((c for c in review_candidates(report_evidence) if c["character"] == priority["character"]), None)
                if candidate and priority["action"] == "Investigate":
                    st.caption(f"Ranking evidence: flagged skill groups represent {candidate['player_share']:.0%} of the player base · largest deviation {candidate['deviation']*100:.2f} percentage points beyond the expected range · {report_evidence.config.ranking.lower()}")
                metric_table([index[ref] for ref in priority["metric_refs"]])
                st.write("**Uncertainty:** " + priority["uncertainty"])
                st.write("**Next step:** " + priority["next_step"])
                st.caption("Comment IDs: " + (", ".join(priority["comment_ids"]) or "None") + " · Context IDs: " + (", ".join(priority["context_refs"]) or "None"))
        st.subheader("Every character accounted for")
        st.caption("Selected priorities, other statistical flags, and explicit exclusions. This is coverage, not an extended priority list.")
        coverage = pd.DataFrame(run.get("character_review", []))
        if not coverage.empty:
            st.table(coverage[["Character", "Disposition", "Signal", "Reason"]])
        with st.expander("Review notes", expanded=True):
            for note in report["review_notes"]:
                st.write("• " + note)
    else:
        st.error(run.get("error", "The report failed validation and is not accepted as a recommendation."))
        if run.get("diagnostic", {}).get("status_code") == "429":
            st.markdown("[App owner: view active limits in Google AI Studio](https://aistudio.google.com/rate-limit)")
            if run.get("quota"):
                with st.expander("Google quota details"):
                    st.json(run["quota"])
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
    d1.download_button("Download report", report_markdown(run, report_evidence), "balancecheck_report.md", "text/markdown")
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
