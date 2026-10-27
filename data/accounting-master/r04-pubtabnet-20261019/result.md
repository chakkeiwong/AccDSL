# PubTabNet, EDD and TEDS: original-source inquiry

19 October 2026. P15/P17/P19; MC01–05/23/26/28–35. This is a documentary
preparation result, not an extraction benchmark or a new model recommendation.
The six exact acquisitions, 24 selected passages, six bindings and six separate
literature ledgers are retained beside this note. The inspected paper is
arXiv1911.10683v5, dated 4 March 2020; it is not certified as the published text.
The metric source is pinned to IBM PubTabNet commit
8ffde9024bd331f5a61c3c549fdf30dd3c3e43a5, not asserted to be the experiment's
original implementation. No external code, model or dependency was executed.

## What the source establishes

Sections III–IV define recognition of an already cropped table image. The
dataset comes from paired XML and PDF scientific articles, using 72-PPI
images. Bounding boxes are filtered by text similarity and length agreement;
tables with spans above ten, rare characters or mathematical annotation nodes
are removed. HTML curation removes nonvisual attributes and standardises header
cells. These operations make a selected recognition dataset; they do not
preserve every disclosure or prove the correctness of the source labels.

The v5 text reports a random 60/20/20 partition, 548,592 training examples,
and separately draws 5,000 simple and 5,000 complex tables for each heldout
set. The roughly 568k released total and the raw-population wording cannot be
silently treated as one reconciled denominator. The raw pool and release may
differ, but this source does not resolve that explanation here. Page 3 was
visually checked. No membership, article-level separation, contamination or
leakage check was performed; none is inferred from this textual discrepancy.

The encoder is modified ResNet-18; two attention-based LSTM decoders produce
structure and character-level cell content, with the structure state directing
cell recognition. Equation 1 combines the two cross-entropies. Section VI.A
limits training to approximately 399k examples with each image dimension at
most 512 pixels, at most 300 structural tokens and at most 100 tokens in the
longest cell. Images are resized to 448 by448 and channel-standardised.
Structure/cell vocabularies are32/281; decoder hidden sizes256/512; attention
hidden size256; embeddings16/80; beam width3. Five encoder variants are
compared on validation data and EDD-S1S1 is selected.

The source reports Adam training: structure-only weight1, batch10, learning
rate0.001 for10 epochs then0.0001 for3; joint weight0.5, batch8, rate0.001
for10 epochs then0.0001 for2. It reports approximately16 days on two V100s.
These are historical protocol descriptions, not reviewed AccDSL defaults.
No target-specific capacity search, seed policy, uncertainty estimate or
financial downstream validation is supplied by this read.

Table II reports mean test TEDS88.3 for EDD and78.6 for WYGIWYS. The latter
uses the same training subset and CNN, with truncated backpropagation of200
steps. Other comparisons mix cropped text-based PDFs and images; Adobe also
uses300-PPI images. The reported9.7-point difference is descriptive source
evidence for that setup. No repeated-seed interval or statistical ranking was
found in the inspected analysis. It is not an AccDSL result or current ranking.

Section VI.D relates performance to table size and suggests image reduction as
an explanation. Section VI.E trains and tests anew on500k synthetic tables,
partitioned420k/40k/40k and balanced across four categories. Its TIES exact
match comparison excludes OCR content errors for both arms. This is not a
zero-shot transfer test on real financial reports. Section VII expressly
leaves accurate table localisation outside the EDD input task and proposes
cell-coordinate prediction as future work. The later repository describes
nonempty-cell boxes in its July2020 dataset release; that later annotation
must not be retroactively attributed to this paper's original training.

## TEDS definition and the pinned implementation

Section V describes unit insertion/deletion costs, span-dependent cell
substitution and equation2's normalised tree-edit score. Two printed details
need reconciliation: it calls the cell substitution quantity a Levenshtein
similarity, and says substitution costs1 when either node is not a cell.
The code instead divides Levenshtein distance by maximum token length, returns
zero for equal noncell labels, and returns1 for differing tags or spans.
Page4 confirms the wording is printed; it is not a PDF-extraction error.
The intended metric and this exact wording should not be called identical.

