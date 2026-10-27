# Portable identity for company authoring and derived results

23 October 2026. S3/S4; MC02/04/05/08/10/13/18/24/25/28/34; G2/13/15/18.
Version 3.54 integrates the bounded language increments. The raw company
draft hashes still differ from the domain-prefixed portable record identities.

## Question and skeptical audit

Can one portable closure retain the exact authored family, expression policy,
derived company results and recovery reference without pretending their raw
draft hashes are portable record hashes? Reuse the existing strict portable
encoder/record contracts and CompanyPathExchangeDraft evidence. Inspect that
implementation before designing a new wrapper. The baseline is the exact
recorded family/expression/recovery bytes, not a hand-recreated numerical case.

The critical risk is calling an opaque JSON blob a complete portable semantic
record. A blob can preserve bytes but cannot alone expose dependency kinds,
roles, model identity, result meaning or admission. Conversely, changing old
draft identities would invalidate protected comparisons. Preserve both:
original blob digest and decoder, plus typed records with explicit references
and independently checked field correspondence. No historical or temporal
admission follows from successful import. No mutable module code is loaded
from the submitted packet.

Primary criterion: exact source-byte preservation, unique old-to-portable
mapping, closed schema/dependency validation, full current trusted replay and
retained unknown/partial family outcomes. Both literal and escaped Unicode
input must decode to the same portable DraftContent record where code points
agree. DraftImport and exchange identities remain distinct when their raw
bytes differ; old decoded draft identity is preserved separately. This
distinction was clarified during the resumed audit. Missing/altered dependencies,
wrong reference kind, forged results, codepoint normalization and false
admission claims veto the candidate. Missing indispensable comparator bytes
blocks dependent work only. Other ready methods/source work can continue.

First inspect prior common-envelope encoding and closure checks, then specify
the smallest additional record kinds required. Do not invent a parallel
general serialization library. Save one source-to-record-to-result example,
adverse checks, prior hashes and an exact migration comparison. Distinguish
content binding from semantic replay. This is a design/reference exchange;
physical persistence, arbitrary modules, real source admission and broad
language coverage remain open.

Assumptions: the current six authored scenarios are explicit unweighted
choices (protected baseline); the local decoder and evaluator are trusted
caller dependencies (existing trust boundary); exact raw blobs plus typed
records preserve two identities (required compatibility distinction). Earliest
checks are non-ASCII identity round trips, missing dependency closure and an
altered-but-rehashed cash result. These can expose wrong baselines before any
large packet construction.

Use CPU-only deterministic checks, a smoke then recorded/replayed verification,
bounded under five minutes per command. Save the reviewed design and evidence
under data/accounting-master/company-portable-authoring-20261023. Audit verdict:
proceed to focused inspection and contract design; revise if the existing
portable profile already supplies an exact compatible form. Keep all original
53/6/46 obligations and broader module/real-case residuals. S6 held; S7 deferred.
