#!/usr/bin/env python3
"""Validate and aggregate the ten independent LLM-agent panel ratings."""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RATINGS = HERE / "ratings"
PACKET = HERE / "evaluation_packet.json"
PROFILES = HERE / "profiles.json"
SUMMARY = HERE / "summary.json"
TABLE = ROOT / "paper" / "figures" / "table_llm_agent_panel.tex"

MODULE_LABELS = {
    "question_plan": "Question plans",
    "followup": "Follow-ups",
    "feedback_report": "Feedback reports",
}


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def fmt(value, digits=2):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "--"
    return f"{value:.{digits}f}"


def load_json(path):
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)


def validate():
    packet = load_json(PACKET)
    profiles = load_json(PROFILES)
    expected_agents = {profile["agent_id"] for profile in profiles}
    expected_artifacts = {
        artifact["artifact_id"]: artifact["module"]
        for artifact in packet["artifacts"]
    }
    criteria = packet["criteria"]

    rating_files = sorted(RATINGS.glob("A*.json"))
    if len(rating_files) != len(expected_agents):
        raise RuntimeError(
            f"Expected {len(expected_agents)} rating files, found {len(rating_files)}"
        )

    panels = []
    seen_agents = set()
    for path in rating_files:
        panel = load_json(path)
        agent_id = panel.get("agent_id")
        if agent_id not in expected_agents or agent_id in seen_agents:
            raise RuntimeError(f"Unexpected or duplicate agent_id in {path}: {agent_id}")
        seen_agents.add(agent_id)
        ratings = panel.get("ratings") or []
        if len(ratings) != len(expected_artifacts):
            raise RuntimeError(f"{agent_id}: expected 12 ratings, found {len(ratings)}")

        seen_artifacts = set()
        for rating in ratings:
            artifact_id = rating.get("artifact_id")
            module = rating.get("module")
            if artifact_id not in expected_artifacts or artifact_id in seen_artifacts:
                raise RuntimeError(f"{agent_id}: unexpected/duplicate artifact {artifact_id}")
            seen_artifacts.add(artifact_id)
            if module != expected_artifacts[artifact_id]:
                raise RuntimeError(f"{agent_id}/{artifact_id}: wrong module {module}")
            scores = rating.get("scores") or {}
            if set(scores) != set(criteria[module]):
                raise RuntimeError(
                    f"{agent_id}/{artifact_id}: criteria {sorted(scores)} != "
                    f"{sorted(criteria[module])}"
                )
            for key, value in scores.items():
                if not isinstance(value, int) or not 1 <= value <= 5:
                    raise RuntimeError(
                        f"{agent_id}/{artifact_id}/{key}: invalid score {value}"
                    )
        panels.append(panel)
    return packet, profiles, panels


def aggregate(packet, profiles, panels):
    score_grid = defaultdict(dict)
    module_values = defaultdict(list)
    criterion_values = defaultdict(list)
    agent_module_values = defaultdict(lambda: defaultdict(list))

    for panel in panels:
        agent_id = panel["agent_id"]
        for rating in panel["ratings"]:
            artifact_id = rating["artifact_id"]
            module = rating["module"]
            for criterion, value in rating["scores"].items():
                score_grid[(artifact_id, criterion)][agent_id] = value
                module_values[module].append(value)
                criterion_values[(module, criterion)].append(value)
                agent_module_values[module][agent_id].append(value)

    within_one = defaultdict(list)
    for (artifact_id, criterion), agent_scores in score_grid.items():
        module = next(
            artifact["module"] for artifact in packet["artifacts"]
            if artifact["artifact_id"] == artifact_id
        )
        values = list(agent_scores.values())
        within_one[module].extend(
            abs(left - right) <= 1 for left, right in combinations(values, 2)
        )

    module_summary = {}
    for module in MODULE_LABELS:
        values = module_values[module]
        per_agent = [mean(scores) for scores in agent_module_values[module].values()]
        module_summary[module] = {
            "artifacts": sum(
                artifact["module"] == module for artifact in packet["artifacts"]
            ),
            "criterion_ratings": len(values),
            "mean": mean(values),
            "rating_sd": statistics.pstdev(values),
            "agent_mean_sd": statistics.pstdev(per_agent),
            "high_score_rate": mean([value >= 4 for value in values]),
            "within_one_pair_agreement": mean(within_one[module]),
            "criteria": {
                criterion: {
                    "mean": mean(criterion_values[(module, criterion)]),
                    "sd": statistics.pstdev(criterion_values[(module, criterion)]),
                }
                for criterion in packet["criteria"][module]
            },
        }

    all_values = [value for values in module_values.values() for value in values]
    return {
        "study_type": packet["study_type"],
        "human_experts": 0,
        "llm_agents": len(panels),
        "artifacts": len(packet["artifacts"]),
        "artifact_level_reviews": len(panels) * len(packet["artifacts"]),
        "criterion_ratings": len(all_values),
        "overall_mean": mean(all_values),
        "overall_rating_sd": statistics.pstdev(all_values),
        "module_summary": module_summary,
        "profiles": [
            {"agent_id": profile["agent_id"], "role": profile["role"]}
            for profile in profiles
        ],
        "interpretation_boundary": (
            "These are simulated LLM-agent judgments over text-visible artifacts. "
            "They are a protocol pilot, not human-expert evidence and not a validation "
            "of audio, video, learning outcomes, or hiring-related validity."
        ),
    }


def write_table(summary):
    rows = []
    for module, label in MODULE_LABELS.items():
        item = summary["module_summary"][module]
        rows.append(
            f"{label} & {item['artifacts']} & {fmt(item['mean'])} & "
            f"{fmt(item['agent_mean_sd'])} & "
            f"{100.0 * item['within_one_pair_agreement']:.1f}\\% \\\\"
        )

    content = "\n".join([
        "\\begin{center}",
        "\\small",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{tabular}{@{}lrrrr@{}}",
        "\\toprule",
        "\\textbf{Module} & \\textbf{$n$} & \\textbf{Mean} & \\textbf{Agent SD} & \\textbf{$\\pm1$ agree} \\\\",
        "\\midrule",
        *rows,
        "\\bottomrule",
        "\\end{tabular}",
        "\\captionsetup{hypcap=false}",
        "\\captionof{table}{Scores from the ten-agent simulated protocol pilot (1--5).}",
        "\\label{tab:llm-panel}",
        "\\end{center}",
        "",
    ])
    TABLE.write_text(content, encoding="utf-8")


def main():
    packet, profiles, panels = validate()
    summary = aggregate(packet, profiles, panels)
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_table(summary)
    print(
        f"Aggregated {summary['llm_agents']} agents, "
        f"{summary['artifact_level_reviews']} artifact reviews, "
        f"{summary['criterion_ratings']} criterion ratings; "
        f"overall mean={summary['overall_mean']:.3f}"
    )


if __name__ == "__main__":
    main()