The code selects only the first direct body/table, removes comments and may
strip configured tags. Cells become leaves whose content includes text
characters and inline markup tokens. However, the normalising denominator
counts descendants in the raw HTML table: it excludes the table root and
includes inline nodes which are inside cell content, not distinct nodes in
the converted tree. Thus it is not simply the number of converted-tree nodes
as an unqualified reading of equation2 might suggest.

Empty or absent input receives0. Batch evaluation iterates the ground-truth
keys, with missing predictions supplied as empty strings. Extra predictions
do not become extra evaluation samples. Parsing, span conversion and empty
table edge cases are not guarded by a general exception handler in this file.
APTED, distance, lxml, the parallel helper and their versions remain uninspected
dependencies; no runtime behavior of those components is claimed.

Four exact one-cell examples isolate consequences without executing upstream
code. The proof and narrow input restrictions are in execution-audit.md.

| Fictional input change | Cell distance | Code-style raw denominator | Closed-form score |
|---|---:|---:|---:|
|100 to900|1/3|3|8/9|
|The same change with both cells bold|1/5|4|19/20|
|100 to−100|1/4|3|11/12|
|Unchanged100, external unit changes from thousands to millions|0|3|1|

Identical markup raises the score in the second example by enlarging both the
cell token normalisation and the raw descendant count. The last example has
the same table but defined amounts100,000 and100,000,000. A perfect table score
cannot identify which external unit applies. These finite cases do not say
the metric is useless: it measures structure/text disagreement under a chosen
representation. They show why a high score cannot alone admit a financial
fact, sign, period, unit or provenance relation. Six elementary distance
controls pass; four altered outcomes and three out-of-contract inputs fail.

## Relation to the governing proposal and next repair

Chapter3 lines201–240 already separates structure, text supply, units and
accounting meaning. This inquiry supports that distinction and adds a precise
metric normalisation issue to future protocol preparation. It does not reveal
a confirmed error requiring a changed3.44 manuscript or replace its separate
TableFormer evidence. Whole-page segmentation, repeated/continued tables,
entity/period/unit attachment, footnote context, source positions and financial
validation still need independent acceptance criteria. Neither source supports
complete company-history reconstruction from a TEDS score.

The captured PubTabNet README says EDD source will not be released. That is
only a statement in these bytes. An unverified, model-recalled separate IBM EDD
repository route and an ECVA paper route are now queued; neither came from
readable search results. Their identity, published-edition differences and
model code must be checked in the next bounded unit. No global unavailability
claim survives this audit. Six-URL acquisition limit is reached here.

|Decision|Primary criterion|Veto status|Main uncertainty|Next justified action|Not concluded|
|---|---|---|---|---|---|
|Complete bounded source inquiry|Exact paper, selected full code and technical sections inspected|No protection veto; source/code equivalence blocked|Published edition and original experiment code|Verify distinct edition/repository leads|Literature or product complete|
|Keep TEDS as candidate diagnostic|Four finite consequences checked|Financial-correctness promotion veto supported|Target failure distribution and parser behavior|Specify source/context checks separately|Rejecting all table metrics|
|Do not transfer historical model ranking|Published means recorded faithfully|No target/uncertainty evidence|Seeds, split membership and financial domain|Target-specific protocol only if later authorised|AccDSL model superiority|

|Inference status|Finding|
|---|---|
|Hard veto screen|Exact paper/code-definition equality and TEDS-only financial admission fail; no empirical candidate was screened locally|
|Statistically supported ranking|None established by this inquiry|
|Descriptive-only differences|The paper's mean scores and reported compute cost|
|Default-readiness|No model, optimiser, parser or metric default promoted|
|Next evidence needed|Published-edition/code reconciliation, target-specific valid sampling and downstream financial checks|

Version3.44 remains396 pages and not_ready; all53 obligations, six interactions
and46 operation rows are preserved. This unit closes no whole row. All runtime,
installation, empirical, commit, external-engagement and fee holds remain.
