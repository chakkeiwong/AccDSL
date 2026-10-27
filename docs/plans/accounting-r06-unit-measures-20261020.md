# R06 — seven retained unit measures and declared numeric compatibility

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–06,MC23–26,MC28–35.
Output:data/accounting-master/r06-unit-measures-20261020/.

Question: do the exact retained unit structures, expanded measure names and
fact/type joins meet the source-supported unit rules that can be checked
without an installed processor or historical currency registry?

The baseline is the preserved instance/packet/portable representation and
full declaration/type map. Seven units are observed: USD,shares,USD/share,pure,
issuer Vendor,issuer Subsidiary and EUR. There are963 unit-bearing numeric/nil
facts and164 nonnumeric facts without units. Inspect retained XBRL2.1 sections
4.6,4.8 and5.1.1.3.1, plus both DTR percent and perShare annotations.

Primary criterion: seven exact source-bound unit records and1,127 fact/type/
unit joins, with checked per-element QName expansion, ordered ratio sides,
nonempty measure products, reserved xbrli names and no common measure on
opposite sides. Numeric type, rather than digits or unit presence, determines
whether a unitRef is required. Check monetary single-currency shape/namespace,
shares exact measure,pure exact measure,and per-share monetary/share ratio.
For general integers, preserve issuer-defined measures without inventing
count ontology or collapsing them to pure.

Currency code validity during each fact's period is an explicit unverified
condition. No authoritative historical ISO4217 registry has been inspected
in this unit. A currency-shaped QName is therefore a partial monetary-unit
result, not full validity. The same applies to currency validity in perShare.
No currency conversion, rescaling, unit algebra admission, accounting meaning
or registered runtime profile follows.

Research intent: test finite unit/type correspondence. Expected failures are
missing units for nil numeric facts, units on numeric-looking strings,
prefix-sensitive equality, cancelling identical numerator/denominator measures
silently, dropping multiplicity in products, treating perShare as a plain
monetary item, or multiplying percent values by100. Failed local guards veto
that record and trigger repair; missing currency history blocks full unit
promotion only. Protected-state changes/uncontrolled execution veto continuation.

| Choice | Provenance/reason | Failure mode/early discriminator | Status |
| --- | --- | --- | --- |
| Expanded QName identity | XBRL measure equality rule | Same prefix with different URI; alternate-prefix fixture | Source rule |
| Multiplicity-preserving products | Schema allows repeated measures; square-feet example | Set deduplication changes dimensional power; repeated-measure fixture | Required representation |
| No cancellation repair | XBRL requires simplest form and forbids same measure on both sides | Algebraically equivalent but source-invalid ratio; control remains rejected | Source rule |
| Declared-type classification | Completed inspected type graph | Numeric-looking nonnumeric facts misclassified; all164 unitless values checked | Required comparator |
| Currency namespace check only | Current source lacks historic code-validity evidence | Shape pass silently becomes ISO/date validity; per-fact unverified field | Explicit partial result |
| DTR perShare/percent annotations | Retained type semantics beyond base decimal | Monetary-vs-ratio mismatch or100x scaling; source-specific fixtures | Reviewed semantic requirement |

Skeptical audit passes for the bounded correspondence question. The opening
XBRL prose mentions a single simple measure, but its schema and square-feet
example allow a product of measures; preserve that explicit behavior rather
than implement a single-child shortcut. Full currency/history and unit-registry
validation are not replaced by count or namespace proxies. No new acquisition
or installed schema/processor execution. All actual Values remain unchanged.

Deliver unit/fact/type records, source/claim and six ledgers,fixtures,result/
review,manifest and separate R08 supplement. One-time prepare/construct/check/
record; then read-only replay. Only four live controls advance. Preserve
3.44/396/not_ready,53/6/46,zero whole-row closures,36 dirty paths,HEAD/index and
empty staging. Predecessor:r06-typed-domain-dates-20261020.

Commands:CUDA_VISIBLE_DEVICES=-1
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B; standard library only.
No upstream runtime,install,empirical campaign,commit,outreach,publication or fees.
