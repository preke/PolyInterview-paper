# Paper Plan

**Title (working)**: PolyInterview: An Explainable Multimodal Mock-Interview System with Theory-Grounded Feedback

**One-sentence contribution**: PolyInterview is a publicly deployed, multimodal AI mock-interview system that converts each spoken answer (text + audio + video) into explainable, theory-grounded (KSA × STAR) multi-dimensional feedback through a three-layer, parallel-agent evaluation architecture in which every score is traceable to the behavioral signal that produced it.

**Venue**: EMNLP 2026 — System Demonstrations track (ACL style)
**Type**: System demonstration (working-system paper; light evaluation, not benchmark-driven)
**Date**: 2026-05-28
**Page budget**: 6 pages body (references, ethics, appendix uncounted; >6 = desk reject)
**Section count**: 6 (+ Abstract)
**Live demo**: https://polyinterview.comp.polyu.edu.hk/
**Demo video**: ≤2.5 min MPEG4/YouTube (required; see paper_sources/Demo.mp4 as the basis)

---

## Claims–Evidence Matrix

| # | Claim | Evidence | Status | Section |
|---|-------|----------|--------|---------|
| C1 | A working, publicly deployed system lets students rehearse a *complete, end-to-end* multimodal interview (HR→behavioral→technical), not one-off Q&A. | Live URL; 3-stage journey (Setup/Live/Report); screenshots; deployment logs (85 users, 1,535 raw sessions). | Supported | §3 |
| C2 | A three-layer, theory-grounded evaluation architecture (13 features → 10 KSA aspects → 2 proficiency tracks) makes every multi-dimensional score **explainable and traceable** to a behavioral signal. | Architecture (interview_pipeline.drawio); KSA×STAR grounding; per-question Suggestion/Polished cards + whole-interview report. | Supported | §4 |
| C3 | Four **parallel** feature agents over text/audio/video make full-interview scoring cheap (≈ single-answer compute) and genuinely multimodal — including non-verbal signals existing tools drop. | Parallel-agent design; modality routing (LLM/VLM/Azure speech); per-question relevance gating (LLM selects active aspects). | Supported | §4 |
| C4 | Persona-driven adaptive questioning delivers personalization **beyond the first question** (the "Match" side), with configurable follow-up depth. | 3 personas (Amy/David/James) → 1/2/3 follow-ups; CV-grounded question generation. | Supported | §3 |
| C5 | Real deployment yields a usable corpus and an actionable finding: across three modalities, **visual-modality scores are systematically low** relative to audio/text. | Cleaned dataset (46 users / 120 sessions / 475 recordings); per-feature means from dashboard (/tmp/dash2.json): visual features (gesture 0.43, eye-contact 0.71) ≪ audio (prosody 5.11, fluency 4.80). | Supported | §5 |
| C6 | Pilot users find the system realistic and usable. | Two rounds, 129 participants / 6 institutions / 9 faculty reviewers; Round-1 praise: UI clarity 67%, immersion 58%, report depth 50%, personalization 42%; Round-2 qualitative realism signals. | Supported (self-report) | §5 |
| C7 | Privacy is designed-in (campus-only, encrypted-at-rest, per-user isolation, one-click delete, IRB/GDPR/PDPO). | Privacy architecture from narrative. | Supported | §5 / Ethics |

---

## Structure

### §0 Abstract (≈180 words)
- **What**: PolyInterview — a deployed multimodal mock-interview system with explainable multi-dimensional feedback.
- **Why hard**: existing AI interview tools give shallow, single-modality, one-off feedback with no theory grounding; students can't rehearse a realistic full interview.
- **How**: digital-human interviewer + persona-driven adaptive questioning (Match); a three-layer parallel-agent pipeline (13 multimodal features → 10 KSA aspects → 2 proficiency tracks) grounded in KSA × STAR, with every score traceable (Convince).
- **Evidence**: publicly live; deployed to 100+ users across 6 institutions; a cleaned 120-session corpus surfaces a systematic visual-modality scoring gap.
- **Remarkable**: full-interview scoring at ≈ single-answer compute via parallel agents; per-score traceability.

### §1 Introduction (≈1 page)
- **Hook**: shrinking HK graduate market, high interview anxiety (93%), brutal funnel (~242 applicants/role, ~2% reach interview); expert mock interviews cost ≥US$180 and don't scale.
- **Gap**: existing AI tools fail on 4 axes — (1) personalization (static banks, only first question), (2) feedback depth (surface metrics / model answers, no pedagogical grounding), (3) multimodal assessment (audio+text only; HireVue *removed* facial analysis in 2020), (4) scenario continuity (one-off Q&A, no multi-stage interview).
- **One-sentence contribution** (above).
- **Approach overview**: Offer = Match × Convince → personalized questioning + multimodal, theory-grounded, explainable scoring; deployed and live.
- **Contributions** (numbered, falsifiable):
  1. A deployed multimodal mock-interview *system* with an embodied (digital-human) interviewer and end-to-end multi-stage interviews.
  2. A three-layer, KSA×STAR-grounded, **explainable** evaluation architecture with four parallel feature agents (text/audio/video) and per-score traceability.
  3. Persona-driven adaptive follow-up questioning for personalization beyond the first question.
  4. A real deployment + cleaned 120-session corpus, with an empirical finding (systematic visual-modality scoring gap) and pilot user feedback.
