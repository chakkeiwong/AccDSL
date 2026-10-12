# TableFormer: what the paper and retained consumer establish

12 October 2026. E08/C06 and E14/C07; MC23/25/29–35, G8/G9/G10/G18.
This is documentary preparation. No model, training code or inference pipeline
was executed. The protected manuscript is Version 2.44.

The model card's 95.4/90.1/93.6 values reproduce the simple/complex/all row
in Nassar et al. (2022), Table 4, printed p. 4620 (PDF 7). That table evaluates
PubTabNet **structure with content**, taking PDF documents with cropped tables
as input. The text comes from PDF cells. These numbers are not Table 2's
structure-only scores, a whole-page detection result, accounting-semantic
accuracy, or a measured result for the retained 4.0.2 consumer. Reporting them
as any of those quantities would be wrong relative to the reported target.

## Identity, version and correction check

The CVF title-specific landing page, linked main PDF and linked supplement
identify Ahmed Nassar, Nikolaos Livathinos, Maksym Lysak and Peter Staar,
*TableFormer: Table Structure Understanding With Transformers*, CVPR 2022.
The main PDF has ten pages, printed 4614–4623. CVF's bibliographic entry agrees.
Crossref resolves DOI 10.1109/CVPR52688.2022.00457 to the same title and authors,
but gives pages 4604–4613. That page field is excluded from our citation:
the inspected publisher-hosted PDF and landing page supply the locators.
The discrepancy is metadata evidence, not a reason to silently shift ten pages
or to identify a different paper. CVF describes its accepted open-access copy
as identical to the accepted version except for the watermark; it points to
IEEE for the final proceedings. The linked arXiv version was not retrieved.

The bounded correction check consists of the CVF landing and Crossref record.
No correction/withdrawal notice was visible on that landing, and Crossref has
an empty relation object with no update-to/updated-by entry. This does not
establish comprehensive correction clearance or identity with every later
version. Technical use is confined to this identified, inspected CVF copy.
Crossref's 109 citing works is retrieval-specific visibility metadata, not a
validity measure. Venue rankings were not obtained.

## Method, content and structural correction

Main Sections 3–4 (PDF 3–5; printed 4616–4618) describe cropped table images,
a ResNet18 feature extractor, transformer structure decoding and cell boxes
synchronized with cell tokens. The original structure language uses HTML tags,
including the split tags for row/column spans. The model predicts structure
and boxes; the cell content is acquired separately from PDF or OCR text.
The main paper and supplement do not establish a beam-search decoder.
The later code's argmax therefore does not prove a disagreement with a
paper-specified beam algorithm.

Supplement Section 2, pp. 2–3, matches predicted table cells to PDF text cells.
It first uses intersection-over-union, then intersection divided by PDF-cell
area, and corrects cell positions using alignment and median estimates.
The numbered steps can discard a column with bad matching, deduplicate
columns, append orphan text to existing cells, or create new structural cells.
Post-processing can change the table structure as well as its coordinates.
The illustrated successes/failures in supplement Figures 1–3 are selected
examples; they do not supply a random accuracy sample or an uncertainty bound.

The inspected official 4.0.2 source is a later implementation candidate, at
commit d1569fdffee1d09cb3111d6d5490991cb59d59fd. Complete methods read here:
TableModel04_rs.predict (110–328), TFPredictor.predict (714–853),
TFPredictor._merge_tf_output (379–436) and MatchingPostProcessor.process
(1265–1515); relevant constructor settings were also checked. The prior
loader unit verified all thirteen retained source bodies against Git blobs.

That consumer emits OTSL tokens (including fcel/ecel and span tokens), converts
them to HTML, and merges text from pdf_cell["text"]. It takes argmax predictions
and a cached step bound. The max_steps and k formal arguments are not consumed
in the inspected predict body; a beam_size setting is not evidence of active
beam search. The matcher receives iocr_page, and post-processing depends on
boxes, available tokens and its configuration. The process method skips extra
realignment above 300 PDF cells and gates overlap correction at 300 table
cells. Those are explicit later-code boundaries. Helper algorithms were not
fully audited, so conceptual correspondence with supplement Section 2 does
not establish exact algorithmic or numerical equivalence.

