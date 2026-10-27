# Docling page outcomes and Version 2.25

10 October 2026. E14/C07/C08; MC23–25/27–29/31–35;
G5/G8/G11/G14/G17–18. Bounded author preparation is complete; E14 remains
open. The 168-page Version 2.25 is
`docs/design/proposal/manuscript-page-failure-20261010/accounting-product-proposal.pdf`,
SHA256 `caf4a818348b2a9df9c6943c2e9dcefd811ec302caaf91918db8d07541a624fc`.
Full proposal readiness remains `not_ready`; independent/human/domain
acceptance pending.

At Docling commit `eda5b5fc86d10b2b79a900ff3e69fc159d5f6014`, the inspected
timeout branch assigns `PARTIAL_SUCCESS` whenever positive expected pages
remain, including when none succeeded. The public converter yields that status
even with `raises_on_error=True`, provided downstream stages return normally.
Missing page numbers may be restored as empty page objects. Therefore no
exception, partial-success status or output page count is sufficient evidence
of complete page processing. The builder supplies the timeout state's source
path; the missing base pipeline was acquired from the same official pin and
inspected before drawing the return-path conclusion.

Five synthetic stage-outcome cases exercise exact retained integration,
placeholder, status, expected-page, base-execution and public-filter bodies.
All 35 fragment checks pass. All-requested and requested-subset cases report
success; partial failure and zero-success timeout report partial success;
zero-success failure without timeout reports failure and raises at the public
filter. Structured page errors and a document timeout error remain separate.
The fixtures inject data-class stand-ins and synthetic stage outcomes. They
do not run OCR, PDF backends, reading-order models, threads or a Docling install.
These are source-derived interface decisions, not observed failures on a real
filing or an end-to-end assembly result. Cleanup was a disclosed no-op stand-in.

The source also uses bounded worker and producer joins and can log a live
thread after shutdown waiting. No termination experiment was performed. Later
isolated execution must establish stopping separately from the timeout result.
A successful requested subset remains distinct from whole-source coverage.
The proposed exchange retains source inventory, requested pages, successful
pages, empty placeholders, structured errors and unprocessed/unrequested
frontiers. No conversion status admits an accounting interpretation.

The declared project is `docling-slim` 2.133.0. Its metadata array has nine
base requirements, despite an eight-package comment; optional extras and build
requirements are preserved without pretending they are an installed lock.
The MIT source notice is retained. Exact transitive versions/licences, model
weights/terms and compatibility remain open. This source inventory supplies
no distribution clearance or new software default.

Version 2.25 adds two source-attributed paragraphs to Section 13.13 and one
bibliography entry. All 23 candidate/preservation checks pass: 48 displays are
byte-identical, all 66 previous bibliography entries survive unchanged, and
only the title version, adapter section and bibliography changed. All prior
adapter prose and source qualifications remain exact. All 56 baseline files
and 1062 preceding manifest references verify with saved live-pointer copies.
The normal LuaLaTeX build succeeds with clean final logs. Its total wall time
was not recorded; do not interpret the component/tool waits as build runtime.

PDF 137–141 was read as one ordered five-page slice at 120 dpi; navigation
1–7 and the new bibliography page 164 were inspected separately. The local
transition now moves from individual-field loss to page-content loss, then
external dependencies and validation. The chapter boundary and licensing
qualifications survive. Author review remains `independent_reader_pending`;
no complete-chapter or whole-document read is claimed.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Reject status/count-only completeness | Exact source path and adverse fragments show that the signals do not identify processed content | Source pin and full relevant return path checked | Real model/assembly behavior not executed | Preserve requested/processed/error/frontier distinctions in proposed exchanges | Docling is unsuitable for layout |
| Retain Version 2.25 author candidate | Bounded omission repaired in rendered Section 13.13 | Preservation, references, source anchors and final logs pass | Independent comprehension remains pending | Continue source-specific E14 preparation | Human acceptance or whole-proposal readiness |
| Keep runtime and distribution admission open | Required evidence is absent | No installed/transitive/model lock or termination result | Exact future environment and intended use | Resolve applicable source/component terms and declared model paths before implementation | Installed compatibility, performance or cleared redistribution |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Status-only completeness is wrong relative to the proposed preserved-page target; final source/candidate checks pass. |
| Statistically supported ranking | None: no stochastic or accuracy comparison performed. |
| Descriptive-only differences | Five fixtures, 35 fragment checks, 23 candidate checks and one added page describe scope. |
| Default-readiness | No library/default promoted; this is a proposal repair. |
| Next evidence needed | Exact component/model terms, dependency decisions and later separate runtime/cleanup checks; independent reader/human/domain acceptance. |

Post-run red team: a synthetic stage outcome can conceal an impossible caller
state or an assembly exception. The inspected caller constructs failed pages
after timeout, and the prose expressly conditions the public return on later
stages returning normally. A real assembly failure would change the end-to-end
outcome without erasing the method-level status finding. The weakest evidence
is unexecuted backend/model behavior, so the result does not assert an observed
zero-page conversion. Remaining evidence gaps motivate further preparation,
not research-direction rejection or paid referral.

One ordinary sandbox request retrieved the official base-pipeline source with
HTTP 200; no source route was retried. No installation, GPU, product/controller
restart, outreach, publication, commit or push occurred. Unrelated dirty work
is preserved. Continue the next source-specific E14 terms/dependency question.
