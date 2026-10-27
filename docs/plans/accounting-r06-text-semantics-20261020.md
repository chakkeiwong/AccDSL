# R06 — retained Text candidates and declared value spaces

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–06, MC23–26, MC28–35.
Output: data/accounting-master/r06-text-semantics-20261020/.

Question: what narrow declared-type interpretations can be supported for the
157 retained Text candidates, without changing their frozen portable Values?
The selected set contains 14 boolean, 17 duration, one date, one gMonthDay,
77 string, 23 normalizedString and 24 token terminals. The seven Unknown
facts and 963 numeric/nil observations have separate completed inquiries;
do not reconstruct them. There are 112 selected concepts and 35 path nodes.

Evidence contract: the exact comparator is the retained instance text,
declaration/path/facets, and XML Schema 1.0 Second Edition dated 28 October
2004. The primary pass criterion is a separate source-bound disposition for
every selected occurrence: supported narrow interpretation, explicitly
unsupported scope, or documented mismatch. Do not equate a stored Text tag
with a declared string type. Full schema/XBRL validity, installed behavior,
embedded-markup validity, enumeration-domain membership and accounting meaning
remain unadmitted. All original Values and validation statuses remain intact.

Research intent: expected failure modes are boolean truthiness of nonempty
text, converting years/months to a fixed number of days, assigning a timezone
to an unzoned date, reducing a recurring month/day to an instant, omitting
inherited string restrictions, or applying Python regex/Unicode behavior as
if it were the full XSD specification. Missing source/facet support vetoes
the affected interpretation; it does not silently become a valid result.
Changed protected input or uncontrolled processor execution vetoes continuation.

Default and assumption audit:

| Choice | Provenance and reason | Failure mode / early diagnostic | Status |
| --- | --- | --- | --- |
| 2004 specification | Already retained primary edition used by predecessor | Importing later rules; bind exact sections and dates | Reviewed bounded comparator |
| Explicit whitespace rules | Part 2 section 4.3.6 and built-in definitions | Unicode strip loses NBSP; preserve/replace/collapse fixtures | Source-derived |
| Exact boolean literals | Section 3.2.2 | Nonempty false becomes true; test false, 0, TRUE, empty | Source-derived |
| Duration component tuple | Section 3.2.6 | Fixed-day conversion invents a value relation; retain six fields and source partial-order qualification | Documentary representation, not canonical equality |
| Positive four-digit unzoned date subset | Actual retained spelling; section 3.2.9 and dateTime/Appendix D prerequisites | Subset refusal confused with invalidity; valid timezone/long-year/negative-year examples return outside_scope | Convenience subset |
| Unzoned gMonthDay subset | Actual retained spelling; section 3.2.12 | Invented year/timezone; use a leap-year calendar only to check day membership | Convenience subset |
| Restricted string patterns | Actual retained derivation children and Appendix F | Python Unicode/name classes diverge; support explicit ASCII proof subset and return unknown beyond it | Local formalization with bounded scope |
| Exact text preservation | Frozen coverage and instance | Whitespace-normalized values replace raw text; store both and compare raw bindings | Required invariant |

Skeptical audit passes after inspecting all selected facet kinds. Fourteen
custom restricted types include enumerations, min/max lengths and five
pattern families; terminal-only checks would be insufficient. Enumerations
are compared in the base value space; lengths count characters. Pattern
matching is source-specific, with whole-string membership and no generic
XSD-regex equivalence claim. The observed URI/name patterns are ASCII; general
Unicode name/category support is deliberately unknown. Finite calendar
membership is checked independently with standard-library date arithmetic.

Pre-mortem: all records receive a successful-looking status while the
checker ignores a facet or changes their meaning. Bind and inspect actual
derivation children first; unsupported constraints produce an explicit
unresolved status. A component tuple must not be promoted into duration
ordering, canonical equivalence or financial cash-flow timing.

Deliver bounded source extracts, type/facet audit, 157 separate interpretations,
positive/negative/out-of-scope fixtures, result/review, six additive source
ledgers, manifest, preservation/completion bindings and separate R08 supplement.
No new source acquisition is planned. Standard-library Python only, with
CUDA_VISIBLE_DEVICES=-1 and -B; no package install or acquired code execution.
Use the numeric unit's local XML source-binding helpers with exact hashes,
not any upstream parser or completed predecessor lifecycle stages.

Only four existing live controls may advance. Preserve 3.44/396/not_ready,
53 obligations/six interactions/46 operations, zero whole-row closures,
HEAD/index/empty staging and 36 existing dirty paths. Prepare, construct,
check and record once; future replay has no flags. Continue independent work
while E3's target direction and six scientific choices remain unselected.
