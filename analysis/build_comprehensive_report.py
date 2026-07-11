#!/usr/bin/env python3
"""Build a self-contained HTML evidence report for PolyInterview.

The report keeps three data snapshots separate:
1. the legacy v3 dashboard cohort;
2. the paper-locked 46-user/120-session corpus;
3. the current backend snapshot under the paper's strict 39-account exclusion.

Only aggregate statistics and de-identified system-generated questions are
written to the report. CV text is used locally for an aggregate lexical check
and is never included in the output.
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import statistics
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
USERS = ROOT / "backend" / "users"
OUTPUT = ANALYSIS / "polyinterview-comprehensive-analysis.html"

# Rule-based exclusions documented in PAPER_FACTS.md / FINDINGS.md.
REMOVED = set(
    "5865 5899 5890 5951 7 5879 5841 5883 5877 5870 5884 6 1 8 5885 "
    "5871 5876 5882 5840 5878 5861 5893 5923 5936 5889 5842 5845 5873 "
    "5887 5880 5874 5875 5881 5886 5844 5888 5843 2 5".split()
)

TEXT_PROF = ["conceptual_accuracy", "terminology_usage", "problem_solving_logic_chain"]
TEXT_EXPR = ["structural_clarity", "coherence", "word_usage_pattern"]
VIDEO = ["eye_contact", "facial_expression", "body_posture", "gesture"]
AUDIO = ["accuracy", "prosody", "fluency"]
TEXT = TEXT_PROF + TEXT_EXPR
ALL_FEATURES = TEXT + VIDEO + AUDIO
FEATURE_GROUPS = {
    "professional_performance": TEXT_PROF,
    "way_of_expression": TEXT_EXPR,
    "nonverbal": VIDEO,
    "oral_expression": AUDIO,
}
FEATURE_LABELS = {
    "conceptual_accuracy": "概念准确性",
    "terminology_usage": "术语使用",
    "problem_solving_logic_chain": "问题解决逻辑链",
    "structural_clarity": "结构清晰度",
    "coherence": "连贯性",
    "word_usage_pattern": "用词模式",
    "eye_contact": "眼神交流",
    "facial_expression": "面部表情",
    "body_posture": "身体姿态",
    "gesture": "手势",
    "accuracy": "发音准确度",
    "prosody": "韵律",
    "fluency": "流利度",
}
ASPECT_LABELS = {
    "general_intelligence": "通用智力",
    "applied_mental_skills": "应用思维",
    "creativity": "创造力",
    "job_knowledge_and_skills": "岗位知识技能",
    "education_and_training": "教育与培训",
    "experience_and_work_history": "经验与经历",
    "communication_skills": "沟通能力",
    "interpersonal_skills": "人际能力",
    "leadership": "领导力",
    "persuasiveness": "说服力",
}
CATEGORIES = ["Self Introduction", "Behavioral", "Skill QA", "Scenario", "Candidate Questions"]
CATEGORY_ZH = {
    "Self Introduction": "自我介绍",
    "Behavioral": "行为题",
    "Skill QA": "技能题",
    "Scenario": "情景题",
    "Candidate Questions": "候选人提问",
}


def pct(num: float, den: float) -> float:
    return 100.0 * num / den if den else 0.0


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def fmt(value: float, digits: int = 1) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "--"
    return f"{value:.{digits}f}"


def load_sessions():
    sessions = []
    for user_dir in sorted(USERS.iterdir(), key=lambda p: p.name):
        if not user_dir.is_dir() or user_dir.name in REMOVED:
            continue
        for log_path in sorted(user_dir.glob("*/interview_log.json")):
            try:
                log = json.loads(log_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue
            questions = [
                q for q in (log.get("questions") or [])
                if isinstance(q, dict) and (q.get("question") or "").strip()
            ]
            sessions.append({
                "user": user_dir.name,
                "session": log_path.parent.name,
                "path": log_path.parent,
                "log": log,
                "questions": questions,
            })
    return sessions


def alignment_metrics(items, query_key, reference_key, group_key):
    """Compare each query to its matched reference and different-group references."""
    if len(items) < 3:
        return None
    vectorizer = TfidfVectorizer(
        stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=1
    )
    matrix = vectorizer.fit_transform(
        [item[query_key] for item in items] + [item[reference_key] for item in items]
    )
    n = len(items)
    similarity = cosine_similarity(matrix[:n], matrix[n:])
    matched = np.diag(similarity)
    baselines = []
    rank_one = []
    for idx, item in enumerate(items):
        candidates = [
            j for j, other in enumerate(items)
            if str(other[group_key]).casefold() != str(item[group_key]).casefold()
        ]
        if not candidates:
            candidates = [j for j in range(n) if j != idx]
        values = [similarity[idx, j] for j in candidates]
        baselines.append(float(np.median(values)))
        rank_one.append(float(matched[idx]) > max(values))
    baseline = np.asarray(baselines)
    delta = matched - baseline
    rng = np.random.default_rng(42)
    boot = np.asarray([
        np.mean(rng.choice(delta, size=len(delta), replace=True)) for _ in range(5000)
    ])
    return {
        "n": n,
        "matched_median": float(np.median(matched)),
        "matched_mean": float(np.mean(matched)),
        "baseline_median": float(np.median(baseline)),
        "baseline_mean": float(np.mean(baseline)),
        "delta_median": float(np.median(delta)),
        "delta_mean": float(np.mean(delta)),
        "win_rate": float(np.mean(delta > 0)),
        "rank_one_rate": float(np.mean(rank_one)),
        "ci_low": float(np.quantile(boot, 0.025)),
        "ci_high": float(np.quantile(boot, 0.975)),
    }


def extract_cv_alignment(sessions):
    items = []
    for session in sessions:
        upload_dir = session["path"] / "uploads"
        pdfs = sorted(upload_dir.glob("*.pdf")) if upload_dir.exists() else []
        if not pdfs:
            continue
        query = " ".join(
            q["question"] for q in session["questions"]
            if q.get("category") in {"Self Introduction", "Behavioral"}
        ).strip()
        if not query:
            continue
        try:
            result = subprocess.run(
                ["pdftotext", str(pdfs[0]), "-"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            cv_text = " ".join(result.stdout.split())
        except (OSError, subprocess.SubprocessError):
            cv_text = ""
        if len(cv_text) < 100:
            continue
        items.append({
            "query": query,
            "reference": cv_text,
            "group": session["user"],
        })
    return alignment_metrics(items, "query", "reference", "group")


def analyze_followups(sessions):
    pattern = re.compile(
        r"\[(Main|Follow-up\s+\d+) Question\]\s*(.*?)\s*\n+"
        r"\[Answer\]\s*(.*?)(?=\n+---|\Z)",
        re.I | re.S,
    )
    depths = []
    by_style = defaultdict(list)
    grounding_items = []
    for session in sessions:
        style = (session["log"].get("interview_style") or "unknown").lower()
        for question in session["questions"]:
            transcript = (question.get("answer") or "").strip()
            if not transcript:
                continue
            segments = pattern.findall(transcript)
            depth = sum(label.lower().startswith("follow") for label, _, _ in segments)
            if not depth:
                depth = len(re.findall(r"\[Follow-up\s+\d+ Question\]", transcript, re.I))
            depths.append(depth)
            by_style[style].append(depth)
            for index, (label, followup, _) in enumerate(segments):
                if label.lower().startswith("follow") and index > 0:
                    grounding_items.append({
                        "query": followup.strip(),
                        "reference": segments[index - 1][2].strip(),
                        "group": f"{session['user']}:{session['session']}:{index}",
                    })

    grounding = alignment_metrics(grounding_items, "query", "reference", "group")
    return {
        "answered_records": len(depths),
        "records_with_followup": sum(value > 0 for value in depths),
        "followup_turns": sum(depths),
        "max_depth": max(depths, default=0),
        "depth_counts": Counter(depths),
        "by_style": {key: Counter(values) for key, values in by_style.items()},
        "grounding": grounding,
    }


def get_score(value):
    if not isinstance(value, dict) or "score" not in value:
        return None
    try:
        return float(value["score"])
    except (TypeError, ValueError):
        return None


def analyze_evaluations(sessions):
    records = []
    outcome = Counter()
    evaluated_sessions = 0
    session_modalities = []
    score_values = []
    category_scores = defaultdict(list)

    for session in sessions:
        eval_dir = session["path"] / "evaluations"
        eval_files = sorted(
            eval_dir.glob("*.json"), key=lambda p: p.stat().st_size, reverse=True
        ) if eval_dir.exists() else []
        if not eval_files:
            continue
        try:
            evaluation = json.loads(eval_files[0].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue

        session_features = defaultdict(list)
        session_has_evaluation = False
        for question in evaluation.get("evaluations") or []:
            result = question.get("result") or {}
            criteria = result.get("assessment_criteria") or {}
            record = {
                "category": question.get("category") or "",
                "session": session["session"],
            }
            got_any = False
            for group, features in FEATURE_GROUPS.items():
                values = criteria.get(group) or {}
                for feature in features:
                    value = get_score(values.get(feature) or {})
                    if value is not None:
                        record[feature] = value
                        session_features[feature].append(value)
                        got_any = True
            if not got_any:
                continue
            session_has_evaluation = True

            nonverbal = criteria.get("nonverbal") or {}
            total_videos = nonverbal.get("total_videos")
            evaluated_videos = nonverbal.get("num_videos_evaluated")
            justifications = " ".join(
                str((nonverbal.get(feature) or {}).get("justification", ""))
                for feature in VIDEO
            )
            failed = (
                "Evaluation failed" in justifications
                or (
                    isinstance(evaluated_videos, int)
                    and evaluated_videos == 0
                    and (total_videos or 0) > 0
                )
            )
            no_video = (
                total_videos in (0, None)
                and not failed
                and all(record.get(feature, 0) == 0 for feature in VIDEO)
            )
            if failed:
                outcome["failed"] += 1
            elif no_video:
                outcome["no_video"] += 1
            else:
                outcome["ok"] += 1
            record["nv_failed"] = failed
            record["nv_no_video"] = no_video
            records.append(record)

            try:
                score = float(result.get("score"))
            except (TypeError, ValueError):
                score = None
            if score is not None:
                score_values.append(score)
                category_scores[record["category"]].append(score)

        if session_has_evaluation:
            evaluated_sessions += 1

            def modality_mean(features):
                values = [value for feature in features for value in session_features[feature]]
                return statistics.fmean(values) if values else None

            session_modalities.append({
                "text": modality_mean(TEXT),
                "audio": modality_mean(AUDIO),
                "video": modality_mean(VIDEO),
            })

    feature_stats = {}
    for feature in ALL_FEATURES:
        values = [record[feature] for record in records if feature in record]
        conservative = [
            record[feature] for record in records
            if feature in record and (feature not in VIDEO or not record["nv_failed"])
        ]
        feature_stats[feature] = {
            "n": len(values),
            "mean": statistics.fmean(values) if values else None,
            "n_failure_excluded": len(conservative),
            "mean_failure_excluded": statistics.fmean(conservative) if conservative else None,
        }

    def corr(left, right):
        points = [
            (row[left], row[right]) for row in session_modalities
            if row[left] is not None and row[right] is not None
        ]
        if len(points) < 3:
            return {"n": len(points), "r": None}
        array = np.asarray(points)
        return {"n": len(points), "r": float(np.corrcoef(array.T)[0, 1])}

    modality_means = {}
    for name, features in {"text": TEXT, "audio": AUDIO, "video": VIDEO}.items():
        normal = [feature_stats[f]["mean"] for f in features if feature_stats[f]["mean"] is not None]
        corrected = [
            feature_stats[f]["mean_failure_excluded"]
            for f in features if feature_stats[f]["mean_failure_excluded"] is not None
        ]
        modality_means[name] = {
            "mean": statistics.fmean(normal) if normal else None,
            "failure_excluded": statistics.fmean(corrected) if corrected else None,
        }

    return {
        "sessions": evaluated_sessions,
        "records": len(records),
        "outcome": outcome,
        "feature_stats": feature_stats,
        "modality_means": modality_means,
        "correlations": {
            "text_audio": corr("text", "audio"),
            "text_video": corr("text", "video"),
            "audio_video": corr("audio", "video"),
        },
        "score_n": len(score_values),
        "score_mean": statistics.fmean(score_values) if score_values else None,
        "category_scores": {
            key: {"n": len(values), "mean": statistics.fmean(values)}
            for key, values in category_scores.items()
        },
    }


def horizontal_bars(rows, max_value=None, color="#1769aa", suffix=""):
    if max_value is None:
        max_value = max((value for _, value in rows), default=1)
    output = []
    for label, value in rows:
        width = min(100, pct(value, max_value))
        output.append(
            f"<div class='bar-row'><div class='bar-label'>{esc(label)}</div>"
            f"<div class='bar-track'><span style='width:{width:.2f}%;background:{color}'></span></div>"
            f"<div class='bar-value'>{esc(fmt(value, 1) if isinstance(value, float) else value)}{esc(suffix)}</div></div>"
        )
    return "".join(output)


def stacked_bar(parts):
    total = sum(value for _, value, _ in parts) or 1
    spans = []
    legend = []
    for label, value, color in parts:
        share = pct(value, total)
        spans.append(
            f"<span style='width:{share:.3f}%;background:{color}' title='{esc(label)} {value} ({share:.1f}%)'></span>"
        )
        legend.append(
            f"<span class='legend-item'><i style='background:{color}'></i>{esc(label)} "
            f"<b>{value}</b> <small>{share:.1f}%</small></span>"
        )
    return f"<div class='stacked'>{''.join(spans)}</div><div class='legend'>{''.join(legend)}</div>"


def status_cell(mark, text=""):
    cls = {"✓": "done", "△": "partial", "—": "none"}[mark]
    return f"<td class='matrix-cell {cls}'><b>{mark}</b>{('<span>'+esc(text)+'</span>') if text else ''}</td>"


def build_report():
    sessions = load_sessions()
    users = Counter(session["user"] for session in sessions)
    statuses = Counter((session["log"].get("status") or "unknown") for session in sessions)
    styles = Counter((session["log"].get("interview_style") or "unknown") for session in sessions)
    positions = Counter(
        (session["log"].get("position_name") or "未填写").strip() for session in sessions
    )
    companies = {
        (session["log"].get("company_name") or "").strip().casefold()
        for session in sessions if (session["log"].get("company_name") or "").strip()
    }
    categories = Counter(
        question.get("category") or "unknown"
        for session in sessions for question in session["questions"]
    )
    total_questions = sum(categories.values())
    answered_records = sum(
        bool((question.get("answer") or "").strip())
        for session in sessions for question in session["questions"]
    )
    core_categories = {"Self Introduction", "Behavioral", "Skill QA", "Scenario"}
    complete_flows = sum(
        core_categories | {"Candidate Questions"}
        <= {question.get("category") for question in session["questions"]}
        for session in sessions
    )
    jd_sessions = sum(bool((session["log"].get("job_description") or "").strip()) for session in sessions)
    cv_sessions = sum(
        (session["path"] / "uploads").exists()
        and any((session["path"] / "uploads").glob("*.pdf"))
        for session in sessions
    )
    media = {
        extension: sum(
            sum(1 for _ in session["path"].rglob(f"*.{extension}"))
            for session in sessions
        )
        for extension in ("wav", "webm", "mp4")
    }

    alignment_items = []
    category_alignment = {}
    for session in sessions:
        log = session["log"]
        jd = (log.get("job_description") or "").strip()
        position = (log.get("position_name") or "").strip()
        query = " ".join(
            q["question"] for q in session["questions"]
            if q.get("category") != "Candidate Questions"
        ).strip()
        if jd and position and query:
            alignment_items.append({
                "query": query,
                "reference": jd,
                "group": position,
                "questions": session["questions"],
            })
    role_alignment = alignment_metrics(alignment_items, "query", "reference", "group")
    for category in CATEGORIES[:-1]:
        items = []
        for item in alignment_items:
            query = " ".join(
                q["question"] for q in item["questions"]
                if q.get("category") == category
            ).strip()
            if query:
                items.append({
                    "query": query,
                    "reference": item["reference"],
                    "group": item["group"],
                })
        category_alignment[category] = alignment_metrics(items, "query", "reference", "group")
    cv_alignment = extract_cv_alignment(sessions)

    gating = defaultdict(Counter)
    gating_denominator = Counter()
    for session in sessions:
        for question in session["questions"]:
            category = question.get("category") or "unknown"
            gating_denominator[category] += 1
            for aspect in question.get("applicable_aspects") or []:
                gating[category][aspect] += 1

    followups = analyze_followups(sessions)
    evaluation = analyze_evaluations(sessions)

    locked = json.loads((ANALYSIS / "corpus_stats.json").read_text(encoding="utf-8"))
    legacy_users, legacy_sessions = 77, 185
    locked_manifest = list(csv.DictReader((ANALYSIS / "manifest_clean.csv").open()))
    current_keys = {(session["user"], session["session"]) for session in sessions}
    locked_keys = {(row["user"], row["session_id"]) for row in locked_manifest}
    locked_missing_now = len(locked_keys - current_keys)
    current_new = len(current_keys - locked_keys)

    answered_feature_rows = {}
    with (ANALYSIS / "eval_feature_stats_clean.csv").open() as handle:
        for row in csv.DictReader(handle):
            answered_feature_rows[row["feature"]] = row
    answered_category_rows = []
    with (ANALYSIS / "eval_per_category_clean.csv").open() as handle:
        answered_category_rows = list(csv.DictReader(handle))

    top_positions = positions.most_common(10)
    unique_positions = len({name.casefold() for name in positions if name != "未填写"})
    returning_users = sum(count >= 2 for count in users.values())
    session_counts = list(users.values())

    # De-identified excerpts from generated questions; no answers, CV text, or user IDs.
    role_examples = [
        (
            "数据分析师",
            "技能题",
            "When cleaning data in SQL, what are the first three things you typically check for—and why?",
        ),
        (
            "软件工程师",
            "情景题",
            "Imagine you’re asked to redesign part of a legacy system serving billions of users—how would you balance speed, reliability, and team velocity while ensuring no regression in core functionality?",
        ),
        (
            "AI 研究助理",
            "技能题",
            "How would you decide between PyTorch and JAX for a new deep learning project focused on reproducibility and rapid prototyping?",
        ),
        (
            "土木工程毕业生",
            "情景题",
            "Imagine you’re supporting the design of a new urban footbridge in a flood-prone area—how would you balance safety, sustainability, and stakeholder input in your early recommendations?",
        ),
        (
            "学校辅导员",
            "技能题",
            "How do you integrate MTSS and trauma-informed care when designing tiered interventions for a student showing signs of anxiety and declining academic engagement?",
        ),
        (
            "定性 UX 研究员",
            "情景题",
            "Imagine the design team disagrees with your research finding because it conflicts with their assumptions—how would you present and advocate for your insight?",
        ),
    ]

    demo_rows = [
        ("LM-Interview", ("✓", "任务实验"), ("✓", "专家比较"), ("△", "7人"), ("—", ""), ("—", ""), ("—", ""), ("△", "分析解释"), ("—", ""), ("✓", "规划与追问")),
        ("EmpathyEar", ("✓", "自动指标"), ("✓", "人评"), ("△", "查询级"), ("—", ""), ("—", ""), ("△", "组件"), ("✓", "推理链"), ("—", ""), ("△", "多模态")),
        ("OpenOmni", ("✓", "准确率"), ("✓", "标注"), ("—", ""), ("✓", "在线Demo"), ("✓", "延迟/隐私"), ("✓", "配置比较"), ("✓", "监控面板"), ("✓", "瓶颈"), ("—", "")),
        ("AutoGen Studio", ("—", ""), ("△", "Issue分析"), ("✓", "使用反馈"), ("✓", "20万下载"), ("—", ""), ("—", ""), ("✓", "调试/Profiling"), ("✓", "错误诊断"), ("△", "工作流模板")),
        ("iPET", ("✓", "离线评测"), ("△", "个案"), ("✓", "在线A/B"), ("✓", "百万用户"), ("△", "工程"), ("△", "模块"), ("—", ""), ("—", ""), ("✓", "记忆与偏好")),
        ("AgentMaster", ("✓", "BERTScore/G-Eval"), ("✓", "人评"), ("△", "23查询"), ("✓", "AWS原型"), ("△", ""), ("—", ""), ("△", "路由可见"), ("△", "误分类"), ("✓", "动态路由")),
        ("MathBuddy", ("✓", "8维指标"), ("✓", "人评"), ("✓", "30人"), ("△", "实时原型"), ("✓", "实时识别"), ("✓", "消融"), ("✓", "理论映射"), ("✓", "60%识别"), ("✓", "情感适配")),
        ("AERA Chat", ("✓", "多数据集"), ("✓", "Rationale"), ("✓", "16人"), ("✓", "在线Demo"), ("—", ""), ("✓", "模型比较"), ("✓", "高亮/编辑"), ("✓", "解释可靠性"), ("△", "交互追问")),
        ("Metamo", ("✓", "公共语料"), ("✓", "人评"), ("✓", "38人"), ("✓", "浏览器Demo"), ("✓", "成本/延迟"), ("✓", "敏感性"), ("✓", "标签/头像"), ("✓", "安全层"), ("✓", "认知教练")),
        ("LearnLens", ("✓", "Agent评测"), ("✓", "教师参与"), ("✓", "30人"), ("✓", "在线Demo"), ("✓", "成本/延迟"), ("△", "Verifier"), ("✓", "教师可修正"), ("△", "Verifier"), ("✓", "课程个性化")),
        ("PolyInterview", ("✓", "岗位贴合/日志"), ("△", "9名教师自报"), ("△", "129人自报"), ("✓", "真实部署"), ("—", "未实测"), ("—", "未完成"), ("✓", "13→10→2追踪"), ("✓", "失败审计"), ("✓", "岗位+追问")),
    ]

    demo_matrix = []
    for name, *cells in demo_rows:
        demo_matrix.append(
            f"<tr><th>{esc(name)}</th>" + "".join(status_cell(*cell) for cell in cells) + "</tr>"
        )

    gating_header = "".join(f"<th>{esc(label)}</th>" for label in ASPECT_LABELS.values())
    gating_rows = []
    for category in CATEGORIES:
        cells = []
        denominator = gating_denominator[category]
        for aspect in ASPECT_LABELS:
            value = pct(gating[category][aspect], denominator)
            alpha = 0.06 + 0.66 * value / 100
            text_color = "#ffffff" if value >= 72 else "#17212b"
            cells.append(
                f"<td style='background:rgba(23,105,170,{alpha:.3f});color:{text_color}'>{value:.0f}%</td>"
            )
        gating_rows.append(
            f"<tr><th>{esc(CATEGORY_ZH[category])}<small>{esc(category)}</small></th>{''.join(cells)}</tr>"
        )

    feature_rows = []
    feature_colors = {**{f: "#1769aa" for f in TEXT}, **{f: "#16865c" for f in AUDIO}, **{f: "#c76b14" for f in VIDEO}}
    for feature in ALL_FEATURES:
        stats = evaluation["feature_stats"][feature]
        answered = answered_feature_rows.get(feature, {})
        mean_answered = float(answered["mean_answered"]) if answered.get("mean_answered") else None
        corrected = stats["mean_failure_excluded"]
        feature_rows.append(
            f"<tr><th>{esc(FEATURE_LABELS[feature])}<small>{esc(feature)}</small></th>"
            f"<td><span class='modality-dot' style='background:{feature_colors[feature]}'></span>"
            f"{'文本' if feature in TEXT else '音频' if feature in AUDIO else '视频'}</td>"
            f"<td>{stats['n']}</td><td>{fmt(stats['mean'], 2)}</td>"
            f"<td>{fmt(mean_answered, 2)}</td>"
            f"<td>{fmt(corrected, 2) if feature in VIDEO else '同左'}</td></tr>"
        )

    category_rows = []
    for row in answered_category_rows:
        category_rows.append(
            f"<tr><th>{esc(CATEGORY_ZH.get(row['cat'], row['cat']))}</th>"
            f"<td>{row['n']}</td><td>{row['answered']}</td><td>{float(row['answered_rate'])*100:.0f}%</td>"
            f"<td>{float(row['mean_answered']):.2f}</td></tr>"
        )

    role_example_html = "".join(
        f"<article class='example'><div><b>{esc(role)}</b><span>{esc(category)}</span></div><p>{esc(question)}</p></article>"
        for role, category, question in role_examples
    )

    status_parts = [
        ("已完成", statuses.get("completed", 0), "#16865c"),
        ("断开", statuses.get("disconnected", 0), "#c76b14"),
        ("进行中", statuses.get("in_progress", 0), "#1769aa"),
    ]
    style_rows = [(key.title(), value) for key, value in styles.most_common()]
    category_bar_rows = [(CATEGORY_ZH.get(key, key), categories[key]) for key in CATEGORIES]

    video_total = sum(evaluation["outcome"].values())
    captured = evaluation["outcome"]["failed"] + evaluation["outcome"]["ok"]
    video_parts = [
        ("VLM成功", evaluation["outcome"]["ok"], "#16865c"),
        ("VLM失败并记0", evaluation["outcome"]["failed"], "#c23d4b"),
        ("未捕获视频", evaluation["outcome"]["no_video"], "#9aa7b2"),
    ]

    modality_rows = [
        ("音频", evaluation["modality_means"]["audio"]["mean"]),
        ("视频（原始）", evaluation["modality_means"]["video"]["mean"]),
        ("视频（排除VLM失败）", evaluation["modality_means"]["video"]["failure_excluded"]),
        ("文本", evaluation["modality_means"]["text"]["mean"]),
    ]

    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    role_ratio = role_alignment["matched_median"] / max(role_alignment["baseline_median"], 1e-9)
    cv_note = (
        f"N={cv_alignment['n']}；匹配中位数 {cv_alignment['matched_median']:.3f}，跨用户基线 "
        f"{cv_alignment['baseline_median']:.3f}；{cv_alignment['win_rate']*100:.1f}% 高于基线。"
        if cv_alignment else "可提取 CV 样本不足，未计算。"
    )

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PolyInterview 综合用户与系统证据分析</title>
<style>
:root{{--ink:#17212b;--muted:#5d6b76;--line:#d9e1e6;--bg:#f4f7f8;--paper:#fff;--blue:#1769aa;--green:#16865c;--orange:#c76b14;--red:#c23d4b;--gray:#9aa7b2;}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;color:var(--ink);background:var(--bg);font-family:Inter,"PingFang SC","Microsoft YaHei",Arial,sans-serif;line-height:1.55;letter-spacing:0}}
a{{color:inherit}}.top{{position:sticky;top:0;z-index:20;background:#fff;border-bottom:1px solid var(--line)}}.top-inner{{max-width:1240px;margin:auto;padding:10px 22px;display:flex;align-items:center;gap:18px}}.brand{{font-weight:800;white-space:nowrap}}.brand i{{display:inline-block;width:10px;height:10px;background:var(--green);margin-right:8px}}nav{{display:flex;gap:4px;overflow:auto;scrollbar-width:none}}nav a{{font-size:13px;text-decoration:none;color:var(--muted);padding:7px 9px;white-space:nowrap;border-radius:4px}}nav a:hover{{background:#edf3f6;color:var(--ink)}}
.hero{{background:#fff;border-bottom:1px solid var(--line)}}.hero-inner{{max-width:1240px;margin:auto;padding:54px 22px 42px;display:grid;grid-template-columns:minmax(0,1.5fr) minmax(300px,.7fr);gap:44px;align-items:end}}.eyebrow{{font-size:12px;color:var(--blue);font-weight:800;text-transform:uppercase;margin:0 0 10px}}h1{{font-size:42px;line-height:1.12;margin:0 0 16px;max-width:900px}}.lede{{font-size:18px;color:#34434e;max-width:820px;margin:0}}.hero-note{{border-left:4px solid var(--orange);padding:4px 0 4px 16px;color:#34434e}}.hero-note b{{display:block;margin-bottom:5px}}.hero-note p{{margin:0;font-size:14px}}main{{max-width:1240px;margin:auto;padding:0 22px 70px}}section{{padding:42px 0;border-bottom:1px solid var(--line)}}h2{{font-size:27px;margin:0 0 8px}}h3{{font-size:18px;margin:28px 0 10px}}h4{{font-size:15px;margin:0 0 10px}}.section-intro{{color:var(--muted);max-width:900px;margin:0 0 24px}}.grid-4{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.grid-3{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}}.grid-2{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.metric,.panel,.claim,.example{{background:var(--paper);border:1px solid var(--line);border-radius:6px}}.metric{{padding:18px;min-height:118px}}.metric b{{font-size:31px;line-height:1;display:block;margin:4px 0 9px}}.metric span{{font-size:13px;color:var(--muted)}}.metric small{{display:block;font-size:11px;color:var(--muted);margin-bottom:8px;text-transform:uppercase}}.panel{{padding:20px}}.panel p:last-child{{margin-bottom:0}}.callout{{border-left:4px solid var(--blue);background:#fff;padding:18px 20px;margin:20px 0}}.callout.warn{{border-color:var(--orange)}}.callout.danger{{border-color:var(--red)}}.callout.success{{border-color:var(--green)}}.callout p{{margin:4px 0}}.bar-row{{display:grid;grid-template-columns:minmax(95px,1.25fr) minmax(120px,3fr) 52px;gap:10px;align-items:center;margin:9px 0;font-size:13px}}.bar-label{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}.bar-track{{height:10px;background:#edf1f3;overflow:hidden}}.bar-track span{{display:block;height:100%;min-width:2px}}.bar-value{{font-variant-numeric:tabular-nums;text-align:right;font-weight:700}}.stacked{{height:28px;background:#edf1f3;display:flex;overflow:hidden;margin:12px 0}}.stacked span{{height:100%}}.legend{{display:flex;flex-wrap:wrap;gap:12px 18px;font-size:12px;color:var(--muted)}}.legend-item i{{display:inline-block;width:9px;height:9px;margin-right:6px}}.legend-item b{{color:var(--ink);margin-left:3px}}.legend-item small{{margin-left:2px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:10px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:13px}}thead th{{font-size:11px;text-transform:uppercase;color:var(--muted);background:#f7f9fa;position:sticky;top:46px;z-index:2}}tbody th{{font-weight:700}}tbody th small{{display:block;color:var(--muted);font-weight:400}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:6px;background:#fff}}.matrix{{min-width:1180px}}.matrix th:first-child{{position:sticky;left:0;background:#fff;z-index:3;min-width:140px}}.matrix thead th:first-child{{background:#f7f9fa;z-index:4}}.matrix-cell{{text-align:center;min-width:104px}}.matrix-cell b{{display:block;font-size:17px}}.matrix-cell span{{display:block;font-size:10px;color:var(--muted)}}.matrix-cell.done b{{color:var(--green)}}.matrix-cell.partial b{{color:var(--orange)}}.matrix-cell.none b{{color:var(--gray)}}.heatmap{{min-width:1040px}}.heatmap td{{text-align:center;font-variant-numeric:tabular-nums}}.modality-dot{{width:8px;height:8px;display:inline-block;margin-right:7px}}.examples{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.example{{padding:16px}}.example div{{display:flex;justify-content:space-between;gap:10px}}.example div span{{font-size:11px;color:var(--blue);font-weight:700}}.example p{{font-family:Georgia,"Times New Roman",serif;margin:10px 0 0;color:#293842}}.claim-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}.claim{{padding:17px;border-left-width:4px}}.claim strong{{display:block;margin-bottom:6px}}.claim p{{margin:4px 0;color:#34434e;font-size:14px}}.claim em{{font-style:normal;font-size:11px;font-weight:800;text-transform:uppercase}}.claim.good{{border-left-color:var(--green)}}.claim.medium{{border-left-color:var(--blue)}}.claim.limit{{border-left-color:var(--orange)}}.claim.stop{{border-left-color:var(--red)}}.good em{{color:var(--green)}}.medium em{{color:var(--blue)}}.limit em{{color:var(--orange)}}.stop em{{color:var(--red)}}.pipeline{{display:grid;grid-template-columns:1.35fr 48px 1fr 48px .75fr;align-items:stretch;gap:8px}}.pipe-block{{background:#fff;border:1px solid var(--line);padding:18px;border-radius:6px}}.pipe-block b{{display:block;font-size:24px}}.pipe-block span{{color:var(--muted);font-size:13px}}.arrow{{display:grid;place-items:center;font-size:26px;color:var(--gray)}}.mini-list{{margin:10px 0 0;padding-left:18px;font-size:13px}}.mini-list li{{margin:5px 0}}.tag{{display:inline-block;padding:2px 6px;border:1px solid var(--line);border-radius:3px;font-size:10px;color:var(--muted);margin:2px 3px 2px 0}}details{{background:#fff;border:1px solid var(--line);border-radius:6px;padding:13px 16px;margin:10px 0}}summary{{cursor:pointer;font-weight:700}}details p,details li{{font-size:13px;color:#34434e}}code{{background:#edf2f4;padding:2px 5px;border-radius:3px}}.foot{{color:var(--muted);font-size:12px;margin-top:20px}}.nowrap{{white-space:nowrap}}.num{{font-variant-numeric:tabular-nums}}@media(max-width:900px){{.hero-inner{{grid-template-columns:1fr}}h1{{font-size:34px}}.grid-4,.grid-3{{grid-template-columns:repeat(2,minmax(0,1fr))}}.grid-2,.claim-grid,.examples{{grid-template-columns:1fr}}.pipeline{{grid-template-columns:1fr}}.arrow{{transform:rotate(90deg);height:34px}}}}@media(max-width:560px){{.top-inner{{display:block}}nav{{margin-top:7px}}.hero-inner{{padding-top:34px}}h1{{font-size:29px}}.grid-4,.grid-3{{grid-template-columns:1fr}}main{{padding-left:14px;padding-right:14px}}.bar-row{{grid-template-columns:92px 1fr 45px}}}}@media print{{.top{{display:none}}body{{background:#fff}}section{{break-inside:avoid}}.hero-inner,main{{max-width:none}}.panel,.metric,.claim,.example{{box-shadow:none}}}}
</style>
</head>
<body>
<header class="top"><div class="top-inner"><div class="brand"><i></i>PolyInterview Evidence Report</div><nav aria-label="报告导航"><a href="#summary">结论</a><a href="#provenance">口径</a><a href="#usage">使用</a><a href="#personalization">个性化</a><a href="#followup">追问</a><a href="#assessment">评估</a><a href="#reliability">可靠性</a><a href="#pilot">用户反馈</a><a href="#comparison">Demo对比</a><a href="#claims">论文主张</a></nav></div></header>
<div class="hero"><div class="hero-inner"><div><p class="eyebrow">User, interaction, assessment and deployment evidence</p><h1>PolyInterview 综合用户与系统证据分析</h1><p class="lede">从“有多少用户”进一步回答：系统是否生成岗位贴合的问题、是否真的发生答案驱动追问、评估是否覆盖文本/语音/视频、解释链是否帮助发现真实部署故障，以及这些证据在同类 Demo Paper 中处于什么位置。</p></div><aside class="hero-note"><b>报告原则</b><p>优势必须对应可复算证据；相关性不等于效度；失败审计既是限制，也是可观测、可诊断系统设计的证据。</p><p class="foot">生成时间：{report_date}<br>数据截至：当前本地日志 2026-06-26</p></aside></div></div>
<main>
<section id="summary"><p class="eyebrow">Executive summary</p><h2>结论先行</h2><p class="section-intro">现有数据最有力地支持四项系统优势，同时也清楚指出三项尚不能宣称已经验证的能力。</p>
<div class="claim-grid">
<article class="claim good"><em>证据较强</em><strong>生成问题具有明显岗位/JD区分度</strong><p>{role_alignment['n']} 场可比较会话中，问题集与匹配 JD 的词汇相似度中位数是跨岗位基线的 {role_ratio:.1f} 倍；{role_alignment['rank_one_rate']*100:.1f}% 的问题集对自己的 JD 比对任何其他岗位 JD 都更接近。</p></article>
<article class="claim good"><em>证据较强</em><strong>评估覆盖广，而且按题型选择维度</strong><p>系统落实 13 个行为特征、10 个 KSA 方面、2 条能力轨道；{complete_flows}/{len(sessions)} 场会话包含完整五阶段，所有可评分题型都带有适用 aspect，而候选人反问阶段不强行评分。</p></article>
<article class="claim medium"><em>探索性证据</em><strong>追问确实读取了上一轮回答</strong><p>{followups['answered_records']} 条有回答记录中，{followups['records_with_followup']} 条触发追问，共保留 {followups['followup_turns']} 个追问 turn；追问与其真实前序回答的匹配度在 {followups['grounding']['win_rate']*100:.1f}% 的样本中高于错配基线。</p></article>
<article class="claim good"><em>系统设计优势</em><strong>特征级追踪把聚合分数会掩盖的故障暴露出来</strong><p>当前严格清洗快照中，非语言评估在 {evaluation['outcome']['failed']}/{video_total}（{pct(evaluation['outcome']['failed'],video_total):.1f}%）个问题上失败并写入 0；排除失败后，视频均值由 {evaluation['modality_means']['video']['mean']:.2f} 升至 {evaluation['modality_means']['video']['failure_excluded']:.2f}。</p></article>
<article class="claim limit"><em>证据较弱</em><strong>CV 个性化尚不能像 JD 贴合那样强宣称</strong><p>{cv_note} 样本小、词汇重叠弱，只能作为初步信号；需要人工配对判断或语义评价才能证明 CV 细节被正确使用。</p></article>
<article class="claim stop"><em>尚未验证</em><strong>不能据此声称“评分有效”或“显著提升面试能力”</strong><p>目前没有专家金标准一致性、控制组、前后测学习增益或公平性评估。129 人反馈支持可接受性，不支持 criterion validity 或 learning effectiveness。</p></article>
</div></section>

<section id="provenance"><p class="eyebrow">Data provenance</p><h2>先把三套数据口径分开</h2><p class="section-intro">旧 HTML、论文锁定语料和当前后端目录并不是同一快照。混用会造成用户数、会话数、评分问题数互相矛盾。</p>
<div class="grid-3">
<article class="panel"><h3>旧版 v3 仪表板</h3><p><b>{legacy_users} 用户 / {legacy_sessions} 会话</b></p><p>只排除 24 个种子/显式测试账号，仍包含研究团队自测及占位账号。保留它作为字段和旧统计参考，不用于优势结论。</p><span class="tag">legacy</span><span class="tag">宽松清洗</span></article>
<article class="panel"><h3>论文锁定快照</h3><p><b>{locked['meta']['users_clean']} 用户 / {locked['meta']['sessions_clean']} 会话</b></p><p>排除 39 个测试、自测和占位账号；包含 {locked['meta']['pooled_eval_questions']} 个评分问题。论文中的 31.8% 视频失败率来自此快照。</p><span class="tag">paper-locked</span><span class="tag">可复现</span></article>
<article class="panel"><h3>当前严格清洗快照</h3><p><b>{len(users)} 用户 / {len(sessions)} 会话</b></p><p>对当前 <code>backend/users</code> 继续使用同一 39 账号排除规则，覆盖至 6 月 26 日；以下新增分析主要基于该快照。</p><span class="tag">current</span><span class="tag">严格清洗</span></article>
</div>
<div class="callout warn"><b>版本关系：</b><p>当前目录与论文锁定清单重合 {len(current_keys & locked_keys)} 场；锁定清单中的 {locked_missing_now} 场日志当前不在目录中，当前目录另有 {current_new} 场新增日志。因此应把它们视作两个版本化语料，而不是简单把 120 更新成 139。</p></div>
<details><summary>严格清洗规则</summary><p>排除四类账号：显式 test 命名；早期整数种子账号；占位/垃圾名称；研究团队自测账号。完整 39 账号集合保留在生成脚本中，但 HTML 不展示用户名或个人信息。</p></details>
</section>

<section id="usage"><p class="eyebrow">Usage and workflow coverage</p><h2>用户、会话与完整工作流</h2><p class="section-intro">这里区分“会话被创建”“完成一次流程”“留下可分析回答”“产生评估”四个层级，避免把启动页面访问当成完整使用。</p>
<div class="grid-4">
<article class="metric"><small>严格清洗用户</small><b>{len(users)}</b><span>{returning_users} 人使用至少 2 场，回访用户占 {pct(returning_users,len(users)):.1f}%</span></article>
<article class="metric"><small>会话与完成</small><b>{len(sessions)}</b><span>{statuses.get('completed',0)} 场标记 completed，完成率 {pct(statuses.get('completed',0),len(sessions)):.1f}%</span></article>
<article class="metric"><small>生成问题</small><b>{total_questions}</b><span>{complete_flows} 场包含完整五阶段，占 {pct(complete_flows,len(sessions)):.1f}%</span></article>
<article class="metric"><small>可评估记录</small><b>{evaluation['records']}</b><span>来自 {evaluation['sessions']} 场会话；另有 {answered_records} 条日志回答记录</span></article>
</div>
<div class="grid-2" style="margin-top:16px">
<article class="panel"><h3>会话状态</h3>{stacked_bar(status_parts)}<p class="foot">“断开”可能同时包含主动离开和技术中断，不能直接解释为用户不满意。</p></article>
<article class="panel"><h3>面试风格</h3>{horizontal_bars(style_rows, max(styles.values()) if styles else 1, '#1769aa')}</article>
<article class="panel"><h3>五阶段问题覆盖</h3>{horizontal_bars(category_bar_rows, max(categories.values()) if categories else 1, '#16865c')}<p class="foot">五类问题数量接近，说明生成器不是只产出泛化自我介绍题。</p></article>
<article class="panel"><h3>岗位覆盖</h3>{horizontal_bars(top_positions, max(positions.values()) if positions else 1, '#c76b14')}<p class="foot">共 {unique_positions} 个不同岗位标题、{len(companies)} 个公司/组织输入；长尾岗位包括金融、设计、教育、工程和医疗。</p></article>
</div>
<div class="callout"><b>多模态数据资产：</b><p>当前严格快照包含 {media['wav']} 个 WAV、{media['webm']} 个 WebM 和 {media['mp4']} 个 MP4 文件。三种格式可能来自同一回答或追问，不能相加当成独立样本。</p></div>
</section>

<section id="personalization"><p class="eyebrow">Personalization and job fit</p><h2>问题是否真的贴合不同岗位</h2><p class="section-intro">用每场非候选人反问题目组成“问题文档”，与本场 JD 做 TF-IDF 词/双词组余弦相似度；对照为同一问题集与所有不同岗位 JD 的相似度中位数。</p>
<div class="grid-4">
<article class="metric"><small>可比较会话</small><b>{role_alignment['n']}</b><span>{jd_sessions}/{len(sessions)} 场具有 JD；每场都生成岗位与题型信息</span></article>
<article class="metric"><small>匹配 JD 中位数</small><b>{role_alignment['matched_median']:.3f}</b><span>跨岗位错配基线 {role_alignment['baseline_median']:.3f}，约 {role_ratio:.1f} 倍</span></article>
<article class="metric"><small>胜过错配基线</small><b>{role_alignment['win_rate']*100:.1f}%</b><span>平均提升 {role_alignment['delta_mean']:.3f}，95% bootstrap CI [{role_alignment['ci_low']:.3f}, {role_alignment['ci_high']:.3f}]</span></article>
<article class="metric"><small>跨岗位 Rank-1</small><b>{role_alignment['rank_one_rate']*100:.1f}%</b><span>匹配 JD 比任何不同岗位 JD 都更接近的会话比例</span></article>
</div>
<div class="grid-2" style="margin-top:16px">
<article class="panel"><h3>匹配与错配对照</h3>{horizontal_bars([('匹配本场 JD',role_alignment['matched_median']),('不同岗位 JD 基线',role_alignment['baseline_median'])], role_alignment['matched_median'], '#1769aa')}<p class="foot">余弦值绝对数不高是因为问题比 JD 短；关键证据是同一表示空间中的配对差异。</p></article>
<article class="panel"><h3>各题型高于错配基线的比例</h3>{horizontal_bars([(CATEGORY_ZH[key], category_alignment[key]['win_rate']*100) for key in CATEGORIES[:-1]],100,'#16865c','%')}<p class="foot">自我介绍、行为、技能与情景题都显示岗位区分度；情景题措辞更开放，因此词汇重叠最低。</p></article>
</div>
<h3>不同岗位的实际问题片段</h3><div class="examples">{role_example_html}</div>
<div class="callout success"><b>可支持的论文表述：</b><p>“Generated question sets are lexically more aligned with their matched job descriptions than with descriptions from other roles.” 这是岗位/JD 贴合证据，不等同于专家判定的题目质量。</p></div>
<div class="callout warn"><b>CV 个性化边界：</b><p>{cv_note} 目前只够说明“可能利用了部分 CV 信息”，不宜写成“validated CV personalization”。建议下一轮让 HR/教师对匹配 CV 与错配 CV 的问题对进行盲评。</p></div>
</section>

<section id="followup"><p class="eyebrow">Adaptive interaction</p><h2>答案驱动追问是否发生</h2><p class="section-intro">日志把主问题、回答和追问保存在同一 transcript 中。我们统计追问标记，并比较追问与真实前序回答、错配回答之间的词汇联系。</p>
<div class="grid-4">
<article class="metric"><small>有回答的问题记录</small><b>{followups['answered_records']}</b><span>当前严格清洗快照</span></article>
<article class="metric"><small>触发追问</small><b>{followups['records_with_followup']}</b><span>占 {pct(followups['records_with_followup'],followups['answered_records']):.1f}%；无须对每个充分回答强行追问</span></article>
<article class="metric"><small>追问 turn</small><b>{followups['followup_turns']}</b><span>日志标记总数；包含深层模式中的重复记录</span></article>
<article class="metric"><small>回答-追问 grounding</small><b>{followups['grounding']['win_rate']*100:.1f}%</b><span>真实前序回答匹配度高于错配基线</span></article>
</div>
<div class="grid-2" style="margin-top:16px">
<article class="panel"><h3>追问深度分布</h3>{horizontal_bars([(f'{depth} 次',count) for depth,count in sorted(followups['depth_counts'].items())], max(followups['depth_counts'].values()) if followups['depth_counts'] else 1, '#1769aa')}</article>
<article class="panel"><h3>按风格的持久化标记</h3><table><thead><tr><th>风格</th><th>回答记录</th><th>0次</th><th>1次</th><th>2次</th><th>3次</th><th>6/9次</th></tr></thead><tbody>{''.join(f"<tr><th>{esc(style.title())}</th><td>{sum(counter.values())}</td><td>{counter.get(0,0)}</td><td>{counter.get(1,0)}</td><td>{counter.get(2,0)}</td><td>{counter.get(3,0)}</td><td>{counter.get(6,0)+counter.get(9,0)}</td></tr>" for style,counter in sorted(followups['by_style'].items()))}</tbody></table></article>
</div>
<div class="callout warn"><b>重要日志发现：</b><p>Basic 的所有持久化记录都不超过 1 次追问；但 Intermediate/Advanced 中出现 6 或 9 个追问标记，超过名义深度上限。它可能是重复序列化，也可能是真实重复追问。修复日志 schema 前，数据支持“发生了 answer-aware probing”，但不能支持“深度上限始终被正确执行”。</p></div>
</section>

<section id="assessment"><p class="eyebrow">Comprehensive and selective assessment</p><h2>全面，不等于把所有维度 indiscriminately 打一遍</h2><p class="section-intro">PolyInterview 的优势是两层同时成立：覆盖文本、音频、视频的 13 个 feature；再依据题型选择相关 KSA aspects，聚合成专业与沟通两条能力轨道。</p>
<div class="pipeline"><div class="pipe-block"><b>13</b><span>行为特征</span><ul class="mini-list"><li>文本：专业表现 3 + 表达方式 3</li><li>视频：眼神、表情、姿态、手势 4</li><li>音频：发音、韵律、流利度 3</li></ul></div><div class="arrow">→</div><div class="pipe-block"><b>10</b><span>KSA aspects</span><ul class="mini-list"><li>认知 3</li><li>背景 3</li><li>社会与沟通 4</li></ul></div><div class="arrow">→</div><div class="pipe-block"><b>2</b><span>能力轨道</span><ul class="mini-list"><li>Professional</li><li>Communication</li></ul></div></div>
<h3>题型与适用 aspect 的实际映射比例</h3><div class="table-wrap"><table class="heatmap"><thead><tr><th>题型</th>{gating_header}</tr></thead><tbody>{''.join(gating_rows)}</tbody></table></div><p class="foot">单元格表示该题型中声明该 aspect 为 applicable 的问题比例。候选人反问阶段保持空白，符合“不评分”的设计。</p>
<h3>13 个 feature 在当前评估语料中的表现</h3><div class="table-wrap"><table><thead><tr><th>Feature</th><th>模态</th><th>N</th><th>全体均值</th><th>有回答均值*</th><th>排除VLM失败</th></tr></thead><tbody>{''.join(feature_rows)}</tbody></table></div><p class="foot">*“有回答均值”来自 <code>eval_feature_stats_clean.csv</code> 的 115 条回答子集；视频均值仍包含未捕获视频的 0。不同 evaluator 的标度尚未校准，不应直接用高低判断候选人哪一方面最好。</p>
<div class="grid-2" style="margin-top:16px">
<article class="panel"><h3>模态均值</h3>{horizontal_bars(modality_rows,10,'#1769aa')}<p class="foot">音频明显偏宽松，文本偏低；这是跨 evaluator calibration 问题，不是候选人真实能力排序。</p></article>
<article class="panel"><h3>题型评分子集</h3><table><thead><tr><th>题型</th><th>评估N</th><th>有回答</th><th>回答率</th><th>有回答均值</th></tr></thead><tbody>{''.join(category_rows)}</tbody></table></article>
</div>
<div class="callout"><b>全面性证据：</b><p>13 个 feature 都在部署语料中产生过观测；四类可评分题型呈现不同 aspect 签名；文本-音频、文本-视频、音频-视频的 session-level 相关分别为 {evaluation['correlations']['text_audio']['r']:.2f}、{evaluation['correlations']['text_video']['r']:.2f}、{evaluation['correlations']['audio_video']['r']:.2f}。这支持模态承载非冗余信息，但不证明各分数已经有效或公平。</p></div>
</section>

<section id="reliability"><p class="eyebrow">Reliability audit</p><h2>真实部署最重要的发现：视频评分失败会伪装成低分</h2><p class="section-intro">聚合分数会把“候选人表现差”和“VLM 没有成功运行”都呈现为 0。特征级日志允许把两者拆开。</p>
<div class="panel">{stacked_bar(video_parts)}</div>
<div class="grid-4" style="margin-top:16px">
<article class="metric"><small>视频相关评估</small><b>{video_total}</b><span>当前严格清洗快照</span></article>
<article class="metric"><small>VLM成功</small><b>{evaluation['outcome']['ok']}</b><span>{pct(evaluation['outcome']['ok'],video_total):.1f}%</span></article>
<article class="metric"><small>有视频但失败</small><b>{evaluation['outcome']['failed']}</b><span>占全部 {pct(evaluation['outcome']['failed'],video_total):.1f}%；占捕获视频 {pct(evaluation['outcome']['failed'],captured):.1f}%</span></article>
<article class="metric"><small>没有视频</small><b>{evaluation['outcome']['no_video']}</b><span>{pct(evaluation['outcome']['no_video'],video_total):.1f}%</span></article>
</div>
<div class="grid-2" style="margin-top:16px"><article class="panel"><h3>论文锁定快照</h3><p><b>成功 22.7% / 失败 31.8% / 无视频 45.5%</b></p><p>论文应继续使用这个冻结数字，除非正式更新并重新冻结新语料。</p></article><article class="panel"><h3>当前严格快照</h3><p><b>成功 {pct(evaluation['outcome']['ok'],video_total):.1f}% / 失败 {pct(evaluation['outcome']['failed'],video_total):.1f}% / 无视频 {pct(evaluation['outcome']['no_video'],video_total):.1f}%</b></p><p>失败率没有自然消失，说明 retry、fallback 和 capture QA 应成为提交前后的首要工程工作。</p></article></div>
<div class="callout danger"><b>不能把失败当低表现：</b><p>排除明确 VLM failure 后，四个视频 feature 均值平均由 {evaluation['modality_means']['video']['mean']:.2f} 升到 {evaluation['modality_means']['video']['failure_excluded']:.2f}，提升 {pct(evaluation['modality_means']['video']['failure_excluded']-evaluation['modality_means']['video']['mean'],evaluation['modality_means']['video']['mean']):.1f}%。报告界面应把 “not captured / evaluator failed / scored zero” 显示为三个状态。</p></div>
</section>

<section id="pilot"><p class="eyebrow">Pilot feedback</p><h2>用户反馈支持可接受性，而不是学习效果</h2><p class="section-intro">两轮 pilot 共 129 名参与者，来自 6 所机构、8+ 学科，包括 9 名英语教学相关教师评审。</p>
<div class="grid-2"><article class="panel"><h3>第一轮认可项</h3>{horizontal_bars([('界面清晰',67.0),('数字人沉浸感',58.0),('报告深度',50.0),('个性化问题',42.0)],100,'#16865c','%')}</article><article class="panel"><h3>第二轮定性反馈</h3><ul class="mini-list"><li>高年级学生认为流程足够顺畅，可用于真实求职准备。</li><li>问题被描述为专业、与岗位相关。</li><li>数字人让面试更接近真实会话。</li></ul><p class="foot">这些是自报反馈，原始样本划分、量表和缺失数据仍应在论文中补齐。</p></article></div>
<div class="callout warn"><b>恰当表述：</b><p>“Participants reported that the workflow was usable and the questions felt relevant.” 不应改写成 “PolyInterview improves interview performance” 或 “users validated the scoring accuracy”。</p></div>
</section>

<section id="comparison"><p class="eyebrow">Comparison with 10 demo papers</p><h2>同类 Demo Paper 做了什么，我们做到了哪里</h2><p class="section-intro">矩阵依据本地 10 篇 ACL/EMNLP 2024–2025 Demo Paper 的正文评测设计。✓ 已覆盖；△ 部分覆盖或证据较弱；— 尚未覆盖。</p>
<div class="table-wrap"><table class="matrix"><thead><tr><th>Paper</th><th>自动/任务指标</th><th>人工/专家</th><th>用户研究</th><th>真实部署/A-B</th><th>延迟/成本</th><th>消融/敏感性</th><th>解释与界面</th><th>失败/可靠性</th><th>个性化/适配</th></tr></thead><tbody>{''.join(demo_matrix)}</tbody></table></div>
<div class="grid-3" style="margin-top:16px">
<article class="panel"><h3>PolyInterview 已有的强项</h3><ul class="mini-list"><li>真实部署而非离线 mock 数据。</li><li>岗位/JD 匹配对照，而不仅展示几个案例。</li><li>追问 grounding 的日志证据。</li><li>解释链直接用于可靠性审计。</li><li>多模态信号和题型 gating 同时可见。</li></ul></article>
<article class="panel"><h3>对齐最佳论文的地方</h3><ul class="mini-list"><li>像 LM-Interview：按完整任务流程组织。</li><li>像 MathBuddy：理论映射到系统决策。</li><li>像 AERA Chat：解释落实为可核验交互。</li><li>像 OpenOmni：把工程瓶颈当作结果。</li><li>像 iPET：把部署数字写进贡献。</li></ul></article>
<article class="panel"><h3>投稿前仍缺的证据</h3><ul class="mini-list"><li>专家与系统评分一致性。</li><li>针对 planner/follow-up/scoring 的消融。</li><li>端到端延迟与单场成本。</li><li>前后测或对照组学习增益。</li><li>不同人群与岗位的公平性分析。</li></ul></article>
</div>
<details><summary>十篇论文各自最核心的分析模板</summary><ul><li><b>LM-Interview：</b>人类与系统访谈对照、专家评分、访后分析相关性。</li><li><b>EmpathyEar：</b>自动指标与小规模人评验证多模态理解/生成。</li><li><b>OpenOmni：</b>不同配置下的延迟、准确率、成本与隐私约束。</li><li><b>AutoGen Studio：</b>下载量与 GitHub issues 归纳设计原则。</li><li><b>iPET：</b>离线评测、在线 A/B、长期使用统计和案例。</li><li><b>AgentMaster：</b>BERTScore、G-Eval、人评和路由错误。</li><li><b>MathBuddy：</b>八个教学维度、消融、实时识别准确率、30 人研究。</li><li><b>AERA Chat：</b>评分表现、rationale 人评、界面用户研究。</li><li><b>Metamo：</b>公共语料、prompt sensitivity、成本/延迟、安全、38 人研究。</li><li><b>LearnLens：</b>用户与 agent 评测、教师控制、延迟和成本。</li></ul></details>
</section>

<section id="claims"><p class="eyebrow">Paper-ready claim map</p><h2>哪些话可以写，哪些话需要降级</h2><div class="table-wrap"><table><thead><tr><th>拟写主张</th><th>当前证据</th><th>证据等级</th><th>推荐措辞</th></tr></thead><tbody>
<tr><th>问题生成具有岗位贴合性</th><td>{role_alignment['n']} 场 matched-vs-mismatched JD 对照；{role_alignment['rank_one_rate']*100:.1f}% Rank-1</td><td><span style="color:var(--green);font-weight:800">较强</span></td><td>lexically aligned / role-discriminative</td></tr>
<tr><th>面试流程覆盖全面</th><td>{complete_flows}/{len(sessions)} 场完整五阶段；{unique_positions} 个岗位标题</td><td><span style="color:var(--green);font-weight:800">较强</span></td><td>multi-stage, end-to-end workflow</td></tr>
<tr><th>追问会根据回答变化</th><td>{followups['followup_turns']} 个追问；grounding 胜率 {followups['grounding']['win_rate']*100:.1f}%</td><td><span style="color:var(--blue);font-weight:800">中等</span></td><td>logs provide evidence of answer-aware probing</td></tr>
<tr><th>评估全面且可追踪</th><td>13 features → 10 aspects → 2 tracks；题型 gating；三模态日志</td><td><span style="color:var(--green);font-weight:800">较强</span></td><td>comprehensive and traceable coverage</td></tr>
<tr><th>多模态不可被单一模态替代</th><td>跨模态相关 {evaluation['correlations']['text_audio']['r']:.2f} / {evaluation['correlations']['text_video']['r']:.2f} / {evaluation['correlations']['audio_video']['r']:.2f}</td><td><span style="color:var(--blue);font-weight:800">探索性</span></td><td>largely non-redundant in this deployment corpus</td></tr>
<tr><th>CV 个性化质量高</th><td>{cv_note}</td><td><span style="color:var(--orange);font-weight:800">不足</span></td><td>不要强宣称；补盲评</td></tr>
<tr><th>评分准确/有效</th><td>无专家金标准；视频 failure 明显；模态标度未校准</td><td><span style="color:var(--red);font-weight:800">未验证</span></td><td>advisory; validity remains future work</td></tr>
<tr><th>提升面试表现</th><td>只有自报接受度，无前后测或控制组</td><td><span style="color:var(--red);font-weight:800">未验证</span></td><td>participants reported usability/relevance</td></tr>
</tbody></table></div>
<h3>下一轮最划算的四项补充分析</h3><div class="grid-2"><article class="panel"><b>1. 专家盲评问题贴合度</b><p>对 matched JD/CV 与 shuffled JD/CV 生成的问题做成对盲评，指标包括 relevance、specificity、difficulty 和 redundancy。</p></article><article class="panel"><b>2. 专家-系统评分一致性</b><p>按 13 features 和 10 aspects 报 ICC / weighted kappa，并区分 text/audio/video。</p></article><article class="panel"><b>3. 追问与评分消融</b><p>固定题单 vs answer-aware follow-up；文本-only vs multimodal；KSA×STAR vs generic rubric。</p></article><article class="panel"><b>4. 工程指标</b><p>按 planner、interviewer、四 evaluator、聚合与报告统计 P50/P95 latency、失败率和单场成本。</p></article></div>
</section>

<section id="methods"><p class="eyebrow">Methods and limitations</p><h2>方法附录</h2>
<details open><summary>岗位/JD 贴合度如何计算</summary><p>将每场非 Candidate Questions 的问题拼接为 query，将 JD 作为 reference；使用英文 stop words、1–2 gram、sublinear TF-IDF 和 cosine similarity。Matched 值与所有“不同岗位”JD 的相似度中位数比较；Rank-1 表示 matched JD 高于所有不同岗位 JD。该方法可复算、无需调用外部模型，但会低估语义改写。</p></details>
<details><summary>CV 分析如何保护隐私</summary><p>只读取当前严格清洗会话 <code>uploads/</code> 下的 PDF，在本机通过 <code>pdftotext</code> 提取文本并计算聚合相似度。HTML 不写入 CV 文本、文件名、用户 ID 或回答内容。</p></details>
<details><summary>追问 grounding 如何计算</summary><p>从 transcript 的 <code>[Main Question]</code>、<code>[Answer]</code>、<code>[Follow-up N Question]</code> 标记解析 turn。将每个追问与真实前序回答比较，并以其他回答为错配基线。该指标证明 lexical grounding，不等于追问在逻辑上一定优质。</p></details>
<details><summary>评估与视频失败如何分类</summary><p>读取每场最大的 evaluation JSON。若 nonverbal justification 包含 “Evaluation failed”，或存在视频但 evaluated count 为 0，则标记 VLM failure；没有视频且四项视频特征均为 0，则标记 no-video；其余为 success。Failure-excluded 均值仍保留 no-video 0，因此是保守修正。</p></details>
<details><summary>主要限制</summary><ul><li>这是观察性部署语料，不是随机对照实验。</li><li>当前快照与论文锁定快照不完全重合。</li><li>TF-IDF 只能测词汇贴合，不能替代专家语义判断。</li><li>追问深度日志存在 6/9 turn 异常。</li><li>多模态 evaluator 的标度没有校准。</li><li>问卷只有汇总百分比，缺少完整 protocol 和原始计数。</li></ul></details>
<p class="foot">生成脚本：<code>analysis/build_comprehensive_report.py</code> · 输出：<code>analysis/polyinterview-comprehensive-analysis.html</code> · 所有分析在本地完成，未上传原始用户数据。</p>
</section>
</main>
</body></html>"""

    OUTPUT.write_text(page, encoding="utf-8")
    print(f"WROTE {OUTPUT}")
    print(
        f"current strict snapshot: users={len(users)} sessions={len(sessions)} "
        f"questions={total_questions} eval_questions={evaluation['records']}"
    )
    print(
        f"role/JD: matched={role_alignment['matched_median']:.4f} "
        f"baseline={role_alignment['baseline_median']:.4f} "
        f"rank1={role_alignment['rank_one_rate']:.3f}"
    )


if __name__ == "__main__":
    build_report()
