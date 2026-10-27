# R06 — retained context period boundaries and concept compatibility

20 October 2026, Asia/Hong_Kong. P15/P16/P17/P19; MC01–06, MC23–26, MC28–35.
Output: data/accounting-master/r06-context-periods-20261020/.

Question: what time boundaries follow from the exact retained context period
tokens, and do all 1,127 fact occurrences use a period form compatible with
their inspected concept declaration? This is distinct from completed source
locating, portable copying, fact lexical interpretation and text-block work.

The source inventory contains 193 contexts: 98 startDate/endDate pairs and
95 instants. All observed tokens are positive four-digit dates without timezone.
Use the retained XBRL 2.1 2013-corrected text, retained normative schema
correspondence, XML Schema 1.0 Second Edition date/dateTime/ordering rules,
actual instance, source inventory, proposed packet and full declaration map.
No new acquisition, installed processor, empirical run or runtime admission.

Evidence contract: exact date tokens and original byte slices are the baseline.
The primary criterion is 193 source-bound period records with explicit boundary
derivation and 1,127 joins from fact to context and declared periodType. Verify
all selected date spellings/calendars, strict end-after-start and declared
instant/duration compatibility. A startDate without time maps to the same date
at 00:00:00; an endDate or instant without time maps to the following date at
00:00:00, preserving absence of timezone. Do not infer UTC, reporting time zone,
publication time, information availability, or economic event time.

Research intent: the candidate is this finite documentary interpretation.
Expected failures are treating an end-date token as start-of-day, using lexical
strict ordering to reject a valid single-day period, assuming 365-day reporting
years, coercing missing timezone to the host timezone, or accepting a fact with
the wrong period form. Illustrative malformed/altered records must distinguish
these cases. A failed source/period check vetoes that record and triggers
investigation; it does not automatically reject the wider filing or direction.
Protected-source changes and uncontrolled execution veto continuation.

Diagnostics: full source correspondence, interpretation and form compatibility
are pass criteria; mutation fixtures are validation of those checks. Duration
lengths, repeated period signatures and fact counts by form are explanatory.
Do not treat identical periods as identical contexts or deduplicate facts.
Full schema, dimensions, units, duplicate-fact consistency, financial validity
and installed correspondence remain outside this unit.

| Choice | Provenance and justification | Failure mode / early diagnostic | Status |
| --- | --- | --- | --- |
| Retained XBRL period rules | Exact acquired section 4.7.2 and 5.1.1.1 | Wrong date role; same-day fixture distinguishes start/end | Reviewed local rule |
| Positive four-digit no-timezone date subset | Every observed token has this form | Generic rejection of otherwise valid dateTime/timezone forms; return outside_scope for those | Finite convenience profile |
| Gregorian calendar arithmetic | XSD date semantics; Python date only as one arithmetic path | Leap/month/year errors; independent ordinal algorithm and fixtures | Checked local mechanism |
| Unknown timezone | Source tokens contain none | Host-local or UTC inference; no timestamp/timezone APIs used | Required preservation |
| Equal source token on start and end | XBRL role-specific implied boundary | Lexical comparison falsely rejects one-day duration; explicit witness | Hypothesis to check |
| Calendar-day span | Difference of implied untimezoned boundaries | Mistaken elapsed UTC hours or financial year fraction; explanatory label only | Diagnostic, no financial admission |

Skeptical audit passes for this finite question. The exact comparator avoids
the wrong baseline (literal date comparison), and diagnostics cannot promote
source-level consistency into full XBRL validity. XSD Second Edition allows a
24:00:00 lexical form subject to restrictions, while the retained XBRL paragraph
uses older prohibiting language in its explanation. Do not use that wording
to reject broader dateTime forms: this unit leaves them outside scope and
records the edition boundary. Investigate technical passages before execution.

Construct the source/period/fact ledgers, fixtures, six source ledgers,
result/review and run manifest once. Prepare/check/record once; read-only
no-argument replay afterward. Add a separate R08 supplement. Edit only the
four live controls; preserve 3.44/396/not_ready,53/6/46,zero whole-row closures,
the 36 dirty paths,HEAD/index and empty staging.

Command environment: CUDA_VISIBLE_DEVICES=-1 and
/home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B; standard library only.
The predecessor is r06-textblock-fragments-20261020. Its frozen completion is
replayed and inherited, never reconstructed.
