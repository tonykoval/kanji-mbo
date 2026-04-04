# CHANGELOG

## Research Papers Reviewed

This section tracks academic papers that have been reviewed for potential algorithm improvements, to avoid re-reading them in the future.

---

### Kandrac, P. (2025). "The Multicriteria-Based Ordering Effect on the Long-Term Retention Rate of Kanji"

- **Type:** Doctoral thesis, Palacky University Olomouc
- **URL:** https://theses.cz/id/h3vldp/The_Multicriteria-Based_Ordering_Effect_on_the_Long-Term_.pdf
- **Pages:** 246
- **Status:** READ IN FULL (key chapters)

#### Key Experimental Results
- **VR kanji (phonetic reliability) showed statistically significant improvement** (p=0.02 after regression adjustment) for MBO group vs FBO control group
- **Keywords showed NO significant difference** between groups — semantic ordering alone doesn't improve keyword retention in classroom settings
- VR kanji pairs: MBO group averaged 4.16 correct vs FBO group 3.18 — 12/19 MBO students got 4+ right vs 6/23 FBO students
- ~39.4% decline in passive kanji knowledge after ~6 weeks without review (36.6% within one SD)
- First-year students retained ~440 kanji readings+keywords after one month (29.14% of 1,500)
- Delayed test (3 months later): 7/11 students stable, 2 increasing, 2 decreasing (up to 40% loss)

#### Algorithm Details Confirmed (Table 6 & Table 7)
- Automation has 6 task types: kanji selection (semi-auto), group categorization (semi-auto), subgroup categorization (manual), character decomposition (manual), VR clustering (automatic), VISUAL kanji insertion (automatic)
- The algorithm runs in **two passes**: first pass categorizes chief kanji, second pass assigns companions using SRL
- Visual type ordering (Table 7, Rule 6 steps):
  - 6a: Check if kanji [col A] = any component in [cols B-D] of other kanji
  - 6b: Check if kanji component [col C] = any component in [col C] of other kanji
  - 6c: Check if kanji component [col B] = any kanji in [col A]
- Max 5 components per kanji; single-level two-component decomposition preferred
- SRL = "Semantic Relatedness Level" — determines which chief kanji a companion is assigned to

#### Open Problems Identified in Thesis
1. **Subgroup categorization cannot be automated** — requires semantic understanding; thesis suggests neural networks/language models could create semantic maps for kanji, but calls it "a rather time-demanding interdisciplinary project"
2. **Character decomposition lacks universal rules** — ambiguity in component/subcomponent/chunk/stroke boundaries; ~850 components missing from Unicode 17.0
3. **Consonant voicing in on'yomi matching** — voiced/unvoiced pairs (e.g., TAN/DAN) need special handling; currently only partially addressed
4. **Reading removal cascading effects** — removing rarely-used readings forces VR companions to relocate, sometimes degrading to less desirable VISUAL type
5. **Frequency data inconsistency** — excluded WKFR and KD databases; uses weighted averages from 5 sources; Google data CR=0.84 is borderline
6. **No automated learning cost calculation** — Librenjak proposed stroke_count + frequency + 2*readings, but thesis notes "several other factors" influence difficulty (phonetic reliability, symmetry, etc.)
7. **Single-keyword limitation** — some kanji need context that a single keyword cannot convey; corpus phrase data partially addresses this
8. **Scalability below 1,000 kanji** — MBO system shouldn't be applied to fewer than ~1,000 kanji; frequency-based ordering (FBO) more suitable for smaller sets

#### Algorithm Improvement Ideas from Thesis
- Combining FBO with phonetic reliability may be more efficient than full MBO for intensive courses
- The word-level reading analysis (vs character-level) should be the default — ~20% of readings can be removed
- Anki integration with custom SRS settings (starting ease=1.40, 3 learning steps, max interval=100d) proved effective
- Reading "invaders" (rarely-used readings kept for ordering purposes) need systematic tracking

---

### Kandrac, P. (2022). "How Reliable and Consistent Are Kanji Frequency Databases?"

