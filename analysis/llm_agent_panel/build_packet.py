#!/usr/bin/env python3
"""Build a deterministic, de-identified packet for the LLM-agent panel pilot.

Question-plan artifacts contain system-generated questions and job descriptions.
Follow-up and feedback artifacts are restricted to known template/test accounts;
no CV files, raw audio, raw video, account IDs, or session IDs leave this script.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
USERS = ROOT / "backend" / "users"
OUTPUT = Path(__file__).resolve().parent / "evaluation_packet.json"

QUESTION_ROLES = [
    "AI Research Assistant",
    "Data Analyst",
    "Software Engineer",
    "Graduate Civil Engineer",
]
SYNTHETIC_USERS = {"5840", "5844", "5868", "5884"}
EVALUATED_CATEGORIES = ["Self Introduction", "Behavioral", "Skill QA", "Scenario"]

FOLLOWUP_PATTERN = re.compile(
    r"\[(Main|Follow-up\s+\d+) Question\]\s*(.*?)\s*\n+"
    r"\[Answer\]\s*(.*?)(?=\n+---|\Z)",
    re.I | re.S,
)


def load_logs():
    logs = []
    for path in sorted(USERS.glob("*/*/interview_log.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        logs.append((path, payload))
    return logs


def scrub(value, limit=1200):
    text = str(value or "")
    text = re.sub(r"(?i)\b(?:Terry|John\s+Doe|Chan\s+Tai\s+Man)\b", "[NAME]", text)
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"https?://\S+|www\.\S+", "[URL]", text)
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", "[PHONE]", text)
    text = re.sub(
        r"(?i)\b(my name is|i am|i'm)\s+[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2}",
        r"\1 [NAME]",
        text,
    )
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text


def word_count(value):
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", str(value or "")))


def source_digest(path):
    relative = str(path.relative_to(ROOT)).encode("utf-8")
    return hashlib.sha256(relative).hexdigest()[:12]


def build_question_artifacts(logs):
    artifacts = []
    for index, role in enumerate(QUESTION_ROLES, start=1):
        candidates = []
        for path, log in logs:
            if (log.get("position_name") or "").strip() != role:
                continue
            jd = (log.get("job_description") or "").strip()
            questions = [
                question for question in (log.get("questions") or [])
                if isinstance(question, dict)
                and (question.get("question") or "").strip()
                and question.get("category") != "Candidate Questions"
            ]
            categories = {question.get("category") for question in questions}
            if len(jd) < 200 or len(questions) < 4:
                continue
            rank = (
                1 if log.get("status") == "completed" else 0,
                len(categories),
                sum(word_count(question.get("question")) for question in questions),
            )
            candidates.append((rank, str(path), path, log, questions))
        if not candidates:
            raise RuntimeError(f"No question-set candidate for role: {role}")
        _, _, path, log, questions = max(candidates)
        artifacts.append({
            "artifact_id": f"Q{index}",
            "module": "question_plan",
            "role": role,
            "job_description_excerpt": scrub(log.get("job_description"), 900),
            "generated_questions": [
                {
                    "category": question.get("category") or "",
                    "question": scrub(question.get("question"), 360),
                }
                for question in questions[:4]
            ],
            "source_digest": source_digest(path),
        })
    return artifacts


def build_followup_artifacts(logs):
    by_category = {category: [] for category in EVALUATED_CATEGORIES}
    for path, log in logs:
        if path.parent.parent.name not in SYNTHETIC_USERS:
            continue
        role = scrub(log.get("position_name"), 120)
        for question in log.get("questions") or []:
            category = question.get("category")
            if category not in by_category:
                continue
            segments = FOLLOWUP_PATTERN.findall((question.get("answer") or "").strip())
            for segment_index, (label, followup_question, followup_answer) in enumerate(segments):
                if not label.lower().startswith("follow") or segment_index == 0:
                    continue
                prior_answer = segments[segment_index - 1][2].strip()
                if word_count(prior_answer) < 3:
                    continue
                rank = min(word_count(prior_answer), 120) + min(word_count(followup_question), 40)
                by_category[category].append((rank, str(path), {
                    "role": role,
                    "category": category,
                    "main_question": scrub(question.get("question"), 420),
                    "candidate_answer": scrub(prior_answer, 850),
                    "generated_followup": scrub(followup_question, 420),
                    "source_digest": source_digest(path),
                }))

    artifacts = []
    for index, category in enumerate(EVALUATED_CATEGORIES, start=1):
        if not by_category[category]:
            raise RuntimeError(f"No synthetic follow-up candidate for category: {category}")
        _, _, payload = max(by_category[category])
        artifacts.append({
            "artifact_id": f"F{index}",
            "module": "followup",
            **payload,
        })
    return artifacts


def candidate_answers(transcript):
    segments = FOLLOWUP_PATTERN.findall((transcript or "").strip())
    if segments:
        return " | ".join(answer.strip() for _, _, answer in segments if answer.strip())
    return transcript or ""


def compact_aspects(aspects):
    compact = []
    for name, payload in (aspects or {}).items():
        if not isinstance(payload, dict):
            continue
        compact.append({
            "aspect": name,
            "score": payload.get("score"),
            "justification": scrub(payload.get("justification"), 420),
        })
    compact.sort(key=lambda item: str(item["aspect"]))
    return compact[:4]


def compact_suggestion(suggestion):
    if isinstance(suggestion, dict):
        return {
            str(key): scrub(value, 420)
            for key, value in suggestion.items()
            if value
        }
    return scrub(suggestion, 700)


def build_feedback_artifacts(logs):
    by_category = {category: [] for category in EVALUATED_CATEGORIES}
    for path, log in logs:
        if path.parent.parent.name not in SYNTHETIC_USERS:
            continue
        role = scrub(log.get("position_name"), 120)
        for question in log.get("questions") or []:
            category = question.get("category")
            if category not in by_category:
                continue
            response = candidate_answers(question.get("answer") or "")
            aspects = compact_aspects(question.get("aspects"))
            suggestion = compact_suggestion(question.get("suggestion"))
            polished = scrub(question.get("polished_answer"), 900)
            if word_count(response) < 3 or not aspects or not suggestion:
                continue
            rank = (
                min(word_count(response), 160)
                + 15 * len(aspects)
                + min(word_count(polished), 80)
            )
            by_category[category].append((rank, str(path), {
                "role": role,
                "category": category,
                "question": scrub(question.get("question"), 420),
                "candidate_response": scrub(response, 900),
                "system_aspect_evidence": aspects,
                "system_recommendation": suggestion,
                "polished_response": polished,
                "source_digest": source_digest(path),
            }))

    artifacts = []
    for index, category in enumerate(EVALUATED_CATEGORIES, start=1):
        if not by_category[category]:
            raise RuntimeError(f"No synthetic feedback candidate for category: {category}")
        _, _, payload = max(by_category[category])
        artifacts.append({
            "artifact_id": f"R{index}",
            "module": "feedback_report",
            **payload,
        })
    return artifacts


def main():
    logs = load_logs()
    artifacts = (
        build_question_artifacts(logs)
        + build_followup_artifacts(logs)
        + build_feedback_artifacts(logs)
    )
    packet = {
        "study_type": "profiled_llm_agent_protocol_pilot",
        "human_experts": 0,
        "llm_agents": 10,
        "artifact_count": len(artifacts),
        "sampling_note": (
            "Question plans use system-generated text from four roles. Follow-up and "
            "feedback artifacts use known template/test accounts only. No CV files, "
            "raw audio, raw video, account IDs, or session IDs are included."
        ),
        "scale": {
            "1": "poor or unsupported",
            "2": "substantial weakness",
            "3": "mixed or adequate",
            "4": "strong",
            "5": "excellent",
        },
        "criteria": {
            "question_plan": ["role_relevance", "specificity", "stage_coverage"],
            "followup": ["answer_dependence", "relevance", "diagnostic_depth"],
            "feedback_report": ["evidence_alignment", "actionability", "response_faithfulness"],
        },
        "artifacts": artifacts,
    }
    OUTPUT.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(artifacts)} artifacts")


if __name__ == "__main__":
    main()
