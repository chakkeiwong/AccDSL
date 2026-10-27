# Language dependency audit after Version 5.11

26 October 2026. Inspected the current source/invariant/opening implementations,
prospective term-history state validation and source wrapper, and earlier
partial-population/history/opening/continuation/fiscal results.

| Candidate work | Existing evidence | Remaining behavior | Decision |
|---|---|---|---|
| Partial claim populations | Retained annual/interim population views with explicit unknowns | Actual invoice identities and gross/net/perimeter mappings still missing | Preserve; do not fabricate a complete opening |
| History-to-opening and continuation | ConditionalCompanyOpening/1 and ConditionalCompanyContinuation/1 retain witnesses, obligations and full results | General execution clearance and issuer facts remain unresolved | Do not rebuild these bridges |
| Prospective term history | Migration, state invariants, amendments, assessments, carry and matched command authoring already exist | General source-declared nested term invariants and construction remain distinct | Candidate broader language unit; needs its own exact invariant audit |
| Fiscal timelines | Current/deferred assessments and carry already composed with native clocks | Broader fiscal policy and source authority remain | Do not repeat completed scheduling |
| Current invariant source Unicode | Generic source preserves LF/CRLF and U+2028 within quoted data, but invariant_text.lines and render_rules call splitlines | A valid quoted separator breaks source roundtrip and can shift nested line references | Repair first as a concrete existing contract defect |

The debugging probe adds a literal U+2028 in a residual string of the exact
retained alpha invariant. The typed invariant remains valid; rendering refuses
with an unterminated-string error at line 71 because splitlines treats the data
character as a physical source newline. This does not invalidate the eight
checked source programs, which did not contain that character in invariant
text. It does disprove broader Unicode preservation for this nested parser.

The next unit preserves old parser/evidence files and derives a successor with
LF/CRLF-only physical-line handling. Test both top-level invariant residuals
and nested guarded-rule strings, exact UTF-8 locations, full source execution,
and all retained positive/adverse cases. No financial evaluator changes. The
term-history authoring gap remains on the subsequent queue rather than being
mistaken for a missing term-history implementation.

| Decision | Primary criterion | Veto status | Uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Repair Unicode source preservation | Reproduced valid typed string failing source roundtrip; exact code cause inspected | No global continuation veto | Wider nested-map rule language still incomplete | Execute accounting-invariant-unicode-repair-20261026.md | Whole DSL or independent acceptance |