- **Published in:** Electronic Journal of Contemporary Japanese Studies, Vol. 22, Issue 2
- **URL:** https://www.japanesestudies.org.uk/ejcjs/vol22/iss2/kandrac.html
- **Status:** REVIEWED (summary from thesis)

#### Key Findings
- Evaluated 6 freely available frequency databases + Google data (7 total)
- KUF (Kanji Usage Frequency by Shpika) is the most consistent database
- WKFR and KD deemed inconsistent and excluded from MBO frequency calculations
- ~25% of characters in the least consistent database show significant FN deviation
- Less frequent kanji have more deviated frequency numbers across databases
- Recommends weighted averages from multiple sources rather than single-source data

#### Relevance to Algorithm
- Current `freq` field in our data uses these weighted averages
- Could implement configurable frequency source weighting in the algorithm

---

### Kandrac, P. (2023). "How Many Joyo Kanji Readings Are Rarely Used?"

- **URL:** Referenced in thesis; dataset at "Joyo Kanji Readings Ver. 1.1"
- **Status:** REVIEWED (summary from thesis)

#### Key Findings
- ~20% of joyo kanji readings are rarely used (appear only in words with FV < threshold)
- 179 kanji (8.4% of all joyo) have only a single rarely-used reading
- Word-level analysis is superior to character-level for determining reading usefulness
- 4 conditions for keeping rarely-used readings: combined FV exceeds threshold, reading is needed for ordering, reading is uniquely memorable, kanji has no other reading

#### Relevance to Algorithm
- On'yomi matching in Rules 3-4 currently treats all readings equally
- **Potential improvement:** weight on'yomi matches by reading usefulness category (often/sometimes/rarely used)
- Could filter out rarely-used readings before VR clustering to reduce noise

---

### Kandrac, P. (2020). "Maximizing the Efficiency in the Kanji Learning Task by Multicriteria-Based Ordering"

- **Type:** Master's thesis
- **URL:** https://www.researchgate.net/publication/339054674
- **Status:** REVIEWED (summary only)

#### Key Findings
- Foundational paper defining MBO criteria: visual, phonetic, semantic, frequency
- Proposes 75 semantic groups for categorization
- Goal was to minimize VISUAL-type kanji (phonetically unreliable)
- MBO version progression: 4.2d -> 5.9 (2,000 kanji) -> 6.1 (1,336) -> 6.2 (1,500) -> 6.3 (1,136) -> 6.5 (2,250)

---

### Loach, J.C. & Wang, J. (2016). "Optimizing the Learning Order of Chinese Characters Using a Novel Topological Sort Algorithm"

- **Published in:** PLOS ONE 11(10): e0163623
- **DOI:** 10.1371/journal.pone.0163623
- **Status:** REVIEWED (abstract + key algorithm)

#### Key Algorithm Idea
- **Centrality measure: eta = frequency / learning_cost**
  - Learning cost for primitives: 1 + 0.1 * stroke_count
  - Learning cost for compounds: number of component combinations
- Topological sort ensures components always appear before characters containing them
- "Move left as far as possible" heuristic for within-group ordering

#### Relevance to Algorithm
- **Could implement centrality measure for within-group ordering** — currently groups are ordered by SRL, but eta could provide a secondary sort criterion
- Topological constraint is partially enforced by our STEM-first rule (Rule 2) but not systematically for all components
- Learning cost model maps to our component decomposition data

---

### Yan, X. et al. (2013). "Efficient Learning Strategy of Chinese Characters Based on Network Approach"

- **Published in:** PLOS ONE 8(8): e69745
- **DOI:** 10.1371/journal.pone.0069745
- **Status:** REVIEWED (abstract + key findings)

#### Key Findings
- Constructs a node-weighted network of characters where edges = composition relationships
- **Distributed Node Weight (DNW) strategy** balances frequency with network hierarchy
- Algorithmically-optimized order is substantially more efficient than pure frequency ordering

