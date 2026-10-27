# R06 — Native-XBRL translation into the existing portable records

18 October 2026. P16/P17/R06, with additive P19/R08 evidence.
MC01–06/23–25/27/30–35; G2/G9/G11–13/G17/G18.
Authorised proposal/specification and internal preparation only.

## Question and baseline

Can a bounded native-instance adapter specify source-preserving fact, context
and unit records using the current P16 portable architecture, while refusing
unsupported financial meaning? The baseline is L1/L2 of
`docs/design/proposal/architecture/language-ir-contract-v1.md`, E1/E3 of
`evidence-contract-v3.md`, T1/T2 of `time-contract-v2.md`, I1 of
`interfaces-contract-v1.md`, and their integration/amendments. The older
`docs/design/spec/core-ir.schema.json` is not the portable baseline.

Keep the 15 October selected Arelle commit
`01f6a4656c2c6551d2f05f31c9d74366d133ee7e`, its eleven documentary exchanges,
the 18 October accessor-boundary inquiry and Version 3.44 unchanged. This unit
adds a proposed, closed documentary profile under the existing six-field
Record envelope. It does not silently register a production schema or select
a runtime. Preserve LegacyImport/ImportMapping, typed Ref, BlobRef, exact
Rational and Unknown semantics; no parallel generic envelope.

## Evidence contract and intent ledger

| Item | Requirement for this unit |
| --- | --- |
| Mechanism | Separate retained XML bytes/occurrences, decoded source fields and explicit proposed conversions; retain every repeated fact |
| Expected failure | Convenient accessors normalize dates, identifiers, units, values or defaults; an XML context is mistaken for complete financial Context |
| Primary pass | A precise field map and closed profile, author-specified positive/negative fixtures, and a read-only verifier that checks byte locators, exact values, field coverage and dependency closure |
| Promotion veto | Source/hash mismatch; field loss; dangling/cyclic portable Ref; coercion of nil/unknown/default to a source value; unsupported date or financial interpretation; attribution of runtime output |
| Continuation veto | Corruption of protected inputs or inability to preserve required bytes; stop only the dependent unit and investigate |
| Repair trigger | A fixture exposes unsupported semantics or an uninspected source dependency: preserve an explicit unknown/unsupported outcome and inspect the smallest required source span |
| Explanatory diagnostics | Record/mapping/check counts, source lines, execution time and schema validity show bounded consistency only |
| Not concluded | Parser correctness, taxonomy/XBRL validity, faithful extraction of arbitrary XML, accounting admission, complete dependency/rights closure, empirical performance or product readiness |
| Preserved result | `data/accounting-master/native-xbrl-translation-20261018/`, proposed adjunct under `docs/design/proposal/architecture/`, additive R08 supplement and refreshed live controls |

This is deterministic specification work, not a stochastic method comparison.
Engineering consistency, source semantics and accounting acceptance remain
separate. No research benchmark or numerical ranking is authorised here.

## Skeptical audit before execution

The inherited first idea risked targeting the old Core IR and treating Arelle
properties as original XML. Corrected before implementation: use current P16
records; original bytes, decoder interpretations and effective/presentation
values occupy distinct fields. `contextID` and `unitID` are not interchangeable
raw-token accessors. Period normalization delegates to XmlUtil; inspect it
before specifying conversions. An identifier scheme/value is source evidence,
not automatic legal-entity resolution. Namespace, unit, period and dimensions
cannot infer book, perimeter, accounting basis, fiscal calendar, publication
time, review or admission. Non-dimensional segment/scenario content must survive.

Audit passes for a bounded proposed adjunct with these corrections. Required
source spans will be read before their claims are written. All fixtures are
explicitly authored synthetic examples, not observed Arelle output. The checker
uses only Python's standard library on supplied evidence, with no upstream
imports, network, installation, controller, parser campaign or manuscript build.
Finite fixtures cannot certify general losslessness or interoperability.

Resume audit, before fixture execution: the unfinished checker conflated Int
with nonnegative metadata, concatenated unit numerator/denominator checks and
allowed an unrelated source entry to justify a named conversion. Repair these
before preparing evidence: signed Int with separate count/span constraints,
independent unit-side/order checks, closed packet/type assumptions and exact
owning-entry provenance. Check nested decoded text and all dimension/container
spans against XML. Mutations must reach the intended semantic diagnostic,
using rebuilt dependent Refs where needed rather than merely stale hashes.

## Default and assumption audit

| Choice/provenance | Justification | Failure mode and early check | Status |
| --- | --- | --- | --- |
| Current P16 six-field Record, L1 | Required cross-contract baseline | Old envelope drift: check exact envelope/Ref/BlobRef shapes and digests | Reviewed documentary baseline |
| Pinned native Arelle source, prior selection | Stable inspected comparator | Source change or inherited inline behavior: hash and line-bound checks | Documentary baseline, no runtime recommendation |
| UTF-8 synthetic XML fixture | Makes byte ranges directly reproducible | General-XML inference: retain source bytes and label decoding limits explicitly | Convenience fixture only |
| Decimal exactness, L1/E3 | Preserve base-ten source values | Binary-float drift: reduced rational and nonterminating fraction cases | Existing requirement |
| Date normalization only when supported | Avoid period-end/publication confusion | Wrong one-day adjustment or timezone claim: distinct date/dateTime fixtures and unresolved cases | Explicit conversion hypothesis bound to source |
| Unknown financial Context fields, L2/E3 | Missing semantics cannot be inferred | Taxonomy or issuer-name defaults: negative cases must retain unknown fields and block arithmetic/admission | Existing requirement |
| No deduplication, selected native scope | Every occurrence is evidence | Equal values collapse: duplicate-value/different-locator fixture | Existing requirement |
| Proposed profile namespace, not global registration | Specify missing portable bodies without rewriting frozen contracts | False production-compatibility claim: label profile proposed and evidence_mode specification_example | Derived engineering proposal |

## Execution and validation

1. Read remaining current contract interactions and selected source spans for
   period, entity, dimensions, units, QName and XML locators. If a needed
   implementation is absent, retain that source boundary as not checked.
2. Specify field-by-field mappings, raw span identity, explicit conversions,
   unknowns, failures, admission boundary and exact dependency/byte closure.
3. Supply a closed profile and authored portable records using the existing
   envelope. Provide multiple-output LegacyImport/ImportMapping correspondence
   and source-field accounting. Include repeated facts, nil, accuracy absence,
   fractions, unit products/division, dimensions/non-dimensional content,
   missing references and unsupported inputs.
4. Run the smallest deterministic consistency check. Exercise meaningful
   corruptions of locators, values, Ref closure and admission claims; preserve
   diagnostics rather than merely mirroring a successful serializer.
5. Record checked conclusions, residuals, exact command/environment/timing and
   hashes. Snapshot four live controls, bind evidence additively to the exact
   3.44 candidate, then refresh controls without rewriting frozen assessments.
6. Continue the next independent ready preparation task. Missing runtime or
   independent acceptance is not a global blocker.

No empirical execution, installations, commits, outreach, publication, fees or
manuscript revision is part of this unit. Preserve the pre-existing index,
36 tracked dirty entries and all source/frozen evidence.
