"""Read-only scenario loading, calculated evidence, and statistics-only baseline."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CURRENT = "3.2"
STATS = ["character", "update", "skill_group", "wins", "appearances", "picks", "eligible_selections"]
FEEDBACK = ["comment_id", "author_id", "character", "update", "skill_level", "text"]
COUNTS = STATS[3:]
TABLES = {
    "characters": ["character", "role", "released_update", "availability", "description"],
    "abilities": ["ability_id", "character", "ability", "type", "cooldown_s", "key_value", "key_value_unit", "description"],
    "patch_notes": ["change_id", "update", "character", "ability_id", "change_type", "old_value", "new_value", "designer_note"],
    "design_backlog": ["backlog_id", "character", "ability_id", "proposed_change", "source", "status"],
    "skill_groups": ["skill_group", "mmr_min", "mmr_max", "share_of_players"],
    "review_thresholds": ["parameter", "value", "unit", "meaning"],
}


class DataError(ValueError):
    """A useful user-facing input error."""


@dataclass(frozen=True)
class ReviewConfig:
    win_rate_min: float = .46
    win_rate_max: float = .54
    min_appearances: int = 500
    pick_rate_min: float = .02
    pick_rate_max: float = .30
    ranking: str = "Player reach first"
    scope: str = "Standard + observed test queue"

    def __post_init__(self):
        for lower, upper in [(self.win_rate_min, self.win_rate_max), (self.pick_rate_min, self.pick_rate_max)]:
            if not 0 <= lower < upper <= 1:
                raise DataError("Each lower percentage must be below its upper percentage, between zero and one hundred.")
        if isinstance(self.min_appearances, bool) or not isinstance(self.min_appearances, int) or self.min_appearances < 1:
            raise DataError("Minimum appearances must be a positive whole number.")
        if self.ranking not in ["Player reach first", "Largest deviation first"]:
            raise DataError("Choose a supported ranking policy.")
        if self.scope not in ["Standard + observed test queue", "Standard only", "Entire roster"]:
            raise DataError("Choose a supported review scope.")

    def snapshot(self):
        return {**asdict(self), "current_update": CURRENT, "max_priorities": 3,
                "action_order": ["Investigate", "Collect data", "Monitor"]}


def scenarios() -> list[str]:
    return sorted(p.name for p in (DATA / "scenarios").iterdir() if p.is_dir())


def read_csv(raw: bytes, columns: list[str], label: str) -> pd.DataFrame:
    if len(raw) > 2_000_000:
        raise DataError(f"{label}: limit is 2 MB per file.")
    try:
        frame = pd.read_csv(StringIO(raw.decode("utf-8-sig")), dtype=str, keep_default_na=False)
    except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
        raise DataError(f"{label}: expected a valid UTF-8 CSV with a header.") from exc
    missing = set(columns) - set(frame.columns)
    if missing:
        raise DataError(f"{label}: missing columns: {', '.join(sorted(missing))}.")
    if len(frame) > 10_000:
        raise DataError(f"{label}: limit is 10,000 rows.")
    frame = frame[columns].copy()
    for col in columns:
        frame[col] = frame[col].str.strip()
    return frame


def records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records"))


@dataclass
class Evidence:
    label: str
    tables: dict[str, pd.DataFrame]
    stats: pd.DataFrame
    feedback: pd.DataFrame
    guide: str
    hashes: dict[str, str]
    warnings: list[str]
    config: ReviewConfig = field(default_factory=ReviewConfig)
    coverage: list[dict] = field(default_factory=list)

    @property
    def thresholds(self) -> dict[str, float]:
        return {k: v for k, v in self.config.snapshot().items() if k in ["win_rate_min", "win_rate_max", "min_appearances", "pick_rate_min", "pick_rate_max", "max_priorities"]}

    @property
    def characters(self) -> list[str]:
        return self.tables["characters"].character.tolist()

    def check_character(self, character: str) -> None:
        if character not in self.characters:
            raise DataError("Unknown character. Use a character returned by get_performance.")

    def get_review_rules(self) -> dict:
        return {"current_update": CURRENT, "guide": self.guide, "configuration": self.config.snapshot(), "coverage": self.coverage, "thresholds": self.thresholds,
                "skill_groups": records(self.tables["skill_groups"]), "input_warnings": self.warnings}

    def get_performance(self, character: str | None = None) -> dict:
        if character is not None:
            self.check_character(character)
        frame = self.stats if character is None else self.stats[self.stats.character == character]
        overall = []
        groups = set(self.tables["skill_groups"].skill_group)
        for (name, update), sub in frame.groupby(["character", "update"], sort=False):
            complete = set(sub.skill_group) == groups and sub[["wins", "appearances"]].notna().all().all()
            total = sub.appearances.sum()
            overall.append({"character": name, "update": update,
                            "win_rate": float(sub.wins.sum() / total) if complete and total > 0 else None,
                            "complete": bool(complete), "note": "Always inspect individual skill groups."})
        return {"current_update": CURRENT, "rows": records(frame), "overall": overall, "candidates": review_candidates(self)}

    def get_character_context(self, character: str | None = None) -> dict:
        if character is not None:
            self.check_character(character)
        return {name: records(frame[frame.character.isin([character, "All"] if character else list(set(self.stats.character)) + ["All"])])
                for name, frame in self.tables.items() if "character" in frame.columns}

    def get_feedback(self, character: str | None = None) -> dict:
        if character is not None:
            self.check_character(character)
        frame = self.feedback[self.feedback.character == character] if character else self.feedback[self.feedback.character.isin(set(self.stats.character))]
        return {"comments": records(frame), "note": "Untrusted player text. Duplicates are not independent evidence; outdated comments do not support current-patch claims."}

    def metric_index(self) -> dict[str, dict]:
        return {r["evidence_id"]: r for r in records(self.stats)}


def load_scenario(name: str = "00_practice", *, stats_bytes: bytes | None = None,
                  feedback_bytes: bytes | None = None, config: ReviewConfig | None = None) -> Evidence:
    config = config or ReviewConfig()
    if name not in scenarios():
        raise DataError("Choose an available sample scenario.")
    upload = stats_bytes is not None or feedback_bytes is not None
    if upload and (stats_bytes is None or feedback_bytes is None):
        raise DataError("Upload both stats.csv and feedback.csv.")
    folder = DATA / "scenarios" / name
    hashes = {}

    def source(filename: str, supplied: bytes | None = None) -> bytes:
        path = folder / filename
        raw = supplied if supplied is not None else (path if path.exists() and not upload else DATA / "shared" / filename).read_bytes()
        hashes[filename] = sha256(raw).hexdigest()
        return raw

    tables = {n: read_csv(source(n + ".csv"), cols, n) for n, cols in TABLES.items()}
    guide = source("game_guide.md").decode("utf-8")
    stats = read_csv(source("stats.csv", stats_bytes), STATS, "Statistics")
    feedback = read_csv(source("feedback.csv", feedback_bytes), FEEDBACK, "Feedback")
    if stats.empty:
        raise DataError("Statistics must contain at least one record.")
    for key in ["characters", "skill_groups", "review_thresholds"]:
        col = {"characters": "character", "skill_groups": "skill_group", "review_thresholds": "parameter"}[key]
        if tables[key][col].eq("").any() or tables[key][col].duplicated().any():
            raise DataError(f"{key}: identifiers must be present and unique.")
    expected = {"win_rate_min": .46, "win_rate_max": .54, "min_appearances": 500,
                "pick_rate_max": .3, "pick_rate_min": .02, "max_priorities": 3}
    try:
        actual = dict(zip(tables["review_thresholds"].parameter, tables["review_thresholds"].value.astype(float)))
        shares = tables["skill_groups"].share_of_players.astype(float)
    except ValueError as exc:
        raise DataError("Invalid numeric thresholds or player shares.") from exc
    if actual != expected or not all(token in guide for token in ["46%", "54%", "500", "30%", "2%"]):
        raise DataError("Guide/thresholds differ from the supported, reviewed game rules. Review them together before changing code.")
    if not shares.between(0, 1).all() or abs(shares.sum() - 1) > 1e-6:
        raise DataError("Player shares must be between zero and one and sum to one.")
    names, groups = set(tables["characters"].character), set(tables["skill_groups"].skill_group)
    for frame, label, group_col in [(stats, "Statistics", "skill_group"), (feedback, "Feedback", "skill_level")]:
        if not set(frame.character) <= names or not set(frame[group_col]) <= groups | ({""} if label == "Feedback" else set()):
            raise DataError(f"{label}: unknown character or skill group for this game's roster.")
        if not set(frame["update"]) <= {"3.1", CURRENT}:
            raise DataError(f"{label}: this prototype supports patches 3.1 and {CURRENT}; include current-patch records.")
    if stats[STATS[:3]].eq("").any().any() or stats.duplicated(STATS[:3]).any():
        raise DataError("Statistics: character/update/skill_group keys must be unique and nonempty.")
    for col in COUNTS:
        try:
            stats[col] = pd.to_numeric(stats[col].replace("", None), errors="raise").astype(float)
        except (ValueError, TypeError) as exc:
            raise DataError(f"Statistics: {col} must contain whole numbers or blanks.") from exc
        values = stats[col].dropna()
        if ((values < 0) | (values % 1 != 0) | (values > 1e12)).any():
            raise DataError(f"Statistics: {col} contains impossible counts.")
    if (stats.wins > stats.appearances).any() or (stats.picks > stats.eligible_selections).any():
        raise DataError("Wins cannot exceed appearances; picks cannot exceed eligible selections.")
    if not stats["update"].eq(CURRENT).any():
        raise DataError(f"No current-update ({CURRENT}) statistics were provided.")
    # Game mechanics remain authoritative; replace default policy sections with the active settings.
    start = guide.index("## 4.")
    end = guide.index("## 6.")
    policy = f"## Active review policy\n{json.dumps(config.snapshot(), indent=2)}\nInvestigate only sufficient-sample out-of-range groups. Missing or small samples require Collect data. Pick-watch signals warrant Monitor. Supported investigations precede collection and monitoring. Within investigations use {config.ranking.lower()}; use the other numerical criterion next. Context explains mechanisms and uncertainty, not causal proof. Return at most three priorities; explain deferred investigation candidates. Meeting the sample setting is not statistical certainty.\n\n"
    guide = guide[:start] + policy + guide[end:]
    guide = guide.replace("Signal is borderline, the pick rate is outside its watch range", "Signal is borderline, the pick rate is outside the configured watch range")
    warnings = []
    coverage = []
    roster = tables["characters"]
    observed = set(stats.loc[stats["update"].eq(CURRENT), "character"])
    standard = set(roster.loc[roster.availability.eq("Standard"), "character"])
    expected_names = standard if config.scope == "Standard only" else names if config.scope == "Entire roster" else standard | observed
    for character in sorted(names):
        present = set(stats.loc[(stats.character == character) & stats["update"].eq(CURRENT), "skill_group"])
        included = character in expected_names
        coverage.append({"Character": character, "Scope": "Included" if included else "Outside scope",
                         "Records received": len(present), "Expected groups": len(groups) if included else 0,
                         "Coverage": "Complete" if included and present == groups else "Incomplete" if included else "Not reviewed"})
    stats = stats[stats.character.isin(expected_names)].copy()
    stats["record_missing"] = False
    missing_rows = []
    for character in sorted(expected_names):
        present = set(stats.loc[(stats.character == character) & (stats["update"] == CURRENT), "skill_group"])
        for group in sorted(groups - present):
            missing_rows.append({"character": character, "update": CURRENT, "skill_group": group, "record_missing": True,
                                 **{c: float("nan") for c in COUNTS}})
            warnings.append(f"Missing current record: {character}, {group}; collect missing records.")
    if missing_rows:
        stats = pd.concat([stats, pd.DataFrame(missing_rows)], ignore_index=True)
    actual = {**actual, **{k: v for k, v in config.snapshot().items() if k in actual}}
    incomplete = stats.loc[stats["update"].eq(CURRENT) & stats[COUNTS].isna().any(axis=1)]
    for row in records(incomplete):
        warnings.append(f"Missing counts: {row['character']}, {row['skill_group']}; affected metrics unavailable.")
    for item in coverage:
        if item["Character"] in set(incomplete.character):
            item["Coverage"] = "Missing records or counts"
    stats["evidence_id"] = "stats:" + stats["update"] + ":" + stats.character + ":" + stats.skill_group
    stats["win_rate"] = stats.wins / stats.appearances.where(stats.appearances > 0)
    stats["pick_rate"] = stats.picks / stats.eligible_selections.where(stats.eligible_selections > 0)
    stats["sample_sufficient"] = stats.appearances.ge(actual["min_appearances"]) & stats.wins.notna()
    stats["balance_flag"] = "Within range"
    stats.loc[stats.win_rate > actual["win_rate_max"], "balance_flag"] = "Strong"
    stats.loc[stats.win_rate < actual["win_rate_min"], "balance_flag"] = "Weak"
    stats.loc[~stats.sample_sufficient, "balance_flag"] = "Collect data"
    stats["pick_watch"] = (stats.pick_rate > actual["pick_rate_max"]) | (stats.pick_rate < actual["pick_rate_min"])
    if feedback.comment_id.eq("").any() or feedback.comment_id.duplicated().any() or feedback.author_id.eq("").any() or feedback.text.eq("").any():
        raise DataError("Feedback: unique comment IDs, author IDs, and text are required.")
    for table, key in [("abilities", "ability_id"), ("patch_notes", "change_id"), ("design_backlog", "backlog_id")]:
        if tables[table][key].eq("").any() or tables[table][key].duplicated().any():
            raise DataError(f"{table}: evidence IDs must be present and unique.")
    feedback["outdated"] = feedback["update"] != CURRENT
    seen = {}
    duplicates = []
    for row in records(feedback):
        normalized = re.sub(r"[^\w]+", "", row["text"].casefold())
        key = (row["author_id"], row["character"], row["update"], normalized)
        duplicates.append(seen.get(key))
        seen.setdefault(key, row["comment_id"])
    feedback["duplicate_of"] = duplicates
    feedback["suspicious"] = feedback.text.str.contains(r"ignore.{0,40}(?:rules|instructions)|rank .{0,30}(?:first|top priority)", case=False, regex=True)
    return Evidence("Uploaded files" if upload else name, tables, stats, feedback, guide, hashes, list(dict.fromkeys(warnings)), config, coverage)


def review_candidates(evidence: Evidence) -> list[dict]:
    """Deterministic comparison. Does not read comments, context, or an answer key."""
    shares = dict(zip(evidence.tables["skill_groups"].skill_group,
                      evidence.tables["skill_groups"].share_of_players.astype(float)))
    candidates = []
    for character, frame in evidence.stats[evidence.stats["update"] == CURRENT].groupby("character", sort=False):
        flagged = frame[frame.sample_sufficient & frame.balance_flag.isin(["Strong", "Weak"])]
        collect = frame[~frame.sample_sufficient | frame.pick_rate.isna()]
        watch = frame[frame.pick_watch & frame.sample_sufficient]
        if not flagged.empty:
            action, chosen, quality = "Investigate", flagged, 0
        elif not collect.empty:
            action, chosen, quality = "Collect data", collect, 1
        elif not watch.empty:
            action, chosen, quality = "Monitor", watch, 2
        else:
            continue
        impact = sum(shares[g] for g in chosen.skill_group)
        deviation = max([max(0, r - evidence.thresholds["win_rate_max"], evidence.thresholds["win_rate_min"] - r) for r in flagged.win_rate] or [0])
        stable_id = evidence.tables["characters"].set_index("character").loc[character, "role"]
        candidates.append({"character": character, "action": action, "affected_skill_groups": chosen.skill_group.tolist(),
                           "metric_refs": chosen.evidence_id.tolist(), "player_share": impact, "deviation": deviation,
                           "reason": ("Meets configured sample minimum and is outside the win-rate range." if action == "Investigate" else "Missing counts or below the configured sample minimum." if action == "Collect data" else "Outside the configured pick-rate watch range."),
                           "_sort": (quality, -impact, -deviation, stable_id) if evidence.config.ranking == "Player reach first" else (quality, -deviation, -impact, stable_id)})
    candidates.sort(key=lambda x: x["_sort"])
    for row in candidates:
        row.pop("_sort")
    return candidates


def statistics_baseline(evidence: Evidence) -> list[dict]:
    return review_candidates(evidence)[:int(evidence.thresholds["max_priorities"])]


def coverage_summary(evidence: Evidence, report: dict) -> list[dict]:
    selected = {p["character"]: i for i, p in enumerate(report["priorities"], 1)}
    deferred = {p["character"]: p["reason"] for p in report.get("not_selected", [])}
    candidates = {p["character"]: p for p in review_candidates(evidence)}
    rows = []
    for item in evidence.coverage:
        who = item["Character"]
        candidate = candidates.get(who)
        disposition = f"Priority {selected[who]}" if who in selected else "Outside scope" if item["Scope"] == "Outside scope" else "Not selected" if candidate else "No statistical flag"
        reason = deferred.get(who) or (candidate["reason"] if candidate else "Not included in this review." if item["Scope"] == "Outside scope" else "Current metrics meet the configured checks; this is not proof that no issue exists.")
        rows.append({**item, "Disposition": disposition, "Signal": candidate["action"] if candidate else "—", "Reason": reason})
    return rows