- **Results preview**: live URL; deployment scale; visual-modality finding.
- **Hero figure**: Fig 1 (system journey + Match×Convince).
- **Key citations** (≈4): Schmidt & Hunter 1998 [VERIFY]; Ambady & Rosenthal thin-slice 1992 [VERIFY]; an AVI survey (Hickman et al.) [VERIFY]; HireVue facial-analysis removal 2020 [VERIFY].

### §2 Related Work (≈0.75 page)
- **Subtopics**:
  1. *Commercial AI interview tools* (Google Interview Warmup, Yoodli, Big Interview, HireVue, Interviewing.io) — position via the 4-axis gap; anchor Table 1.
  2. *Automated video interviews (AVIs) in I-O psychology* — feature-engineering pipelines that predict construct scores; contrast with explainable, evidence-based assessment (cite sister work on E-AVIs, Related_Explainable-AVI.docx [VERIFY]).
  3. *LLM/VLM-as-judge & explainable assessment* — reasoning-over-evidence vs. opaque score regression.
- **Positioning**: PolyInterview = a deployed system that unifies adaptive questioning + multimodal *explainable* scoring grounded in established hiring frameworks (KSA, STAR), with non-verbal signals re-introduced responsibly.
- Synthesize, don't list.

### §3 System Overview (≈1.5 pages) — *the demo core*
- **3.1 User journey (3 stages)**: Setup (4 params on one screen: persona, target job/JD or upload, duration→question count, CV parsing) → Live Interview → Report. "No prompt-writing required."
- **3.2 Embodied live interview**: digital-human avatar (real-time face + lip-sync); synchronous capture of voice / face / body; reintroduces social pressure.
- **3.3 Adaptive questioning (Match)**: 3 personas (Amy/David/James) → 1/2/3 follow-ups; CV- and answer-grounded probing; configurable difficulty. Worked example (checkout-flow answer → 3 different follow-ups).
- **3.4 Two-tier feedback**: per-question replay (score 0–10, transcript, Suggestion card, **Polished card** = rewrite of the student's own answer) + whole-interview report (Overall Evaluation, Competency radar over 10 aspects, 13-feature Skills&Behaviors panel).
- Figures: Fig 1 (hero journey), Fig 3 (Report UI screenshot).

### §4 Explainable Multimodal Scoring (≈1.25 pages) — *the technical contribution (Convince)*
- **4.1 Three-layer architecture**:
  - *Layer 1 — Features (13, 0–10)*: 4 parallel agents — Professional-Performance + Way-of-Expression (LLM, text), Non-Verbal-Behaviour (VLM, video: eye contact, posture, expression), Oral-Expression (Azure speech, audio).
  - *Layer 2 — Aspects (10, KSA-aligned)*: 3 cognitive + 3 background + 4 social (Big-Five-aware); aggregation agent with 70/30 primary–secondary weighting; **LLM gates which aspects are relevant per question**.
  - *Layer 3 — Proficiency (2 tracks)*: Professional Competency (cognitive+background) + Communication Competency (social+expression); overall = mean.
- **4.2 Theory grounding (KSA × STAR)**: KSA = *what* we assess (→ professional track, 6/10 aspects); STAR = *how* answers are scored (→ communication track); both recruiter-recognized → interpretable scores. Missing STAR parts → concrete feedback.
- **4.3 Why parallel + traceable**: full-interview scoring ≈ single-answer compute; every score traces feature→aspect→proficiency (no black box).
- Figure: Fig 2 (three-layer architecture / pipeline).

### §5 Deployment, Usage & Findings (≈1 page)
- **5.1 Deployment & corpus**: live on campus network; raw 85 users / 1,535 sessions / 14 GB (text+audio+video+CV). Test-account cleaning → 46 real users / 120 sessions / 475 recordings (rule-based exclusion; report briefly). Table 2.
- **5.2 Multimodal scoring in the wild**: per-feature means; **visual-modality features systematically lowest** (gesture 0.43, eye-contact 0.71, expression 0.76, posture 0.78) vs audio (prosody 5.11, fluency 4.80) and text — discuss as limitation/finding (scoring-standard strictness vs. genuine on-camera behavior). Fig 4.
- **5.3 Pilot user study**: 129 participants / 6 institutions / 9 faculty; Round-1 quantitative praise + Round-2 qualitative realism.
- **5.4 Privacy & responsible deployment** (brief; expand in Ethics): campus-only, pg_tde encryption, per-user isolation, one-click delete, IRB/GDPR/PDPO; roadmap to on-campus models (HKGAI/Qwen).

### §6 Conclusion (≈0.25 page)
- Restate: deployed, explainable, multimodal, theory-grounded, pilot-validated.
- Limitations: self-report evaluation (no expert-vs-system agreement yet); visual-modality calibration; English-centric; single-institution deployment.
- Future: human–system scoring agreement study (ZHI-20); on-campus model migration; multilingual.

### Ethics / Broader Impact (unlimited, uncounted)
- Data privacy stack; de-identification + IRB; risks of automated assessment & non-verbal scoring (explicitly address HireVue-style concerns → why we keep it explainable + advisory, student-facing not gatekeeping); fairness/limitations of visual features.

---

## Figure Plan

| ID | Type | Description | Data Source | Priority |
|----|------|-------------|-------------|----------|
| Fig 1 | Hero (composite) | System journey Setup→Live→Report annotated with Match×Convince; embedded UI thumbnails. | manual (screenshots/ + drawio) | HIGH |
| Fig 2 | Architecture | Three-layer pipeline: 4 parallel feature agents → 13 features → 10 KSA aspects → 2 proficiency tracks; modality icons (LLM/VLM/speech). | manual (interview_pipeline.drawio) | HIGH |
| Fig 3 | Screenshot | Whole-interview Report: competency radar + 13-feature panel + per-question Suggestion/Polished cards. | screenshots/Interview Assessment Report.png, Feedback.png | HIGH |
| Fig 4 | Bar chart (auto) | Mean score per feature, grouped/colored by modality (text/audio/video) — shows visual gap. | /tmp/dash2.json (clean.features) | HIGH |
| Table 1 | Comparison | PolyInterview vs Google Warmup/Yoodli/Big Interview/HireVue/Interviewing.io across 4 axes (personalization, feedback depth, multimodal, scenario continuity). | manual (narrative §3) | HIGH |
| Table 2 | Stats (auto) | Deployment/corpus stats: users, sessions, completion, recordings, mean duration; raw vs cleaned. | /tmp/dash2.json, /tmp/media.json | MEDIUM |

**Hero figure (Fig 1) detail**: left→right three panels (Setup / Live Interview / Report). Setup panel shows the 4 parameters; Live panel shows digital-human avatar + synchronous capture (voice/face/body icons); Report panel shows radar + feature bars. A top ribbon labels the left half "Match (personalized questioning)" and right half "Convince (multimodal explainable feedback)". Caption states the one-sentence contribution. Helps a skim reader grasp the whole system before §3.

---

## Citation Plan (ALL [VERIFY] — build & verify real BibTeX in /paper-write; do NOT fabricate)
- §1 Intro: Schmidt & Hunter 1998 (selection validity, r=.51) [VERIFY]; Ambady & Rosenthal 1992 (thin slices) [VERIFY]; HireVue facial-analysis removal 2020 (news/report) [VERIFY]; an AVI survey/foundational paper (Naim et al. 2018; Hickman et al. 2022) [VERIFY].
- §2 Related: Yoodli / Google Interview Warmup / Big Interview / HireVue / Interviewing.io (product cites / whitepapers) [VERIFY]; AVI feature-engineering pipelines (Hemamou et al. HireNet 2019) [VERIFY]; E-AVI sister work (Related_Explainable-AVI.docx) [VERIFY]; LLM-as-judge (Zheng et al. 2023 MT-Bench) [VERIFY]; Big Five (McCrae & Costa) [VERIFY].
- §3 System: STAR / DDI 1974 [VERIFY]; CV parsing / persona dialogue (light).
- §4 Method: KSA / US OPM competency model [VERIFY]; STAR [VERIFY]; VLM (e.g., Qwen-VL) [VERIFY]; Azure Speech [VERIFY]; LLM-as-judge [VERIFY].
- §5: GDPR / PDPO references [VERIFY]; pg_tde (tech doc).

---

## Page-budget feasibility
6 pages is tight for §3+§4 (system + architecture). If over: move Table 2 + detailed cleaning rules + extended privacy to Ethics/Appendix; keep §5 findings compact (Fig 4 + 3 sentences). §2 stays ≤0.75 page.

## Reviewer Feedback
- GPT-5.4 outline review (skill Step 6) **skipped**: Codex MCP / reviewer model not available in this environment. Self-review applied: claims all map to evidence; C6 flagged as self-report (soften language, list as limitation); visual-modality finding framed as honest finding + limitation, not a win.

## Next Steps
- [ ] /paper-figure — auto-generate Fig 4 + Table 2 from /tmp/dash2.json; export manual Fig 1/2/3 sources
- [ ] /paper-write — draft LaTeX (ACL style), build & verify references.bib (resolve [VERIFY])
- [ ] /paper-compile — build PDF, check ≤6 pages
