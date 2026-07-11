# Profiled LLM-Agent Panel Pilot

This directory contains a reproducible dry run of the planned expert-evaluation
protocol. It is not a human-expert study and must not be reported as one.

## Scope

- 10 independently profiled LLM evaluators.
- 12 frozen text artifacts: four question plans, four answer-follow-up pairs,
  and four feedback reports.
- 120 artifact-level reviews and 360 criterion ratings on a 1--5 scale.
- Question artifacts include system-generated text and job-description excerpts.
- Follow-up and feedback artifacts use known template/test sessions only.
- No CV files, raw audio, raw video, account IDs, or session IDs are exposed.

The pilot evaluates the wording and visible evidence in the frozen packet. It
does not establish human agreement, multimodal validity, learning gains, or
hiring-related validity.

## Files

- `profiles.json`: the ten evaluator profiles.
- `build_packet.py`: deterministic artifact selection and de-identification.
- `evaluation_packet.json`: frozen packet and rubrics.
- `ratings/A01.json`--`ratings/A10.json`: independent structured ratings.
- `aggregate_panel.py`: validation and aggregation.
- `summary.json`: aggregate and criterion-level results.
- `paper/figures/table_llm_agent_panel.tex`: generated paper table.

## Reproduce

```bash
python3 analysis/llm_agent_panel/build_packet.py
python3 analysis/llm_agent_panel/aggregate_panel.py
```

Rebuilding the packet does not rerun the LLM evaluators. The rating files are
the frozen outputs of the ten independent panel agents used in this pilot.

## Replacement With Human Experts

The planned human study should retain the same three modules and rubric keys,
but recruit ten verifiable experts, randomize artifact order, add CV grounding
where consent permits, and provide synchronized audio/video evidence for the
assessment module. The paper should then replace all pilot scores, report
expert backgrounds and recruitment, and compute an appropriate inter-rater
reliability statistic from the human ratings.