The archived Docling Technical Report, PDF 3–4, supplies a checked forward
relation: it says TableFormer was refined with a custom structure token
language. Its reference 9 (PDF 6) is Lysak et al., *Optimized Table Tokenization
for Table Structure Recognition*, ICDAR 2023, pp. 37–50,
DOI 10.1007/978-3-031-41679-8_3. Reference 12 identifies the 2022 TableFormer
paper. The tokenization paper itself remains unread and is the next concrete
literature lead; the Docling sentence does not substitute for reading it.

## Evaluation, training and transfer

Table 2 (PDF 7) reports structure-only TEDS: PubTabNet 98.5/95.0/96.75,
FinTabNet 97.5/96.0/96.8, TableBank 89.6, and SynthTabNet 96.9/95.7/96.7.
Table 4 reports structure with content; the model-card row belongs there.
Tables 3–4 and the paper's comparisons are source-reported results, not a
locally replicated ranking. The inspected material supplies no local paired
uncertainty analysis supporting a ranking of AccDSL candidates. We preserve
the attributed scores while making no comparative performance decision.

Main Section 3 and supplement Section 1 describe homogenization to 72 dpi,
training tables from 1×1 to 20×10, HTML normalization and rejection of
non-strict annotations where missing box attribution is ambiguous. Main
Section 5.4 says no filtering during evaluation. Training preparation must not
be misreported as filtering the evaluation population.

Main Section 5.1 (PDF 6) specifies 448×448 images, 28×28 features, input width
and height at most 1024 and tag sequences at most 512; two encoder/four decoder
layers, four heads and dropout 0.5. It reports three Adam optimizers, learning
rate 0.001, batch 24, 12 epochs and lambda 0.5, then learning rate 0.0001,
batch 18 and 12 more epochs or convergence. These are historical source
choices, not reviewed AccDSL defaults. The retained accurate configuration
instead has six/six layers, eight heads and dropout 0.1; fast has four/two
layers, eight heads and dropout 0.1. Both declare max_steps 1024 and beam_size
5. Labels alone do not establish the consumers' behavior, and no evidence here
identifies these model files with the paper's experimental checkpoints.

The printed box-loss Equation (1), PDF 6/printed 4619, visibly reads
`l_box = lambda_iou l_iou + lambda_l1`. The prose calls this a combination of
l1 and IoU losses and describes lambda_l1 as a hyperparameter. The expression
therefore lacks an explicit l1-loss factor expected from that prose. We record
the formula/prose ambiguity rather than silently repair it; reproducing
training requires checked training-source clarification. No training code was
inspected in this unit. Equation (2)'s combined objective was read, but neither
equation is being implemented or imported as a new mathematical result.

Section 5.4 acknowledges failures on very large tables after downsampling.
The Japanese example demonstrates one qualitative possibility, not general
multilingual or multilingual-financial-report accuracy. Figure and supplement
inspection also shows why plain extracted text cannot replace image review:
the cell geometry, diagrams and some formula glyphs carry the mechanism.

## Consequences for the proposal

The manuscript should explain why a plausible table still needs text-source,
cell-matching and accounting validation. Add the original method and correctly
attributed score scope to the literature chapter, and make the adapter retain
input text locations and structural corrections. Describe the original HTML
method and later OTSL consumer as distinct inspected versions. Keep training
reproduction details and configuration audit in this source dossier.

This closes a bounded source-reading omission, not E08/E14 or whole-survey
coverage. Runtime compatibility, full helper equivalence, checkpoint identity,
training reproducibility, target-specific tuning, heldout financial-document
performance and human acceptance remain open. They do not veto the bounded
manuscript clarification or the next tokenization-paper reading.