#### Relevance to Algorithm
- The network/graph approach could complement our DisjointSet-based grouping
- DNW concept could inform how we weight component sharing vs frequency in categorization

---

### Schuhmacher, D. (2023). "Distance Maps between Japanese Kanji Characters Based on Hierarchical Optimal Transport"

- **URL:** https://arxiv.org/abs/2304.02493
- **Software:** kanjistat R package (CRAN, updated Sep 2025)
- **Status:** REVIEWED (abstract)

#### Key Algorithm Idea
- Hierarchical optimal transport for computing kanji distance/similarity
- Modular cost: (1) ink transport between components, (2) registration transformation distance, (3) label difference
- Produces nearest-neighbor tables for joyo kanji

#### Relevance to Algorithm
- **Could replace or augment Rule 6 (visual similarity)** with principled distance metrics instead of simple component matching
- Pre-computed nearest-neighbor data could feed directly into VISUAL type assignment
- The kanjistat R package could be called as an external tool

---

### Yencken, L. & Baldwin, T. (2008). "Measuring and Predicting Orthographic Associations: Modelling the Similarity of Japanese Kanji"

- **Published in:** Proceedings of COLING 2008
- **URL:** https://aclanthology.org/C08-1131/
- **Data:** https://lars.yencken.org/datasets/kanji-confusion/ (CC BY 3.0)
- **Status:** REVIEWED (abstract)

#### Key Algorithm Idea
- **Stroke edit distance**: encode kanji as stroke-type sequences, compute Levenshtein distance
- Human-validated kanji confusion dataset with top-10 nearest neighbors for 1,945 joyo kanji

#### Relevance to Algorithm
- Simpler alternative to Schuhmacher for visual similarity
- Pre-calculated confusion sets could directly improve Rule 6 accuracy
- Ground truth data available for evaluating our current visual similarity grouping

---

### Hamilton, N. (2019). "The Kanji Code: See the Sounds with Phonetic Components and Visual Patterns"

- **URL:** https://www.researchgate.net/publication/331985327
- **Status:** REVIEWED (abstract)

#### Key Findings
- Catalogs 150 phonetic components that predict on'yomi of 450+ kanji
- Two categories: same reading as parent component, and "rhyming" readings
- Applies visual pattern grouping alongside phonetic grouping

