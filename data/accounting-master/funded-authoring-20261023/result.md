# A matched authoring subset for the funded-year example

23 October 2026. S3/S4; MC13–18/23–26/28. All 24 documentary conformance
checks pass. Independently written text and typed JSON lower to the same closed
FundedYearInputsDraft/1 body. The body names its imported annual projection,
source hash, company/book/currency, floating share, four claim allocations,
facility capacity, loan terms, tax method, explicit assumptions and 14 dated
events. The parser supplies none of those amounts, rates or dates implicitly.

The selected 5%/two-day loan, principal, claim closing balances, event sequence
and dates agree with the previously checked full-year trace. Its interest and
tax effect are independently calculated from the authored terms. Duplicate
declarations or claim IDs, missing loan terms, changed projection/currency,
invalid dates, noncanonical fractions, invalid ordering, over-settlement and
insufficient capacity reject. An unknown collection date returns unresolved
with a named supply_event_instant:collection obligation. An authored nonzero
fee returns unsupported because this profile supplies no fee method.

The final dependency review added explicit income-before-tax requirements and
a named obligation for unknown timing. The final 24 checks include both.
These checks exercise a documented small parser and pure semantic validator;
they do not change the product grammar or run the production compiler.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain the matched example | Text/typed equality and source/trace correspondence pass | Missing data, source/context mismatch, claim/control errors, timing and capacity controls pass | The authoring body is not yet an input to a general event/accounting generator | Connect the typed input to successor execution semantics and integrate the checked design | Whole-company language completeness, durable execution or independent implementation acceptance |

The annual projection remains imported by reference. This preserves earlier
operating/accounting semantics but means the example does not author the whole
company from scratch. Facility eligibility and no intervening changes are
explicit synthetic assumptions; the earlier settlement-decision draft records
the richer eligibility/window distinction. POSIX-style tokenization is a local
documentary lexical choice, not a recommendation for the complete language.
Only the actually checked subset is supported.

Red-team assessment: identical frontends can agree on an insufficient model.
The comparison therefore also checks financial meanings against preserved
inputs and the independently retained journal trace. That still does not prove
that arbitrary valid inputs generate correct journals, that policies respect
all information restrictions, or that fee/revolving-credit/sector extensions
are defined. Those remain explicit design and implementation obligations.

Safe replay: verify.py. prepare.py refuses overwrite. grammar.md, schema.json,
example.accdsl and example.json preserve the complete proposed syntax/body;
checks.json and run-manifest.json preserve results, hashes, environment and
measured duration. The protected source and manuscript are unchanged.

## Input-driven execution follow-on

The authored body now drives a pure documentary executor. All 113 checks pass
across the 18 retained comparison paths. Every proposed journal and cash prefix,
closing account and joint statement result matches the independently retained
funded-year calculation. The executor derives tax from the accrued income
accounts and closes those accounts; it does not copy expected closing balances.

Moving payroll before collections produces a known 50 cash shortage. The
refused payroll changes neither cash nor payroll expense. The earlier draw
and supplier payment remain in the conditional state: a later failure does
not undo previously settled events. Unknown collection timing returns an
unresolved obligation before execution and produces no invented closing state.
Every result remains explicitly conditional and uncommitted.

An initial run completed the calculations but failed while recording its
manifest because Path was not imported. The import was repaired; the complete
rerun passed and wrote execution-manifest.json. This was an evidence-recording
failure, not a changed financial result. Execution-checks.json retains the
complete authored inputs and calculated outputs; verify_execution.py is its
safe replay entry point.

This resolves the previously recorded input-to-reference-execution gap for
this restricted profile. It does not resolve arbitrary company modelling,
facility admission, concurrency, durable commits, broader accounting treatments
or production parser/runtime obligations. The documentary input imports the
prior annual projection and retains its synthetic assumptions.
