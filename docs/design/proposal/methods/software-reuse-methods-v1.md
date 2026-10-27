# Software reuse and adapter method

Reusable software supplies capabilities and interfaces; it does not supply
AccDSL accounting authority, source completeness or semantic identity. This
method addresses MC23–MC25, MC27–MC29 and MC31–MC35. It adopts the retained
adapter audit and evaluation protocol, which are source inspections rather than
runtime integrations. No package installation or external service is required
for the proposed first evaluation.

## R1. Adapter boundary

Every adapter has a pinned source commit/release, dependency/model/taxonomy
lock, license record, input manifest, output schema, preservation sidecar,
failure map, source/time view and review/admission event. It must retain original
bytes and full SHA256 before parsing, literal/transform data, entity/context/
dimensions/units/periods, source locators, duplicate occurrences, nil/blank/
invalid distinctions and unresolved/excluded content. Normalized output is a
proposal; source identity and financial assertion identity are separate.

The adapter pipeline is: preserve bytes and receipt; inventory package/pages/
cross-references; parse candidate structures; attach source occurrences and
context; record transformations; map concepts only with an admitted mapping;
run independent field/context checks; submit proposed records for review; then
compile accepted records into portable IR. A successful conversion count cannot
close a package or approve a journal. A partial converter retains successful
units and exact failures/frontier. Network/model downloads are disabled unless
explicitly included in the manifest.

## R2. Candidate roles and limits

| Candidate | Proposed role | What the inspected source supports | Boundary |
| --- | --- | --- | --- |
| Arelle | Native XBRL facts/context and validation candidate | XBRL 2.1, dimensions, formulas, taxonomies, Inline XBRL, CLI/Python/API; Apache2 source audit | Native IDs are not portable source keys; duplicate handling/options, transforms, taxonomy/context and issuer interpretation need sidecars |
| Docling | PDF/layout/table development candidate | Multi-format/PDF layout, reading order, table and XBRL entry points; MIT code | Model terms/dependencies need separate locks; Markdown is derivative; its XBRL graph loses full fact/context/unit/typed-dimension data in inspected path; no runtime ranking |
| pdfplumber | Deterministic PDF geometry baseline | MIT source and explicit geometry candidate from saved audit | Text extraction/layout errors and no accounting semantics; inspect every page/failure |
| ACTUS | Contract schedule candidate | Retained CC-BY-SA technical specification for algorithmic financial contracts | Contract schedule is not accounting rule, source interpretation or group/statement method; license/share-alike integration review required |
| QuantLib | Valuation/rate/date candidate | BSD3 quantitative-finance library source/README | Curve/price output does not choose EIR, fair-value unit, tax or posting treatment; calendar/version locks required |
| Z3 | Finite constraint/feasibility candidate | MIT theorem prover and language bindings | Solver `sat` is only a witness/certificate under encoded model; encoding omissions and unknown/timeout remain P16 statuses |
| Beancount/hledger | Plain-text double-entry comparison/ledger exchange | GPLv2/GPLv3+ ledger languages, reports and multi-currency behavior | Ledger balance does not carry source evidence, alternatives, authority or economic state; copyleft/interface review needed |
| OpenFisca | Tax/simulation comparison candidate | Python microsimulation core with country packages and tests | Country package rules are jurisdiction-specific; model outputs do not establish real tax authority or AccDSL history lineage |
| Stan/Pyro | Optional continuous-inference backend | Stan HMC/ADVI/MLE and Pyro probabilistic programming interfaces; licenses inspected | Target-specific posterior, parameterization, convergence/MCSE and downstream checks required; no sampler default/promotion |

The adapter's capability matrix distinguishes source preservation, context,
table/layout, concept mapping, time/admission, review and failure behavior.
Native availability is not faithful interpretation. Arelle's object ID is an
internal index; Docling's document hash and output are tool fields. Full source
hash and original occurrences remain AccDSL records. Typed dimensions, composite
units, lexical dates, transformation metadata and link roles must survive or
the field is unresolved.

## R3. Evaluation and license admission

The first evaluation uses the existing 192-report panel and four exposed
development packets only; it is not a heldout population and cannot rank models
from 31 provisional labels. Baselines are manual located source units and
transparent native extraction; then tuned pdfplumber/Arelle where applicable,
plain Docling, and explicit context/footnote repair. All candidates receive the
same files, disclosure roots, context/taxonomy resources and declared budgets.
Metrics are separate transcription, required context, table structure, mapping,
source support, retention/unknowns, historical admission and resource cost.
False acceptance, hash/locator loss, look-ahead, silent omission and untracked
download are vetoes. Cell counts are clustered by document/issuer; small pilot
differences are descriptive only. No threshold or accuracy ranking is promoted
without a predeclared population and uncertainty design.

License admission records code/data/model licenses, dependency licenses,
copyleft obligations, model terms, source redistribution restrictions, commit
hashes, notices and intended distribution boundary. A permissive code license
does not clear an embedded taxonomy, pretrained model or upstream data. An
adapter is eligible for a real branch only after these records and the matched
field-loss cases pass; otherwise it remains a candidate or synthetic-only path.

## R4. Worked adverse cases

An inline numeric fact with raw text `1,234`, an explicitly admitted comma-grouping
numeric transform, scale `-3`, context `c1`, unit `USD`, nil=false must retain raw
bytes, transformed value 1.234, context and
unit. Applying the scale twice gives 0.001234 and fails. A nil fact is unknown,
not zero. A date-only instant remains lexical `2024-12-31` while an exclusive
flow end boundary can be `2025-01-01`; publication/ingestion timestamps are
separate. Two identical values with different contexts remain two occurrences
until an explicit alias decision. A Docling export that loses contextRef or a
typed dimension returns preservation_failure for the affected record, even if
its Markdown looks readable. Arelle validation success does not establish
complete referenced-package closure. These cases bind directly to the P16
evidence/time/review/failure contracts and can be checked without installing
the candidate libraries.

Reuse decision: adopt the adapter boundaries and candidate roles above. P19
assesses source/licence/evaluation specifications; runtime integration and a
benchmark require later implementation authorization. P15-E14 remains open for
the broader product interface and distribution evidence.
