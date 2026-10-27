# POTATR competitor and primary-source result

19 October2026. P15/P17/P19; MC01–05/23/26/28–35.
Decision: the previously metadata-only forward lead now has a bounded technical
reading. Its page-level graph approach is relevant to ingestion, but adoption,
runtime reproduction and financial transfer remain unestablished. No3.44
manuscript defect is confirmed by this comparison.

The acquired arXiv2606.09788v1 is a16-page paper dated8 June2026, matching the
retained title and seven authors. Method, training, inference/evaluation,
limitations and appendices A–C were read, with rendered pages4/7/8/15 inspected.
The31 references are triaged, not technically read as a group. Five requests
are retained with actual curl JSON receipts. The publisher independently
matches the paper and names DAS2026/LNCS16851, first online28 August2026,
but citation/copyright year2027. The old OpenAlex date27 August is not the
primary online date. The publisher PDF endpoint returns200 HTML after seven
redirects. Its actual author repository link returns404. The published
technical edition and implementation therefore remain unchecked; global code
absence is not inferred. Appendix A announces an intended MIT release, which
does not license an unacquired code/model artifact.

POTATR extends TATR from a cropped-table model to page-level prediction:
16 object classes,250 queries, and a three-layer relation head connecting
tables to rows, columns, captions and footers (Section3.1/Figure2). Most weights
start from TATR-v1.1-Pub; expanded heads and queries start randomly. Training
uses100 epochs on Single Pages, then35 with additional table-free pages and
repeated large tables (Section3.2). This is the source's protocol, not a reviewed
AccDSL default. Dataset construction, splits and page-set metrics depend on
PubTables-v2, reference21, whose technical source is the next inquiry.

Text remains externally supplied. Table2's direct-text result combines detected
geometry with PDF text; three other rows use separate OCR. The paper reports
GriTSCon0.9636 for direct text and0.8799 with docTR. The difference is0.0837,
but that score change does not prove an additive causal partition of all errors
into structure and text. Even GriTSTop varies across these text-supply rows;
the downstream assignment/post-processing and metric definitions require their
own source inspection. Section7 explicitly limits evaluated documents to
English PubMed articles and leaves other domains/languages untested.

Two comparisons answer different questions. Section4.2 trains three graph
architectures for10 epochs, with different initialisation and each model's
default losses/weights. It nominates a practical warm-start strategy, but does
not isolate the causal contribution of pretraining. Table2 compares the fully
trained POTATR with zero-shot VLMs/MLLMs, and PDF-text supply differs from
image-generated text. Those conditions must remain visible in any component
selection discussion. No paired uncertainty or local target-specific benchmark
supports an independent superiority claim here. The paper's reported ordering
is retained as its descriptive result.

Table4 uses one A10G24GB for local models, batched VLM inference, API-priced
frontier models and a$2.45/hour local instance. Its52,031 pages/hour implies
about132.4 times the printed393-page/hour comparator; the hourly formula gives
$47.0873 per million pages, rounded to$47. The source also describes a21ms
model step, whereas inverse aggregate throughput is about69.19ms/page. These
can measure different scopes/overheads and do not by themselves contradict
each other. A deployment estimate must account explicitly for rasterization,
text/OCR, batching, post-processing, errors and any continuation model. The
paper supplies no complete local deployment manifest proving these all share
one timing boundary. Fixed queries and observed bins do not establish universal
constant wall time for arbitrary page resolutions or deployments.

Section5.2 says Full Documents deliberately emphasizes multi-page tables; it
is not a typical-document population. Appendix C reports0.6710 for independent
POTATR pages and0.8269 after a separate86M-parameter ViT-B-16 continuation
classifier plus vertical concatenation. The printed complement-score reduction
is47.4%; the fractions of the gap to the printed Gemini/GPT values round to
60%/73%. Those arithmetic statements pass, but they remain descriptive score
transformations, not financial error rates. Recall0.995 alone cannot establish
the claimed near-optimality of continuation: precision, false merges and the
decision cost matter too. Within-page table-part merging remains explicitly
unhandled. None of these scores tests entity, period, units or accounting meaning.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Admit source-specific competitor account | Verified preprint; technical and appendix read;108 checks pass | Identity/protection checks pass | Published-edition differences and source code | Preserve exact version/status | Implementation reproduction |
| Retain qualified comparison | Supplied text/training/domain/timing contexts inspected | Blanket ranking and causal attribution unsupported | Paired uncertainty and target-specific behavior | Read dependency benchmark before protocol design | Financial suitability or superiority |
| Preserve3.44 | Current chapter3 lines201–240 already distinguish structure/text/accounting checks | No contradiction established | Broader coverage and independent acceptance | Inspect PubTables-v2's technical definitions | Survey or proposal completion |

| Inference status | Finding |
|---|---|
| Hard veto screen | Repository route404; published PDF route is HTML. These veto dependent implementation/edition claims only. No model run occurred. |
| Statistically supported ranking | None established by this inquiry. |
| Descriptive-only differences | Tables1–5, timing/cost ratios and score/complement changes. |
| Default-readiness | No architecture, source, hyperparameter, OCR or evaluation default promoted. |
| Next evidence needed | Exact implementation/experiment provenance, benchmark split/metric construction, matched input/tuning comparisons and paired uncertainty on the chosen financial task. |

The engineering ledger contains source identity/reading and nine exact
printed-number relations, with five altered controls rejected. Numerical/model
validity has not been tested. Scientific interpretation remains conditional
on the source's populations and inputs. Six additive literature ledgers close
no mission obligation. Strong alternative explanations include the supplied-text
advantage, different initialization and benchmark selection; a matched ablation
or task protocol could resolve their contributions. The weakest evidence for
reuse is the unavailable implementation and uninspected benchmark dependency.

The first local check rejected equivalent reduced/unreduced fraction strings;
verification-repair.md records the checker defect. Comparing exact rational
values repaired it; the successful check produced108 assertions. No completed
stage was repeated. Acquisition commands/timing and bindings are in
source-ledger.json; lifecycle/environment/elapsed time in run-manifest.json.
GPU was intentionally hidden; only standard-library Python/read/render tools
ran. Preserve3.44/396/not_ready,53 obligations/six interactions/46 operations,
HEAD/index and all unrelated tracked dirty files. No global continuation veto.
