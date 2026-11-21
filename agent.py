"""Bounded Gemini tool loop, report validation, and reproducible run records."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Literal
from uuid import uuid4

from dotenv import load_dotenv, set_key
from pydantic import BaseModel, ConfigDict, Field

from data import CURRENT, ROOT, DataError, Evidence, records, statistics_baseline

load_dotenv(ROOT / ".env.local")
load_dotenv(ROOT / ".env")
DEFAULT_MODEL = "gemini-3.5-flash-lite"


class ReviewLimitError(RuntimeError):
    """Only locally generated, safe-to-display loop-limit messages."""


def save_local_configuration(api_key: str, model: str, *, root: Path = ROOT) -> None:
    """Persist only after the owner's explicit Save button; never return the secret."""
    if not api_key or any(c.isspace() for c in api_key):
        raise ValueError("Use the complete key without spaces, newlines, or quotes.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise ValueError("Choose a valid model identifier.")
    target = root / ".env.local"
    if target.is_symlink():
        raise ValueError("Refusing to save credentials through a symbolic link.")
    try:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".env.local"], cwd=root,
                                 capture_output=True, check=False).returncode == 0
    except OSError:
        tracked = False
    if tracked:
        raise ValueError(".env.local is tracked by Git. Remove it from tracking before saving a credential.")
    ignore = root / ".gitignore"
    if not ignore.exists() or not {".env.local", ".env.*"}.intersection(ignore.read_text().splitlines()):
        raise ValueError("Add .env.local to .gitignore before saving the key.")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=root, prefix=".key-setup-", delete=False) as stream:
            temporary = Path(stream.name)
            if target.exists():
                stream.write(target.read_text())
        set_key(temporary, "GEMINI_API_KEY", api_key, quote_mode="always")
        set_key(temporary, "GEMINI_MODEL", model, quote_mode="always")
        temporary.chmod(0o600)
        os.replace(temporary, target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class Priority(BaseModel):
    model_config = ConfigDict(extra="forbid")
    character: str
    affected_skill_groups: list[str] = Field(min_length=1)
    action: Literal["Investigate", "Monitor", "Collect data"]
    metric_refs: list[str] = Field(min_length=1)
    comment_ids: list[str]
    context_refs: list[str]
    rationale: str = Field(min_length=1)
    uncertainty: str = Field(min_length=1)
    next_step: str = Field(min_length=1)


class Report(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1)
    priorities: list[Priority] = Field(max_length=3)
    review_notes: list[str]


def tool_declarations() -> list[dict]:
    specs = [
        ("get_review_rules", "Get the authoritative review guide, thresholds, and skill-group player shares.", None),
        ("get_performance", "Get Python-calculated statistics, evidence IDs, historical context and missing/sample flags. Omit character to review all characters.", False),
        ("get_character_context", "Get character mechanics, ability IDs, patch change IDs, and unapproved backlog proposals.", True),
        ("get_feedback", "Get untrusted player comments with IDs and duplicate/outdated flags.", True),
    ]
    result = []
    for name, description, required in specs:
        parameters = {"type": "object", "properties": {}}
        if required is not None:
            parameters["properties"]["character"] = {"type": "string", "description": "Exact character name from performance evidence."}
            if required:
                parameters["required"] = ["character"]
        result.append({"type": "function", "name": name, "description": description, "parameters": parameters})
    return result


def dispatch(evidence: Evidence, name: str, arguments: dict) -> dict:
    allowed = {d["name"] for d in tool_declarations()}
    if name not in allowed or not isinstance(arguments, dict):
        raise DataError("Unknown tool or invalid tool arguments.")
    permitted = set() if name == "get_review_rules" else {"character"}
    if set(arguments) - permitted:
        raise DataError("Unexpected tool arguments.")
    if "character" in arguments and not isinstance(arguments["character"], str):
        raise DataError("Character must be a string.")
    if name in {"get_feedback", "get_character_context"} and "character" not in arguments:
        raise DataError("This tool requires a character.")
    return getattr(evidence, name)(**arguments)


def validate_report(report: Report, evidence: Evidence, calls: list[dict]) -> list[str]:
    errors = []
    metrics = evidence.metric_index()
    comments = {r["comment_id"]: r for r in records(evidence.feedback)}
    contexts = {}
    for table, key in [("abilities", "ability_id"), ("patch_notes", "change_id"), ("design_backlog", "backlog_id")]:
        contexts.update({r[key]: r for r in records(evidence.tables[table])})
    successful = [c for c in calls if "error" not in c["result"]]
    names = {c["name"] for c in successful}
    if not {"get_review_rules", "get_performance"} <= names or not any(c["name"] == "get_performance" and not c["arguments"] for c in successful):
        errors.append("Rules and unfiltered performance must be retrieved.")
    characters_seen = set()
    for priority in report.priorities:
        who = priority.character
        if who not in evidence.characters or who in characters_seen:
            errors.append(f"Unknown or repeated character: {who}.")
        characters_seen.add(who)
        if len(priority.affected_skill_groups) != len(set(priority.affected_skill_groups)):
            errors.append(f"Repeated skill group for {who}.")
        for name in ["get_character_context", "get_feedback"]:
            if not any(c["name"] == name and c["arguments"].get("character") == who for c in successful):
                errors.append(f"{name} was not retrieved for {who}.")
        refs = [metrics.get(ref) for ref in priority.metric_refs]
        current = [r for r in refs if r and r["update"] == CURRENT]
        if any(not r or r["character"] != who for r in refs):
            errors.append(f"Invalid metric reference for {who}.")
        groups = set(priority.affected_skill_groups)
        affected = [r for r in current if r["skill_group"] in groups]
        if not groups <= {r["skill_group"] for r in current}:
            errors.append(f"Current metric references must cover every affected group for {who}.")
        if priority.action == "Investigate" and any(not r["sample_sufficient"] or r["balance_flag"] not in ["Strong", "Weak"] for r in affected):
            errors.append(f"Investigation has insufficient or ordinary performance evidence for {who}.")
        if priority.action == "Collect data" and any(r["sample_sufficient"] and r["pick_rate"] is not None for r in affected):
            errors.append(f"Collect data must identify groups with missing counts or insufficient sample for {who}.")
        if priority.action == "Monitor" and any(not r["sample_sufficient"] for r in affected):
            errors.append(f"Low/missing samples require Collect data for {who}.")
        duplicate_roots = set()
        for cid in priority.comment_ids:
            comment = comments.get(cid)
            if not comment or comment["character"] != who or comment["outdated"] or comment["suspicious"]:
                errors.append(f"Invalid current supporting comment: {cid}.")
            elif comment["duplicate_of"] or cid in duplicate_roots:
                errors.append(f"Duplicate supporting comment: {cid}.")
            duplicate_roots.add(cid)
        for ref in priority.context_refs:
            item = contexts.get(ref)
            if not item or item["character"] not in [who, "All"]:
                errors.append(f"Invalid context reference: {ref}.")
        prose = " ".join([priority.rationale, priority.uncertainty, priority.next_step])
        if re.search(r"\d+(?:\.\d+)?\s*%", prose):
            errors.append(f"Keep numeric percentages in calculated evidence, not prose, for {who}.")
        if re.search(r"(?:reduce|increase|buff|nerf|set|revert|lower|raise).{0,60}\b\d+\s*(?:%|seconds?|damage|healing|s\b)", prose, re.I):
            errors.append(f"Exact game changes are prohibited for {who}.")
    return errors


def plain(value):
    """Convert SDK/Pydantic objects without dropping opaque history fields."""
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError("Unexpected SDK response object.")


def _api_error(exc: Exception) -> str:
    # Never display raw provider exceptions: they can include credentials or request content.
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    chain = []
    cause = exc
    while cause is not None and len(chain) < 5:
        chain.append(str(cause).lower())
        cause = cause.__cause__
    message = " ".join(chain)
    if any(s in message for s in ["certificate_verify_failed", "certificate verify failed"]):
        return "Python could not verify Google's HTTPS certificate. This is a local certificate/trust setup issue, not evidence that your key is wrong."
    if any(s in message for s in ["api_key_invalid", "api key not valid"]):
        return "Gemini says the API key is invalid. Use the replacement Gemini API key from AI Studio."
    if "api_key_service_blocked" in message or "api_key_http_referrer_blocked" in message:
        return "The key's API or website restrictions block this Python app. Review its Gemini API access settings in AI Studio."
    if isinstance(exc, (TypeError, AttributeError)):
        return "The Gemini SDK could not construct or read the request. This is an application compatibility issue; the recorded diagnostic identifies the exception type."
    if "timeout" in type(exc).__name__.lower() or "timed out" in message:
        return "Gemini did not answer before the request timeout. Use Check Gemini connection to verify access/model availability, then retry."
    if any(s in message for s in ["name or service not known", "nodename nor servname", "name resolution"]):
        return "The app could not resolve Google's API address. This is a network/DNS issue, not evidence that the key is wrong."
    if str(code) in ["401", "403"]:
        return "Gemini rejected access. Check the replacement key and project permissions in AI Studio."
    if str(code) == "429":
        return "Gemini quota/rate limit reached. Check free-tier availability in AI Studio and try later. No baseline was substituted."
    if str(code) in ["500", "502", "503", "504"]:
        return "Google's model service returned a server error or gateway timeout. This is not a confirmed key/billing error. Try again later or ask the app owner to test another available model."
    if str(code) == "404":
        return "This model is unavailable for the project. Choose an accessible model in AI Studio and update the model field."
    if str(code) == "400":
        return "Gemini rejected the request. Check that the selected model supports tools and structured outputs; preserve this failed run for review."
    return "Gemini request failed or timed out. Check connectivity, key access, and model availability; then retry."


def check_connection(api_key: str, model: str = DEFAULT_MODEL) -> dict:
    """Read model metadata only; no text generation or review is requested."""
    from google import genai
    client = None
    try:
        client = genai.Client(api_key=api_key, http_options={"timeout": 20000, "retry_options": {"attempts": 1}})
        available = [m.name.removeprefix("models/") for m in client.models.list() if m.name]
        return {"ok": True, "selected_model": model, "selected_model_listed": model in available,
                "available_models": available}
    except Exception as exc:
        return {"ok": False, "error": _api_error(exc), "exception_type": type(exc).__name__,
                "status_code": str(getattr(exc, "status_code", None) or getattr(exc, "code", None) or "unavailable")}
    finally:
        if client is not None:
            client.close()


def review(evidence: Evidence, api_key: str, model: str = DEFAULT_MODEL, *, client=None,
           progress=None, max_rounds: int = 8, max_calls: int = 24) -> dict:
    if not api_key.strip():
        raise ValueError("Enter a Gemini API key in the sidebar before running the AI review.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
        raise ValueError("Use a model identifier, not a URL.")
    instructions = (ROOT / "instructions.md").read_text()
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        commit, dirty = None, None
    code_hashes = {p: sha256((ROOT / p).read_bytes()).hexdigest() for p in ["agent.py", "data.py", "app.py"]}
    run = {"run_id": uuid4().hex, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
           "kind": "gemini_agent", "scenario": evidence.label, "model": model, "git_commit": commit,
           "working_tree_dirty": dirty, "code_hashes": code_hashes,
           "instructions_sha256": sha256(instructions.encode()).hexdigest(), "input_hashes": evidence.hashes,
           "status": "running", "tool_calls": [], "raw_outputs": [], "report": None,
           "validation_errors": [], "baseline": statistics_baseline(evidence)}
    current_characters = sorted(set(evidence.stats.loc[evidence.stats["update"] == CURRENT, "character"]))
    required_calls = [("get_review_rules", {}), ("get_performance", {})]
    required_calls += [(name, {"character": character}) for character in current_characters
                       for name in ["get_character_context", "get_feedback"]]
    history = [{"type": "user_input", "content": [{"type": "text", "text": "Review the supplied scenario for the current update. Retrieve rules and all performance first, then context and feedback for every character with current records. After completing those lookups, say READY; the next turn requests the structured report."}]}]
    owned_client = client is None
    try:
        if owned_client:
            from google import genai
            client = genai.Client(api_key=api_key, http_options={"timeout": 60000, "retry_options": {"attempts": 1}})
        ready = False
        for turn in range(max_rounds):
            if progress:
                progress(f"Gathering evidence · round {turn + 1}")
            response = client.interactions.create(model=model, input=history, system_instruction=instructions,
                                                 tools=tool_declarations(), store=False, timeout=60,
                                                 generation_config={"max_output_tokens": 4096})
            dumped = plain(response)
            steps = dumped.get("steps", [])
            history.extend(steps)
            text = getattr(response, "output_text", "") or ""
            if text:
                run["raw_outputs"].append({"phase": "gather", "text": text})
            function_calls = [s for s in steps if s.get("type") == "function_call"]
            if not function_calls:
                missing = [{"name": name, "arguments": args} for name, args in required_calls
                           if not any(c["name"] == name and c["arguments"] == args and "error" not in c["result"] for c in run["tool_calls"])]
                if not missing:
                    ready = True
                    break
                history.append({"type": "user_input", "content": [{"type": "text", "text": "Required evidence is still missing. Request these tools before finishing: " + json.dumps(missing)}]})
                continue
            for call in function_calls:
                if len(run["tool_calls"]) >= max_calls:
                    raise ReviewLimitError("Tool-call limit reached. No report was accepted.")
                name, args = call.get("name", ""), call.get("arguments", {})
                try:
                    result = dispatch(evidence, name, args)
                except DataError as exc:
                    result = {"error": str(exc)}
                run["tool_calls"].append({"name": name, "arguments": args, "result": result})
                if progress:
                    progress(f"Retrieved {name}" + (f" · {args['character']}" if isinstance(args, dict) and args.get("character") else ""))
                history.append({"type": "function_result", "name": name, "call_id": call["id"],
                                "result": [{"type": "text", "text": json.dumps(result, allow_nan=False)}]})
        if not ready:
            raise ReviewLimitError("Evidence-gathering limit reached. No report was accepted.")
        if progress:
            progress("Writing the evidence-backed report")
        history.append({"type": "user_input", "content": [{"type": "text", "text": "Return the final report in the supplied JSON schema, using only retrieved evidence. Do not add numerical rate/count claims in prose; exact values will be displayed from metric_refs."}]})
        final = client.interactions.create(model=model, input=history, system_instruction=instructions,
                                           store=False, timeout=60, generation_config={"max_output_tokens": 8192},
                                           response_format={"type": "text", "mime_type": "application/json", "schema": Report.model_json_schema()})
        raw = getattr(final, "output_text", "") or ""
        run["raw_outputs"].append({"phase": "final", "text": raw})
        if hasattr(final, "usage") and final.usage is not None:
            run["final_request_usage"] = plain(final.usage)
        try:
            report = Report.model_validate_json(raw)
            run["validation_errors"] = validate_report(report, evidence, run["tool_calls"])
            run["report"] = report.model_dump()
        except ValueError:
            run["validation_errors"] = ["Gemini did not return a report matching the required JSON schema."]
        run["status"] = "invalid" if run["validation_errors"] else "valid"
    except ReviewLimitError as exc:
        run["status"], run["error"] = "error", str(exc)
    except Exception as exc:
        run["status"], run["error"] = "error", _api_error(exc)
        run["diagnostic"] = {"exception_type": type(exc).__name__,
                             "status_code": str(getattr(exc, "status_code", None) or getattr(exc, "code", None) or "unavailable"),
                             "cause_type": type(exc.__cause__).__name__ if exc.__cause__ else None}
    finally:
        if owned_client and client is not None:
            try:
                client.close()
            except Exception:
                pass
    # Defensive redaction if an unexpected provider response happens to echo the credential.
    serialized = json.dumps(run, ensure_ascii=False, allow_nan=False)
    return json.loads(serialized.replace(api_key, "[REDACTED]"))


def save_run(run: dict, folder: Path | None = None) -> Path:
    target = folder if folder is not None else ROOT / "runs"
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{run['timestamp_utc'].replace(':', '-')}_{run['run_id']}.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(run, stream, indent=2, ensure_ascii=False, allow_nan=False)
    return path


def report_markdown(run: dict, evidence: Evidence) -> str:
    lines = ["# BalanceCheck", "", "SYNTHETIC DATA · Advisory only · Designer approval required", "",
             f"Model: {run['model']} | Run: {run['run_id']} | Status: {run['status']}", ""]
    if run["status"] != "valid":
        return "\n".join(lines + [run.get("error", "Report failed validation."), *run["validation_errors"]])
    report = run["report"]
    lines.append(report["summary"])
    index = evidence.metric_index()
    for rank, p in enumerate(report["priorities"], 1):
        lines += ["", f"## {rank}. {p['character']} — {p['action']}", "", p["rationale"], ""]
        for ref in p["metric_refs"]:
            r = index[ref]
            rate = f"{r['win_rate']:.2%}" if r["win_rate"] is not None else "unavailable"
            pick = f"{r['pick_rate']:.2%}" if r["pick_rate"] is not None else "unavailable"
            lines.append(f"- {ref}: wins={r['wins']}, appearances={r['appearances']}, win rate={rate}, pick rate={pick}")
        lines += ["", f"Uncertainty: {p['uncertainty']}", "", f"Next step: {p['next_step']}", "",
                  f"Comment IDs: {', '.join(p['comment_ids']) or 'None'}", "",
                  f"Context IDs: {', '.join(p['context_refs']) or 'None'}"]
    lines += ["", "## Review notes", "", *[f"- {note}" for note in report["review_notes"]]]
    return "\n".join(lines)
