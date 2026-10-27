# From the reduced financing equations to the common accounting books

This is a local derivation for the supplied synthetic example. Existing common
engines remain byte-for-byte unchanged and retain their own dependency checks.
The bridge authors explicit method records; it does not invoke the standalone
reference's posting function inside the common engine.

The mathematical reference tracks economic equity after the period's income
and expense. The common book stores signed debit balances for cash, assets,
interest expense and fee expense, with credit balances for debt, payable,
capital and operating income. For its signed balances B, reduced equity is
-B_capital-B_income-B_interest_expense-B_fee_expense. Reduced liabilities are
-B_old_debt,-B_facility_debt and-B_interest_payable. Cash/assets retain their
sign. This explicit map is needed: assigning every expense directly to the
common capital account would erase the income statement distinction.

An interest accrual I adds+I to expense and-I to payable. Applying the map
reduces economic equity by I and increases the claim by I. Paying I adds-I
cash and+I payable, leaving profit unchanged. A draw/pay adds cash0.75-I,
facility debt-1, fee expense0.25 and payable+I. This maps to the same cash,
liability and equity changes as borrowing1, paying fee0.25 and settling I.
Separate cash-flow origins preserve those three legs even though the journal
aggregates their net cash entry. The receipt R adds+R cash and-R income.
Repayment adds the signed facility balance to cash and its opposite to the
liability, so debt becomes zero without changing the persistent used flag.

The opening has cash5.5, assets94.5, old debt-100 and all other balances zero.
The accepted methods require the expected phase and declared date, exact selected
coupon/receipt values, nonnegative cash, payoff prerequisites and agreement
between outstanding payable and accrued-minus-paid memory. The used flag must
agree with the retained draw instructions. The wrapper checks coupon type/rate
against the declared family; event amounts cannot silently substitute another
coupon. Source and clause strings bind the synthetic premise revision, not its
truth or legal applicability. State alterations can be internally consistent
and still false; actual-source admission remains separate.

The two dates are June30 and December31,2027, within one supplied reporting
period. The amounts remain the one-period charges defined by the prior case;
this bridge does not compute accrual duration. The dated convention tests
ordering and rejects unintended dates. It is not an assertion that those dates
make each interval a year or establish a real instrument's interest schedule.

For every accepted command the verifier independently assembles the entire
signed book, memory, event identity sequence, journal and cash-flow record.
It also constructs every report line, balance-sheet total, income/expense
subtotal, gross cash-flow origin and reconciliation. A refused command leaves
the previous accepted book unchanged. The earlier independent closed-form
reference provides a further comparison after applying the reduced-equity map.
Two injective account charts test that labels are not mistaken for semantics.

The amount formulas are affine within a declared guard region. Algebra above
shows how each selected posting maps to the corresponding reduced change; an
induction over an accepted sequence gives the same mapped quantities provided
all guards, timing, memory and input premises agree. That structural argument
does not establish arbitrary typed-method equivalence or validate every region
through concrete tests. The28 witness programs exercise boundaries and failure
mechanisms, while the earlier whole-region oracle supplies its own independent
continuous proof. A general symbolic-to-common-runtime certificate is still open.

Checkpoint acceptance is distinct. Replaying a declared concrete prefix can
verify that a saved book and journal follow from that opening and registry.
It cannot turn a point execution into a proof about a continuous family, infer
source availability, establish durable storage, or give a cheap upper bound on
restore work. Those limits remain explicit in the checkpoint stage.
