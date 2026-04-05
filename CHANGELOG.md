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

### Yang, X. et al. (2023). "Quantifying Character Similarity with Vision Transformers"

- **Published in:** EMNLP 2023 (Proceedings of the 2023 Conference on Empirical Methods in NLP)
- **URL:** https://aclanthology.org/2023.emnlp-main.863/
- **Code:** https://github.com/dell-research-harvard/HomoglyphsCJKTraining
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Self-supervised Vision Transformer (ViT) trained with contrastive learning on augmented digital fonts
- Produces a metric embedding space where visually similar CJK characters cluster nearby
- Pre-trained per-language (separate Japanese model available)
- Nearest-neighbor lookup in embedding space gives principled visual similarity rankings

#### Relevance to Algorithm
- **Direct drop-in replacement for Rule 6 (visual similarity fallback)** — instead of the current 3-step component heuristic (6a: char∈components of other, 6b: component2 match, 6c: component1=char), use ViT embedding distance to rank visual neighbors
- Pre-trained models and code are open-source — could compute pairwise similarity for all 2,250 kanji offline, then use as a lookup table in the algorithm
- Would reduce VISUAL-type misassignments where component matching fails to capture actual perceptual similarity

---

### Shi, F. et al. (2025). "CoLa: Chinese Character Decomposition with Compositional Latent Components"

- **Published in:** arXiv (2506.03798)
- **URL:** https://arxiv.org/abs/2506.03798
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Deep latent variable model that learns character decomposition *without* human-defined radical schemes
- Encodes character images into component-specific latent representations
- Achieves zero-shot character recognition by comparing compositions in latent space
- Components discovered automatically — not constrained to traditional radical taxonomy

#### Relevance to Algorithm
- Could validate our hand-curated component lists in Excel — run CoLa on all kanji and compare discovered components to our component1-5 columns
- Might reveal groupings the rule-based system misses (components that are perceptually similar but have different Unicode codepoints)
- Long-term: data-driven decomposition could replace manual component annotation for new kanji sets

---

### Hong, Y. et al. (2024). "Improving Chinese Character Representation with Formation Tree (FT-CLIP)"

- **Published in:** arXiv (2404.12693) / Neurocomputing 2025
- **URL:** https://arxiv.org/abs/2404.12693
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- "Formation Trees" — hierarchical tree representations where leaf nodes are radicals, edges encode spatial relationships (azimuth directions)
- Dedicated tree encoder aggregates radical features bottom-up into holistic character embeddings
- Explicitly extends to Japanese kanji and Korean Hangul

#### Relevance to Algorithm
- The tree structure directly parallels our component decomposition (component1-5 are flat; a tree would encode nesting and spatial layout)
- **Could improve on'yomi clustering (Rules 3-4)** by considering not just *which* components are shared, but *where* they appear in the character structure
- Example: 清 and 請 both have 青 as component2, but their spatial layouts differ — currently treated identically, a formation tree would distinguish them

---

### Zhu, Y. et al. (2024). "HierCode: A Lightweight Hierarchical Codebook for Zero-shot Chinese Text Recognition"

- **Published in:** arXiv (2403.13761) / Pattern Recognition
- **URL:** https://arxiv.org/abs/2403.13761
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Multi-hot encoding with hierarchical binary tree to create compact character representations based on radical structure
- Characters sharing radicals get similar binary codes — reduces embedding size 10-40% vs character-level models
- Handles out-of-vocabulary characters via shared radical codes

#### Relevance to Algorithm
- Hierarchical radical codes could serve as a fast similarity hash for DisjointSet merging
- Two kanji with high code overlap (many shared radicals in the hierarchy) are strong candidates for the same group
- Lighter-weight alternative to ViT embeddings for Rule 6 — could be computed purely from our existing component data

---

### Han, Z. et al. (2025). "Adaptive Radical Similarity Learning (ARSM)"

- **Published in:** ICDAR 2025
- **URL:** https://link.springer.com/chapter/10.1007/978-3-032-04630-7_27
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Dynamically measures similarity between radical pairs, addressing ambiguities from visually similar radicals across writing styles
- Learns adaptive similarity thresholds rather than binary same/different matching

#### Relevance to Algorithm
- Directly relevant to component matching throughout Rules 3-6
- Our algorithm currently uses exact string matching for components (e.g., `kanji.component2 == k.component2`)
- ARSM's adaptive similarity could handle cases where components are visually similar but assigned different names in the decomposition data (e.g., 氵vs 水, 亻vs 人)
- **Open problem addressed:** the thesis noted ~850 components missing from Unicode 17.0 — fuzzy matching would reduce dependence on exact component naming

---