#### Relevance to Algorithm
- The 150 phonetic component patterns could improve Rules 3-4 (on'yomi clustering)
- "Rhyming" category (e.g., voiced/unvoiced pairs) directly addresses the consonant voicing problem noted in the thesis
- Could be integrated as a phonetic component lookup table alongside our current on'yomi string matching

---

### Perfetti, C.A. & Liu, Y. "The Effect of Radical-Based Grouping in Character Learning in Chinese as a Foreign Language"

- **URL:** https://www.lrdc.pitt.edu/perfettilab/pubpdfs/ChineseRadicalBasedGrouping.pdf
- **Status:** REVIEWED (abstract)

#### Key Findings
- Radical-sharing character groups lead to **better recall and better radical generalization** for beginners
- Effect diminishes for intermediate learners
- Empirically validates component-based grouping approach

#### Relevance to Algorithm
- Confirms our stem/component grouping approach is sound for target audience (beginners/intermediate)

---

### Librenjak, S. (2021). "Considering the Learning Order of Kanji"

- **Published in:** Silva Iaponicarum, Vol. 66, pp. 7-31
- **URL:** https://ray.yorksj.ac.uk/id/eprint/9742/
- **Status:** REVIEWED (summary)

#### Key Findings
- Proposed learning cost formula: stroke_count + frequency + 2 * non_repetitive_readings
- Analyzed Minna-no-Nihongo and Genki textbook orderings
- Notes kanji learning order is understudied

#### Relevance to Algorithm
- Learning cost formula could be implemented for within-group ordering
- Thesis notes this formula is insufficient (missing phonetic reliability, symmetry factors)

---

### scriptin/topokanji (GitHub)

- **URL:** https://github.com/scriptin/topokanji
- **Status:** REVIEWED (README)

#### Key Details
- Implements topological sort using modified Kahn algorithm with frequency-based intermediate sort
- Uses KanjiVG + CJK Decomposition Data + multiple frequency tables
- Generates frequency-ordered lists covering 2,000-2,500 characters

#### Relevance to Algorithm
- Reference implementation for topological sort approach
- Could serve as comparison baseline
- CJK Decomposition Data could supplement our manual decomposition

---

### Joyce et al. "Joyo Kanji as Core Building Blocks of the Japanese Writing System"

- **Published in:** Written Language & Literacy, 17(2)
- **URL:** https://www.researchgate.net/publication/265969060
- **Data:** www.kanjidatabase.com
- **Status:** REVIEWED (abstract)

#### Key Findings
- Large-scale joyo kanji database with on-reading frequency, on-reading ratio, entropy, productivity
- 11 years of Mainichi Newspaper corpus (299M+ tokens)

#### Relevance to Algorithm
- Entropy and productivity metrics could serve as additional ordering criteria
- On-reading ratio data could improve on'yomi weighting in VR clustering

---

### Winiwarter, W. (2025). "CACIKI — Compositionally Analyzed Collection of Illustrated Kanji Information"

- **Published in:** Springer (chapter, Dec 2025)
- **URL:** https://link.springer.com/chapter/10.1007/978-3-032-11976-6_14
- **Status:** REVIEWED (abstract only)

#### Key Findings
- 3,500 kanji with visual, compositional, and semantic annotations
- Web-based learning environment with exercises

#### Relevance to Algorithm
- Compositional analysis data for 3,500 kanji could supplement our decomposition
- Low priority — our decomposition is manually curated for MBO-specific purposes

---

## Potential Algorithm Improvements (Prioritized)

Based on the research review, the following improvements are ranked by impact and feasibility:

### High Priority
1. **Reading usefulness weighting** — Filter or weight on'yomi by usage frequency category (often/sometimes/rarely) before VR clustering (Rules 3-4). Data available from Kandrac's "Joyo Kanji Readings" dataset.
2. **Voiced/unvoiced consonant handling** — Treat voiced/unvoiced on'yomi pairs (TAN/DAN, SEI/ZEI, etc.) as matches in VR clustering. Currently partially handled. Hamilton's phonetic component catalog provides a systematic list.
3. **Within-group ordering by centrality** — Implement Loach & Wang's eta = frequency / learning_cost as a secondary sort criterion within categorization groups.

### Medium Priority
4. **Visual similarity upgrade (Rule 6)** — Integrate Yencken's stroke edit distance or pre-computed confusion sets for more principled VISUAL type assignment. Current component matching is coarse.
5. **Topological component ordering** — Ensure components always appear before the characters containing them (within groups). Partially enforced by STEM-first but not systematic.
6. **Learning cost calculation** — Implement a learning cost metric (stroke count + frequency + reading count + phonetic reliability) for automated kanji selection and ordering.

### Low Priority / Future Research
7. **Semantic subgroup automation** — Use language models to create semantic maps for kanji within stem groups. Thesis explicitly calls this "a rather time-demanding interdisciplinary project requiring active cooperation of multiple researchers."
8. **External data integration** — Incorporate kanjidatabase.com entropy/productivity data, kanjistat distance metrics, or CJK Decomposition Data to augment manual decomposition.
9. **Scalable FBO+phonetic system** — For kanji sets < 1,000, implement frequency-based ordering with phonetic reliability clustering (thesis confirms this is more effective than full MBO for small sets).

---

## Research Gaps (No Papers Found)

These areas have no published research and represent novel contributions of this project:

- **DisjointSet / Union-Find applied to kanji grouping** — our use of Union-Find for transitive group resolution appears novel
- **Neural network-based kanji decomposition for learning order** — CNNs used for recognition but not for optimizing learning order through decomposition
- **Community detection algorithms on kanji similarity graphs** — unexplored combination
