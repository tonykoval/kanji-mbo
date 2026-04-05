# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kanji-MBO is a Python tool for categorizing and grouping Japanese kanji characters based on shared components, on'yomi readings, keywords, and stems. It reads kanji data from Excel spreadsheets and applies a multi-rule categorization algorithm to organize kanji into meaningful groups.

## Running

```bash
# CLI — run from src/
cd src
python cli.py categorize                            # full categorization (all kanji)
python cli.py categorize -k 青 赤                   # categorize specific kanji
python cli.py categorize --subgroups                 # show subgroup breakdown
python cli.py lookup 青 赤                           # look up kanji data
python cli.py freq                                   # frequency-based grouping
python cli.py anki --output deck.apkg                # export to Anki deck
python cli.py -f ../excel/2250\ KANJI\ COMPONENTS\ -\ ver.\ 1.0.xlsx categorize  # custom file
python cli.py -l WARNING categorize                  # quiet logging
python cli.py --format json categorize               # JSON output
python cli.py --format csv lookup 青                 # CSV output

# Web UI
streamlit run src/web_app.py

# Direct scripts (legacy)
cd src && python main.py
cd src/freq && python main.py
```

Dependencies: `pip install -r requirements.txt` (pandas, openpyxl, disjoint_set, numpy, genanki, streamlit)

Python venv is at `venv/`.

## Testing

```bash
# All tests (from project root)
python -m pytest tests/ -v

# Individual test files
python -m pytest tests/test_algorithm.py -v
python -m pytest tests/test_model.py -v
python -m pytest tests/test_freq_algorithm.py -v
python -m pytest tests/test_cli.py -v
python -m pytest tests/test_integration.py -v        # requires Excel files in excel/

# Single test
python -m pytest tests/test_algorithm.py::TestFindKeyword::test_found -v
```

## Architecture

There are two pipelines (SRL-based and frequency-based) unified under a single CLI:

### `src/` — Full categorization pipeline
- **data_loader.py** — Excel I/O: reads spreadsheets and converts rows to `Kanji` domain objects.
- **model.py** — Data classes (`Kanji`, `Source`, `Categorization`, `Stem`) and constants (`Constants`, `ExcelColumn`). `Categorization` uses typed `defaultdict` for `result` and `queue`.
- **algorithm.py** — Rule-based categorization engine. Applies a priority chain of 7 rules to assign each kanji to a group:
  1. Keyword match → group from keyword.list
  2. Stem match → group from stem.list
  3. Special match → special group
  4. Component2 on'yomi cluster (crown tag)
  5. Stem variation lookup via components
  6. Visual similarity fallback (component clustering)
  7. "Other" catch-all group
  Uses a queue system for deferred kanji (those waiting for a higher-SRL kanji to appear) and `DisjointSet` to resolve queue relationships at the end.
- **core.py** — Shared utilities used by both pipelines (logging, on'yomi matching, component clustering).
- **cli.py** — CLI entry point with `categorize`, `lookup`, `freq`, and `anki` subcommands. Supports `--format text|json|csv`.
- **anki_export.py** — Exports categorization results to Anki `.apkg` deck files using genanki.
- **web_app.py** — Streamlit web UI for browsing kanji groups, searching, and looking up kanji.
- **main.py** — Legacy entry point.
- Input: `excel/1500 KANJI COMPONENTS - ver. 1.3.xlsx` (or 2250 variant)

### `src/freq/` — Frequency-based grouping pipeline
- **model.py** — Simplified `Kanji` dataclass (no SRL, tags, or group fields).
- **data_loader.py** — Excel I/O for the frequency pipeline.
- **algorithm.py** — Simpler categorization: groups kanji by shared component2 and on'yomi, using frequency rank instead of SRL for ordering.
- **main.py** — Legacy entry point. Now accessible via `python cli.py freq`.

### Key concepts
- **SRL** (Stroke Radical Level) — priority value used to determine which kanji "leads" a group
- **On'yomi matching** — kanji sharing Chinese readings are clustered together
- **Queue system** — kanji with lower SRL are deferred until their reference kanji (higher SRL) is categorized
- **DisjointSet** — used post-categorization to merge queue entries into final groups

## Data

Excel files in `excel/` are the primary data source. The MAIN sheet columns map to `ExcelColumn` constants in each `model.py`. The `src/` pipeline also uses keyword.list, stem.list, and special.list sheets.
