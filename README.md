# PolyInterview Demo Paper

This repository contains the manuscript, figures, aggregate analysis scripts and
results, reference demo papers, and supporting materials for the PolyInterview
EMNLP demo paper.

## Build

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Data policy

Raw interview records and user-level analysis outputs are intentionally excluded
from this repository. Only aggregate statistics used for manuscript development
are retained.