### UCR Framework (2025). "A Unified Character-Radical Dual-Supervision Framework"

- **Published in:** Pattern Recognition 2025
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0031320325000330
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Three modules: Character Recognition (CRM), Radical Recognition (RRM), Confidence-based Predictor (CPM)
- Dual supervision learns character-to-radical decomposition mappings automatically
- Handles both seen and unseen characters (zero-shot via radical composition)

#### Relevance to Algorithm
- Learned radical decomposition could validate our Excel component data at scale
- Could auto-generate decompositions for kanji not yet in our dataset (useful for expanding from 2,250 to all 3,000+ CJK characters)

---

### JRED (2025). "Joint Radical Embedding and Detection for Zero-Shot Chinese Character Recognition"

- **Published in:** Pattern Recognition, Vol. 161
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0031320324010379
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Learns radical embeddings without positional information, uses them as sliding detectors on visual feature maps
- Bridges seen/unseen character classes via shared radical representations

#### Relevance to Algorithm
- Dense radical embeddings could serve as a continuous similarity metric for components
- Two kanji sharing similar radical embeddings (even if radicals are not identical by name) might belong in the same group
- Could improve stem variation lookup (Rule 5) by finding stem components that are semantically related even when not string-identical

---

### AttGraph (2025). "Disentangling Confusable Ancient Chinese Characters via Component-Correlation Synergy"

- **Published in:** npj Heritage Science
- **URL:** https://www.nature.com/articles/s40494-025-02278-6
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Graph Convolutional Networks (GCN) for modeling patch-wise spatial-semantic dependencies
- Local Content Transformation (LCT) + Local Correlation Reasoning (LCR) to distinguish visually similar characters

#### Relevance to Algorithm
- GCN approach to component correlation is conceptually similar to our DisjointSet graph-based grouping
- The component-correlation modeling could improve distinguishing groups that should be separate but whose members share many components

---

### LECTOR (2025). "LLM-Enhanced Concept-based Test-Oriented Repetition for Adaptive Spaced Learning"

- **Published in:** arXiv (2508.03275)
- **URL:** https://arxiv.org/abs/2508.03275
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- Integrates LLM-based semantic analysis with adaptive interval optimization
- Key innovation: models confusion between semantically/visually similar items — traditional SRS (SM2, FSRS) treats items in isolation
- Achieves 90.2% vs 88.4% for SSP-MMC baseline

#### Relevance to Algorithm
- **Directly relevant to Anki export** — our kanji groups inherently cluster similar kanji, which causes interference during review
- LECTOR's confusion-aware scheduling could inform inter-group spacing: kanji from the same MBO group should not be reviewed back-to-back
- Could add metadata to Anki export indicating which kanji are "confusable" within a group, enabling smarter scheduling

---

### Wang, X. et al. (2025). "Semantic Radicals' Semantic Attachment to Their Composed Phonograms"

- **Published in:** BMC Psychology / PMC
- **URL:** https://pmc.ncbi.nlm.nih.gov/articles/PMC12105197/
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Semantic radicals in transparent and opaque phonograms are semantically activated during recognition
- Activation is "genuine-character status dependent" — only works in real characters, not pseudo-characters
- Low-frequency characters show stronger facilitatory effects from shared radicals

#### Relevance to Algorithm
- **Cognitive validation**: confirms that grouping kanji by shared components leverages real neural pathways — learners subconsciously activate component-level meaning
- Especially strong for low-frequency kanji — supports our strategy of using component grouping to aid retention of rare kanji
- Does NOT change the algorithm but strengthens the theoretical justification for the MBO approach

---

### Han Zi Builder (2025). "A Hybrid Recommendation System for Chinese Character Components"

- **Published in:** Discover Artificial Intelligence (Springer)
- **URL:** https://link.springer.com/article/10.1007/s44163-025-00460-0
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Dual-tower neural network (768d BERT embeddings) + deterministic rule validation for character component assembly
- Curated 141-radical / 803-character database with 12,345 valid combinations
- Controlled experiments (N=127): 36.3% improvement in character decomposition accuracy

#### Relevance to Algorithm
- Architecture validates our hybrid approach (rule-based algorithm + structured data)
- Their valid combination constraints are analogous to our keyword.list / stem.list / special.list validation sheets
- The dual-tower network idea could augment our rule-based system: neural embedding for component matching + deterministic rules for group assignment

---

### Edman, L. et al. (2025). "EXECUTE: A Multilingual Benchmark for LLM Token Understanding"

