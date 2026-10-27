# PubTables-v2 benchmark and metric result

19 October2026. P15/P17/P19; MC01–05/23/26/28–35.
The benchmark dependency is read within the recorded scope. Its populations,
input text, aggregation and continuation protocol now have checked source
anchors. Two exact fictional examples distinguish matching/aggregation rules.
Neither model adoption nor a manuscript repair follows from these findings.

Six acquisitions bind arXiv2512.10888v3 (2 June2026), the linked GriTS
repository/tree and two implementation files at
8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1. The paper has28 physical pages.
pdftotext warned of a mismatched EMC operator and omitted21–28; all eight were
actually read as rendered images, documented in rendered-reading.md. Pages1–20
were read as extracted text. All36 references were considered for role/next
action; that is not36 technical source reads. grits.py and conversion.py were
read fully and parsed as AST only. Their Git blob identities match the pinned
tree. No acquired code, library, model or dataset ran.

Annotation quality is conditional on the source annotation and selection
procedure. Sections3.1/B.2 align author XML/HTML table text to PDF text, requiring
mean normalised cell distance below0.02 and maximum at most0.2. Full-page/
document collections discard an article when an author-annotated table fails
alignment. Multi-part candidates also depend on a retained table detector and
concatenation across contiguous parts. These checks support consistency with
the original annotation; they do not prove every visible table was annotated
by the article's authors or that a financial concept is interpreted correctly.

The collections answer different questions. Cropped Tables deliberately
selects135,578 long/wide tables (at least30 rows or12 columns) from2023–2025
documents, including5,804 hidden-test examples. Single Pages has467,541 pages/
548,414 tables. Full Documents selects9,172 documents containing at least one
multi-part table, with137,095 pages and24,862 tables. The latter count is
9,492 multi-page+630 within-page split+14,740 single-part tables. It supplies
no row/column boxes for multi-part structure. All collections may supply
PDF-extracted words and boxes as inputs. Public train/test/validation and hidden
sets are described, but exact grouped IDs, inter-collection overlap and published
experiment provenance were not acquired. New dates/hidden tests do not prove
unknown model training contamination absent; no leakage is inferred here.

The generalized metric compares sets of tables, allows unmatched members and
aggregates pseudo true-positive scores. Rendered C.4 distinguishes TEDS's
table-count denominators from GriTS's cell-weighted totals and explicitly
changes original mean-per-input aggregation. The code's cell totals include
unmatched predictions. Its separately named exact-grid accuracy is recall-like,
dividing exact matched tables by true table count. A duplicate identical
one-cell prediction gives GriTS F1=2/3 while exact-table recall stays1. Reporting
the latter alone would conceal the extra predicted table.

Rendered C.3 describes choosing a correspondence that maximizes the sum of
individual table GriTS/TEDS scores. The current code instead maximizes the sum
of unnormalised cell-similarity totals. Under the literal normalised-score
reading, these objectives are different. For exact one-row strings with
A1=[a,b],B1=[a,c],A2=[a,c,x repeated18],B2=[a,b,y repeated18], single-character
LCS rewards produce the pair-total matrix [[1,2],[2,1]]. Each pair reward was
checked by dynamic programming and an independent exhaustive index-chain oracle.

| Pairing | Sum of pair GriTS scores | Sum of cell scores | Downstream cell-micro GriTS |
|---|---:|---:|---:|
| Diagonal | 11/20 | 2 | 1/11 |
| Cross | 4/11 | 4 | 2/11 |

The literal summed-pair-score objective selects the diagonal; the current code's
raw-total objective selects the cross pairing. This is a finite counterexample
to equality of those stated objectives, not evidence of which implementation
generated historical results. C.4 may motivate the code's weighting, but does
not make the two mathematical objectives equal. A source clarification or exact
experiment implementation is needed before claiming paper/code equivalence.

The second example has one perfect one-cell input and one completely wrong
nine-cell input. Mean-per-input GriTS is1/2; cell-micro GriTS is1/10. Both
formulas are valid for their declared weighting questions. They cannot be
silently interchanged in comparisons. This also limits comparison of older
macro scores with the newer benchmark. Current factored grid matching labels
itself heuristic and tracks an upper bound; no general optimum theorem or
external dependency behavior was checked here.

The expanded source repairs the earlier recall-only information gap. Section4.6/
Table6 reports ViT recall0.995,precision0.987,F10.991,AUC0.996. Positive pairs
number9,866; negatives number5,964 and come from contiguous pages with tables
in the same documents as positives. AppendixF.3 calls15,830 the full training
sample, uses200 epochs and best validation-F1 checkpoint selection. F.4 reports
20/1,862 ViT failures,46/1,862 ResNet failures and16 shared cases, including a
false continuation example. These source details answer a narrow protocol
question, but no independent grouped split or target-population false-merge
rate is established. The source does not supply a complete confusion matrix.

The dots.ocr merging result is0.6844 here, versus0.7495 in the later POTATR
paper, a printed difference0.0651. This benchmark explicitly requires matching
column counts before vertical concatenation. POTATR's short description does
not state that restriction. The discrepancy is real; its cause is not identified.
Do not average the scores, choose a preferred one or claim an observed regression
under identical settings without matching artifacts.

AppendixD records DocTags parser failures and Qwen context failures. Current
GriTS eval_htmls raises on failed conversion before adding a sample; it cannot
by itself establish how every experimental failure entered the final denominator.
HTML conversion is expressly outside the metric definition and version-dependent:
it uses the first table, repairs/clamps spans, inserts spaces between text nodes
and fills missing grid cells. Source inspection does not validate arbitrary
malformed HTML or installed lxml behavior. The default metrics exclude location;
cell text/structure alone do not bind entity, unit, period or page evidence.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Accept scoped source account |28 pages/two files read;134 checks pass | No identity/protection veto;8 altered controls rejected | Exact dataset/experiment IDs | Inspect official dataset card and small manifests | Reproduction or contamination clearance |
| Reject universal equality of two stated matching objectives | Exact one-row counterexample | Mathematical equality claim fails | Intended wording/historical implementation | Preserve both objectives; require explicit choice | Published results wrong |
| Preserve metric aggregation distinctions | Micro/macro and unmatched examples verified | Silent baseline substitution vetoed | Target-specific weighting question | State aggregation before any future comparison | One weighting universally preferable |
| Retain3.44 | Existing extraction/accounting distinction remains compatible | No confirmed manuscript contradiction | Wider survey/acceptance | Continue exact source gaps | Proposal completion |

| Inference status | Finding |
|---|---|
| Hard veto screen | No local model experiment. Exact matching-equivalence claim fails in the stated example; runtime/data claims remain unadmitted. |
| Statistically supported ranking | None established. |
| Descriptive-only differences | Reported table scores, precision/recall/failure counts, the two merging values and selected ablation outcomes. |
| Default-readiness | No metric weighting, matching rule, preprocessing, model or hyperparameter default adopted. |
| Next evidence needed | Exact grouped data/experimental provenance, explicit failure and metric policies, target-specific downstream comparison with uncertainty. |

Post-run red team: the paper may intend raw-score matching despite its C.3
wording; a later merging implementation may explain the differing result;
published data documentation may establish split safeguards not stated here.
These alternatives motivate the next source inquiry. Engineering evidence is
binding/static checks and finite algebra; model validity and scientific transfer
remain separate. No whole obligation closes. Six additive ledgers and R08
supplement preserve3.44/396/not_ready,53/6/46,HEAD/index and36 dirty paths.
Actual acquisition commands/timings live in source-ledger.json; lifecycle,
environment and elapsed time in run-manifest.json. GPU intentionally hidden.
