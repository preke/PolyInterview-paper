#!/usr/bin/env python3
"""Recompute deployment statistics over every account in backend/users.

No account is excluded. The output is the review snapshot used by the paper
while its deployment statistics are being manually verified.
"""

import json
from collections import Counter
from pathlib import Path

import build_comprehensive_report as report


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "analysis" / "corpus_stats_all.json"


def count_recordings(extension, directory):
    return sum(1 for _ in report.USERS.glob(f"*/*/{directory}/*.{extension}"))


def main():
    report.REMOVED = set()
    sessions = report.load_sessions()
    users = Counter(session["user"] for session in sessions)
    statuses = Counter(
        (session["log"].get("status") or "unknown") for session in sessions
    )
    styles = Counter(
        (session["log"].get("interview_style") or "unknown") for session in sessions
    )
    evaluation = report.analyze_evaluations(sessions)

    required_categories = {
        "Self Introduction", "Behavioral", "Skill QA", "Scenario",
        "Candidate Questions",
    }
    complete_flows = sum(
        required_categories
        <= {question.get("category") for question in session["questions"]}
        for session in sessions
    )
    answered_records = sum(
        bool((question.get("answer") or "").strip())
        for session in sessions for question in session["questions"]
    )
    positions = {
        (session["log"].get("position_name") or "").strip().casefold()
        for session in sessions
        if (session["log"].get("position_name") or "").strip()
    }
    alignment_items = []
    for session in sessions:
        job_description = (session["log"].get("job_description") or "").strip()
        position = (session["log"].get("position_name") or "").strip()
        questions = " ".join(
            question["question"] for question in session["questions"]
            if question.get("category") != "Candidate Questions"
        ).strip()
        if job_description and position and questions:
            alignment_items.append({
                "query": questions,
                "reference": job_description,
                "group": position,
            })
    role_alignment = report.alignment_metrics(
        alignment_items, "query", "reference", "group"
    )
    followups = report.analyze_followups(sessions)

    feature_stats = {}
    for feature, values in evaluation["feature_stats"].items():
        feature_stats[feature] = {
            "mean_all": values["mean"],
            "n_all": values["n"],
            "mean_failure_excluded": values["mean_failure_excluded"],
            "n_failure_excluded": values["n_failure_excluded"],
        }

    feedback_files = list(report.USERS.glob("*/*/feedback/*.json"))
    stats = {
        "scope": "all_account_directories_no_exclusions",
        "meta": {
            "users": len(users),
            "returning_users": sum(count > 1 for count in users.values()),
            "sessions": len(sessions),
            "questions": sum(len(session["questions"]) for session in sessions),
            "statuses": dict(statuses),
            "styles": dict(styles),
            "sessions_evaluated": evaluation["sessions"],
            "pooled_scored_answers": evaluation["records"],
            "feedback_submissions": len(feedback_files),
            "recordings": {
                "wav": count_recordings("wav", "audio"),
                "webm": count_recordings("webm", "video"),
                "mp4": count_recordings("mp4", "video"),
            },
        },
        "usage_evidence": {
            "complete_five_stage_sessions": complete_flows,
            "answered_question_records": answered_records,
            "distinct_position_titles": len(positions),
            "recorded_followup_turns": followups["followup_turns"],
            "records_with_followups": followups["records_with_followup"],
            "role_alignment": role_alignment,
        },
        "nonverbal_outcome": {
            "total": evaluation["records"],
            "vlm_failed": evaluation["outcome"]["failed"],
            "no_video": evaluation["outcome"]["no_video"],
            "vlm_ok": evaluation["outcome"]["ok"],
        },
        "features": feature_stats,
        "modality_means": evaluation["modality_means"],
        "correlations": evaluation["correlations"],
        "score": {
            "n": evaluation["score_n"],
            "mean": evaluation["score_mean"],
        },
    }
    OUTPUT.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(
        f"WROTE {OUTPUT}: users={len(users)} sessions={len(sessions)} "
        f"questions={stats['meta']['questions']} "
        f"scored_answers={evaluation['records']}"
    )


if __name__ == "__main__":
    main()