- **Published in:** ACL 2025 Findings
- **URL:** https://aclanthology.org/2025.findings-acl.95/
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Benchmarks LLMs on character-level and sub-character-level tasks including Kangxi radical decomposition
- Tests Aya Expanse, Gemma 2, Llama 3.1/3.3, Qwen 2.5, Mistral on CJK decomposition
- Different languages show different processing challenges — Japanese kanji have specific failure modes

#### Relevance to Algorithm
- **Establishes which LLMs can reliably decompose kanji** — relevant if we want to use LLMs for semi-automated quality checks on component data
- Could inform future work on semantic subgroup automation (Open Problem 1 from thesis)
- Qwen 2.5 and Llama 3.3 show best results for CJK radical tasks

---

### Hu, P. et al. (2024). "Count, Decompose and Correct: A New Approach to Chinese Character Error Correction"

- **Published in:** Pattern Recognition, Vol. 160
- **URL:** https://www.sciencedirect.com/science/article/abs/pii/S0031320324008616
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Algorithm Idea
- 3-step pipeline: Counter (predicts radical count), Decomposer (IDS-based decomposition), Corrector
- Characters differing by only one radical are treated as near-neighbors

#### Relevance to Algorithm
- IDS (Ideographic Description Sequence) decomposition could provide a principled distance metric: edit distance on IDS = structural similarity
- Characters differing by one radical = candidates for same group or subgroup
- Could systematize the manual subgroup categorization step

---

### Deng et al. (2025). "Multi-Task Learning for Chinese Character and Radical Recognition with Dynamic Channel-Spatial Attention"

- **Published in:** IET Image Processing
- **URL:** https://ietresearch.onlinelibrary.wiley.com/doi/abs/10.1049/ipr2.70213
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Details
- EfficientNetV2 + Transformer with dynamic collaborative channel-spatial attention (DCCSA)
- Joint character + radical recognition with spatial relationship modeling between radicals

#### Relevance to Algorithm
- Spatial relationship modeling between radicals could inform a richer component representation than our flat component1-5 columns
- Lower priority — primarily a recognition system, not a grouping system

---

### Wang, T. (2024). "Designing a Digital Game for Chinese Character Learning: A Theory-Driven Practice Approach"

- **Published in:** Education Sciences, 14(12), 1366
- **URL:** https://www.mdpi.com/2227-7102/14/12/1366
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Gamified structural/component awareness significantly improves character recognition and engagement
- Grounded in task engagement principles for alphabetic-background learners

#### Relevance to Algorithm
- Validates our web UI / Anki export approach for making grouped kanji interactive
- Low direct relevance to the algorithm itself

---

### Yu, J. et al. (2025). "Harnessing Generative AI to Construct Multimodal Resources for Chinese Character Learning"

- **Published in:** Systems, 13(8), 692 (MDPI)
- **URL:** https://www.mdpi.com/2079-8954/13/8/692
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Framework for semi-automated generation of multimodal learning resources using generative AI
- Specifically addresses distinguishing similar characters — a key MBO concern

#### Relevance to Algorithm
- GenAI-generated mnemonics and illustrations could enrich our Anki export
- "Distinguishing similar characters" aligns with our visual similarity grouping
- Feature idea: auto-generate comparison resources for kanji within the same MBO group

---

### Radical-Based Token Representation for Chinese PLMs (2025)

- **Published in:** MDPI Electronics, 14(5), 1031
- **URL:** https://www.mdpi.com/2079-9292/14/5/1031
- **Status:** REVIEWED (2025-04 review cycle)

#### Key Findings
- Extends PLM vocabularies to include both radicals and character tokens
- More granular sub-character understanding in language models

