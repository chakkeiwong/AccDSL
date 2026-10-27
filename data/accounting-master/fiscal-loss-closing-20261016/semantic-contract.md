# FiscalLossClosing/1

Read-only documentary successor to CompanyComposition/1 attempt03. The request
contains exactly wire, operation=report, base_packet, base_sha256, opening,
ordinary_shares, share_findings, calendar, loss_expiry_exclusive and periods.
`reference.py` is the closed field definition; authored-cases.json is the
independent expected-value record. Canonical rational strings carry amounts.
No accounts, controller, service or persistent runtime are executed.

Resolve the fixed P5 packet and retained EU original source against input-lock.
Missing bytes are unresolved and changed bytes reject. Resolve the final State
in the packet rather than trusting caller balances. Require the original ended
compound, sold internal lot,90% interest and zero unmapped working-capital/tax
balances. Close all old profit accounts into legal retained earnings: P61.5,
S52.5. Keep original capital/equity, investment, cash and PPE. Derive group
equity724, NCI15.25 and parent708.75; retain ownership reserve−7.9 separately,
so parent retained earnings are106.65. Compare the entire caller opening with
this independently derived projection. Preserve the old packet and journals.

The new calendar starts2026-01-01 with a stub ending2026-07-01 exclusive,
then at most two July–June years. Every period has unique ID, exact start/end,
information cutoff and context findings. Gaps, overlap, duplicate close and
information after the cutoff reject; other fiscal calendars are unsupported
by this finite successor. The calendar supplies a nonempty change reason and
nonannualisation finding. Reports retain181/365/366 days, comparative IDs and
different-length disclosures. No future source applicability is inferred:
these are hypothetical dates under fixed historical accounting principles.

Each period independently admits continued control, unchanged ownership,
policies/currency, outside-basis tax exception, complete tax inventory, equal
book/tax depreciation, absence of group loss relief/offset rights, no other
operations/instruments, profit origin of every new tax effect, P-only loss
use, no carryback, admitted short-period tax law and immediate expense of paid
costs. The prior control interval ends at the new opening and is insufficient
without these renewed findings. Null findings are unresolved, false findings
unsupported and malformed/extra/missing fields rejected.

P and S operations each contain receipts, cash_costs, depreciation and tax_paid.
Recognise cash revenue/expense and reduce PPE for depreciation, subject to
funding and remaining-asset checks. The single loss origin may arise only in
P's first period; later negative P results or any S loss require broader loss
methods. All positive taxable profit uses legally available P losses, regardless
of their prior DTA recognition. The supplied law expires the unused remainder
at the end of the third interval. There are no carryback refunds or unrelated
tax bases in this projection. Current tax accrues to each legal entity; payments
settle only its own existing/current liability, not a manufactured refund.

The tax record contains current_rate, recovery_rate, law_date, effective_from,
law_id, enacted and complete_fiscal_terms. Law/effect dates cannot be after the
period start. Rates lie in[0,1] and are equal within each supported period;
other rates/schedules are unsupported rather than asserted universally invalid.
The examples change25%→30% at the second opening. These are supplied law facts.

Recovery has supported_loss, assessment_complete, convincing_next_period_evidence,
evidence_id, taxable_entity=P, authority=P-tax and usable_before_expiry. Positive
quantity requires convincing evidence and cannot exceed remaining usable loss.
Zero quantity with negative evidence is accepted; unknown evidence is unresolved.
The recognised quantity is the part expected to be used in the next period.
At the next opening remeasure that quantity at the new enacted rate. Actual
loss use consumes that previously supported next-period amount up to actual
use; excess use is a previously unrecognised loss benefit. Retain that distinction
for IAS12.80(e). This is a specified single-lot, next-period support schedule,
not an arbitrary FIFO allocation among multiple taxable losses.

Let L be opening loss, U=min(L,positive taxable income), X expired remainder,
and N new loss. Closing loss=L+N−U−X. Let q0 be prior recognised quantity,
a0 its DTA and t the new rate. The rate expense is a0−q0*t. Consumption expense
is min(q0,U)*t. Expiry charges any surviving recognised quantity at t. Reassess
the remaining recognised quantity to q1, charging (surviving−q1)*t. Their sum
equals a0−q1*t. A newly supported quantity produces a benefit; actual use of
unrecognised losses reduces current tax without reversing a nonexistent asset.
Every new tax movement has profit origin; old compound equity is preserved.

Close current income accounts to retained earnings once per period. Group
reports eliminate the unchanged investment100, allocate10% of S equity/profit
to NCI, and carry the parent's retained earnings and ownership reserve separately.
Ten unchanged ordinary shares and no potential instruments are explicitly
supplied; EPS=parent-attributed period profit/shares, with no annualisation.
The augmented compound-instrument company is not imported. Each report retains
legal/group balances, tax/loss origins, cash flows, closing books and comparative
period identity. Old reports are immutable values; later recovery cannot change
them. Direct cash and indirect profit/depreciation/tax movements must agree.

`present_offset` separately accepts category=current|deferred, gross asset and
liability, their entities and the four findings same_authority,
legal_current_offset_right, intends_net_or_simultaneous and
each_future_recovery_period. Current netting requires the right and settlement
intention. Deferred netting additionally requires the same authority and either
the same taxable entity or the admitted intention in every relevant future
period. False conditions retain gross presentation; unknown conditions leave
presentation unresolved. Mixed current/deferred netting is unsupported. Gross
balances always remain visible. This conditional helper establishes no actual
legal right and grants the P/S example none.

Refusals return null opening/closing and empty reports, journals, cash flows and
mutations, even when the error occurs in the last period. Requests are unchanged.
The accepted result is conditional_complete, never a declaration of compliance.
Wider loss-lot limits, differing recovery-rate schedules, OCI/equity tax origins,
new company/sector operations and errors/restatements retain their separate
methods and residual obligations.
