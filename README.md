# Kanji MBO — Multicriteria-Based Ordering Algorithm

A rule-based engine for categorizing and grouping Japanese kanji by shared components, on'yomi readings, keywords, and stems. Created as part of doctoral research investigating the long-term effect of multicriteria-based ordering on kanji retention rates.

## Background

This project reproduces the ordering algorithm used to manually order 2,000 and 1,500 kanji. The semantic-based ordering system was subsequently utilized to order as many as 2,250 kanji, followed by a version ordering 1,200 kanji based on usage frequency and phonetic reliability (kanji with the same component and the same Sino-Japanese reading, or *on'yomi*, grouped together, regardless of usage frequency).

Considering how time-consuming it was to reorder 1,500 kanji based on the principles used to manually order 2,000 kanji (in the MBO version 5.9 presented in the master's thesis), an automated version of the ordering system was created. This allows others to apply multicriterial ordering to a different number of kanji without repeating the manual process.

### Key Limitations

1. **Scalability** — The semantic-based ordering system (1,500 and 2,250 kanji) should not be applied to fewer than 1,000 kanji. The more kanji included, the more effective the multicriterial system becomes. It may even be beneficial for **Kanji Kentei Level 1** (6,000+ kanji).

2. **System Adaptation** — Applying the system to significantly different kanji counts may require modifications (group structure, character decomposition). For example, applying the 1,500–2,250 system to 1,800 kanji can lead to a higher number of "OTHER"-type kanji.

3. **Automation** — Complete automation was hindered by character decomposition and ordering within semantic groups/subgroups. The algorithm's main function is **categorization** rather than precise ordering, though certain kanji types are indeed ordered.

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### CLI Usage

Run from the `src/` directory:

```bash
cd src

# Full categorization (all kanji)
python cli.py categorize

# Categorize specific kanji
python cli.py categorize -k 青 赤 白

# Show subgroup breakdown
python cli.py categorize --subgroups

# Look up kanji data (readings, components, SRL, frequency)
python cli.py lookup 青 赤

# Use a different Excel file
python cli.py -f "../excel/2250 KANJI COMPONENTS - ver. 1.0.xlsx" categorize

# Quiet logging
python cli.py -l WARNING categorize
```

### Direct Scripts (legacy)

```bash
# Main categorization pipeline
cd src && python main.py

# Frequency-based grouping
cd src/freq && python main.py
```

### Configuration

In `src/main.py`, you can switch datasets or categorize individual kanji:

```python
# Select source Excel file
source = algorithm.read_excel("../excel/1500 KANJI COMPONENTS - ver. 1.3.xlsx")

# Categorize a specific kanji character
algorithm.categorize_kanji(algorithm.read_kanji_char("麻", source), categorization, source)
```

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Individual test modules
python -m pytest tests/test_algorithm.py -v
python -m pytest tests/test_model.py -v
python -m pytest tests/test_freq_algorithm.py -v
python -m pytest tests/test_cli.py -v
```

## Project Structure

```
src/
  cli.py            # CLI entry point (categorize, lookup commands)
  main.py           # Legacy entry point
  model.py          # Data classes (Kanji, Source, Categorization, Stem)
  algorithm.py      # 7-rule categorization engine
  freq/
    main.py         # Frequency pipeline entry point
    model.py        # Simplified data classes
    algorithm.py    # Component + on'yomi grouping
excel/              # Excel data files (input)
tests/              # Unit tests
docs/               # Static documentation site
```

## Two Pipelines

### Categorization (`src/`)

Applies a 7-rule priority chain to assign each kanji to a named group:

1. **Keyword** — semantic match via keyword.list
2. **Stem** — radical/component match via stem.list
3. **Special** — bypass rules via special.list
4. **Crown component** — reverse component2 lookup + on'yomi
5. **On'yomi cluster** — shared component2 + reading match
6. **Stem variation** — component lookup in stem.list STEM 1–6
7. **Visual similarity** — structural component clustering
8. **Other** — fallback to "79 other"

Uses a queue system for deferred kanji (waiting for higher-SRL references) and DisjointSet to resolve transitive relationships.

### Frequency (`src/freq/`)

Simpler grouping: matches kanji by shared component2 and on'yomi, orders by frequency rank, and merges groups with DisjointSet. Output written to `src/freq/output.txt`.

## Documentation

Open `docs/index.html` in a browser for the full documentation site, including user guide, algorithm reference, API docs, and glossary.

## Notes on Data

### Frequency Data

Kanji frequency numbers were calculated using seven different frequency databases, including Shibano's Google Data and Matsushita's Character Database. For details, see:
- *"How Reliable and Consistent Are Kanji Frequency Databases?"*
- *"2242 Kanji Frequency List ver. 1.1"* — available on [ResearchGate](https://www.researchgate.net/publication/357159664_2242_Kanji_Frequency_List_ver_11/)

### Readings

While nearly all official readings are included in the 2,250-kanji list, some readings were excluded from the 1,500-kanji and 1,200-kanji lists. This editorial decision is discussed in: *"How Many Joyo Kanji Readings Are Rarely Used?"*

## License

See [LICENSE](LICENSE) for details.