#### Relevance to Algorithm
- The dual radical/character vocabulary mirrors our use of both whole-kanji properties (on'yomi, keywords) and component-level properties
- Could inspire a hybrid embedding approach for future ML-augmented grouping

---

## Potential Algorithm Improvements (Prioritized)

Based on the full research review (original + 2025-04 update), the following improvements are ranked by impact and feasibility:

### High Priority
1. **Reading usefulness weighting** — Filter or weight on'yomi by usage frequency category (often/sometimes/rarely) before VR clustering (Rules 3-4). Data available from Kandrac's "Joyo Kanji Readings" dataset.
2. **Voiced/unvoiced consonant handling** — Treat voiced/unvoiced on'yomi pairs (TAN/DAN, SEI/ZEI, etc.) as matches in VR clustering. Currently partially handled. Hamilton's phonetic component catalog provides a systematic list.
3. **ViT-based visual similarity for Rule 6** *(NEW from 2025-04 review)* — Replace the 3-step component heuristic (6a/6b/6c) with Vision Transformer embedding distances from Yang et al. (EMNLP 2023). Pre-trained Japanese model and code available at dell-research-harvard/HomoglyphsCJKTraining. Could pre-compute all pairwise distances offline and use as a lookup table. This is now a more principled and practical approach than Yencken's stroke edit distance (previously listed as medium priority).
4. **Within-group ordering by centrality** — Implement Loach & Wang's eta = frequency / learning_cost as a secondary sort criterion within categorization groups.

### Medium Priority
5. **Fuzzy component matching via radical embeddings** *(NEW from 2025-04 review)* — Replace exact string matching for components (`component2 == k.component2`) with similarity matching using JRED or ARSM radical embeddings. Would handle cases where components are visually similar but assigned different names (氵/水, 亻/人). Addresses thesis open problem of ~850 components missing from Unicode.
6. **IDS-based structural distance** *(NEW from 2025-04 review)* — Use Ideographic Description Sequences (from Hu et al. 2024) to compute structural edit distance between kanji. Characters differing by one radical = natural subgroup candidates. Could partially automate subgroup categorization.
7. **Decomposition validation with CoLa** *(NEW from 2025-04 review)* — Run CoLa (Shi et al. 2025) unsupervised decomposition on all kanji and compare to our hand-curated component1-5 columns. Flag discrepancies for manual review. Could reveal groupings the current system misses.
8. **Topological component ordering** — Ensure components always appear before the characters containing them (within groups). Partially enforced by STEM-first but not systematic.
9. **Learning cost calculation** — Implement a learning cost metric (stroke count + frequency + reading count + phonetic reliability) for automated kanji selection and ordering.
10. **Confusion-aware Anki scheduling** *(NEW from 2025-04 review)* — Annotate Anki export with intra-group confusion metadata (from LECTOR 2025). Kanji from the same MBO group should be spaced apart during review to reduce interference. Could add custom Anki scheduling tags based on group membership.

### Low Priority / Future Research
11. **Semantic subgroup automation via LLMs** — Use language models to create semantic maps for kanji within stem groups. EXECUTE benchmark (ACL 2025) shows Qwen 2.5 and Llama 3.3 are most capable at CJK radical decomposition. FT-CLIP's hierarchical tree embeddings could provide semantic-spatial features. Still "a rather time-demanding interdisciplinary project" per thesis.
12. **Formation tree representation** *(NEW from 2025-04 review)* — Adopt FT-CLIP's (Hong et al. 2024) hierarchical tree encoding to represent kanji structure with spatial relationships, replacing flat component1-5 columns. Would enable richer similarity computation but requires significant data restructuring.
13. **External data integration** — Incorporate kanjidatabase.com entropy/productivity data, kanjistat distance metrics, HierCode radical codebooks, or CJK Decomposition Data.
14. **Scalable FBO+phonetic system** — For kanji sets < 1,000, implement frequency-based ordering with phonetic reliability clustering.
15. **GenAI-enhanced learning materials** *(NEW from 2025-04 review)* — Use generative AI (Yu et al. 2025) to auto-produce comparison mnemonics, illustrations, and example sentences for kanji within the same MBO group. Enriches Anki export and web UI.

---

## Research Gaps (Updated 2025-04)

These areas have limited or no published research and represent potential novel contributions:

- **DisjointSet / Union-Find applied to kanji grouping** — our use of Union-Find for transitive group resolution appears novel. AttGraph (2025) uses GCN for component correlation, but not Union-Find for group resolution.
- **Hybrid rule-based + neural kanji ordering** — Han Zi Builder (2025) validates the hybrid architecture for component *assembly*, but no system combines rule-based ordering with neural similarity for learning order optimization.
- **Confusion-aware SRS for component-grouped kanji** — LECTOR (2025) models item confusion for general learning, but nobody has applied this specifically to kanji groups where visual/phonetic similarity is intentional.
- **Community detection on kanji similarity graphs** — still unexplored. Our DisjointSet is effectively a simple graph algorithm; more sophisticated community detection (Louvain, label propagation) on ViT-similarity or radical-embedding graphs could discover natural groups that our rules miss.

---

## Cognitive Validation (2025-04 update)

Three 2025 papers from BMC Psychology, PMC, and Frontiers in Language Sciences (Wang et al. 2025, and two related studies) confirm that semantic radicals are automatically activated during character recognition, especially for low-frequency characters. This provides strong cognitive science evidence that:

1. **Our component-based grouping leverages real neural pathways** — learners subconsciously process component-level meaning
2. **The effect is strongest for rare kanji** — our strategy of grouping infrequent kanji by shared components is especially well-supported
3. **Activation is character-dependent** — only works in real characters, not arbitrary component combinations. Our groups built from actual kanji (not artificial constructs) are correctly designed.
