# Continuation after equal partial-payment totals

27 October 2026. Implements accounting-coupon-continuation-scope-20261027.md.
The skeptical audit accepts a restricted equality plus explicit distinguishing
witnesses; it does not authorize a generic financial-state quotient.

Target: same-origin schedules [1 on January 2] and [1/2 on January 2,
1/2 on January 3]. Their balances and contract memory coincide, but their current
dates, accepted event IDs and dated gross flows differ. The complete report
therefore differs even before a new instruction. Continuing a prefix must bind
to the external original carry, selection and exact prefix instructions.

The wrapper checks the retained prefix independently before materializing a
new typed program with that prefix as opening. A continuation's own report is
measured from that opening, while a cumulative report is measured from the
original carried opening. Retain both explicitly; do not reuse an old report
hash or pretend that historical flows vanished. The existing report routine
expects flows for its opening-to-closing interval, so segment reporting must
use flow suffixes and a matching empty-flow opening copy, without changing the
actual retained financial book or original history. If this requirement proves
unnecessary or invalid in code inspection, revise before running.

Primary tests: same-date continuation distinguishes current-date guards;
an ID present in only the split prefix distinguishes replay guards; a fresh
January 4 instruction preserves numeric equality but not full history identity.
Compare full states, every accepted journal/flow, complete reports, original
refusal and continuation refusals on the four chart/action origins.

Simpler alternative selected after report inspection: do not request a segment
report at all. The wrapper reports cumulatively from the original carried
opening, exactly as the prior oracle does. The continuation runtime uses the
retained prefix opening for execution only; reporting the entire period binds
the original opening and complete cumulative flow list. This avoids inventing
a reporting interval or deleting earlier history. Record that interface choice.

For common future dates no earlier than both prefixes, common fresh IDs, same
amounts and unchanged rules, equality of numeric state follows from the same
recurrence. This is a financial projection under explicit restrictions. Native
runtime resource limits may still refuse one request; no full runtime quotient
or compression implementation is claimed. The archive stays external and exact.

Promotion/pass requires independent complete comparisons and the distinguishing
counterexamples. Source drift, lossy history, wrong cumulative report or an
unqualified merge claim veto the result. Local checker defects trigger repair;
invalid upstream evidence or three exhausted 120-second attempts stop the unit.
No probabilities, actual default, funding, penalty or new accounting rule.
CPU only, GPU hidden, no install; use one-shot attempt writers and source locks.

Pre-run repair after source inspection: declared_company_program_v2.validate
always reports its opening against itself. company_book_reports_v1 requires
that opening to be at the period start with empty flows. A retained January 2/3
prefix cannot therefore be passed as that runner's opening. This is an interface
boundary, not economic infeasibility. Use one directly proposed typed event via
company_method_clock_v2, preserving the actual current book, and report from the
original January 1 opening. The new wrapper accepts exactly one continuation
instruction and labels it SelectedCouponContinuationStep/1. It does not pretend
to be DeclaredCompanyProgram/2 or silently reset dates/flows. Verify the original
runner's midperiod-opening refusal as a separate diagnostic. No attempt ran
before this repair; frozen source and earlier evidence remain unchanged.
