# CompoundTaxRollforward/1 and CompanyTaxEPS/1

These are deterministic documentary exchange definitions, with no journal,
share or runtime writes. Canonical reduced rational strings represent all
amounts. A missing fact is distinct from zero. Unknown fields reject.

`CompoundTaxRollforward/1` takes the five rational fields `proceeds`, `liability`,
`coupon`, `period_rate`, `tax_rate`, and a closed `fiscal` record. Proceeds/par
and opening liability must be positive, coupon/rates nonnegative, liability
no greater than proceeds, and `liability*(1+period_rate)=proceeds+coupon`.
Tax rates above one are outside this finite profile, not universally invalid.
The fiscal record has rational `initial_base`, `accrued_base`,
`after_coupon_base`, `deduction`, `settlement_taxable_income`, and the seven
boolean findings declared in `reference_tax.FINDINGS`. They must expressly
support the specified par/coupon schedule and complete earnings consequences.

The result has `wire`, `status`, `reason`, `amounts`, ordered `stages`,
`journals`, and empty `mutations`. Positive results report gross/net issue
equity, initial DTL, effective interest, current/deferred expense changes and
after-tax cost. Stages are issue, accrued, coupon_paid and settled, each with
carrying amount, tax base, temporary difference and DTL. Journal values use
debit-positive signs; the standalone current-tax journal is an expense/payable
delta, not a cash refund or a standalone claim of a negative payable.
`unresolved` means a required finding/value is missing or consequence inventory
incomplete; `unsupported` means supplied fiscal findings or rate exceed this
profile; `rejected` means malformed/contradictory arithmetic or structure.
Every refused result has null amounts and empty stages/journals/mutations.

`CompanyTaxEPS/1` takes exactly `wire`, `operation=report`,
`world=conversion|redemption`, `base_packet`, `premises`, and `eps`. Its finite
company premises are the exact closed `premises.json` record; general values
accepted by the standalone tax method do not thereby extend the P5 company
import. Resolve the fixed source/input bytes, reconstruct the protected P5 base
internally, then replay the 19 dated legal-book events. Recalculate parent
current tax by adding the nondeductible discount to book pretax profit before
the inherited returns adjustment. Consolidate legal books, NCI and cash origins;
then reconstruct ordinary/potential shares daily.

The supplied EPS projection must equal the full independently replayed company
projection, including parent-attributed earnings, discount/current/deferred
consequences, dates, class, book, head and evidence view. Only then call the
existing OrderedEPS/1 selector, whose loaded JSON schema is separately pinned.
The response has `wire`, `status`, `reason`, `company`, `eps`, and empty
`mutations`. Refusals expose no company/EPS result. The early internal-base
argument was removed after the call-chain audit; it is not a request field.

The company example uses supplied accrual deduction and no additional
settlement/counterfactual tax. Missing findings are unresolved; different
principal/rights/fiscal schedules are unsupported; wrong earnings, share or
context projections reject. No hypothetical EPS shares enter actual books.
The exact fraction outputs, journals and wrong-projection refusals are in the
authored expectations and accepted second attempt. Current-law/fact truth,
early conversion, multiple periods, varying rates, losses, participating rights,
arbitrary company imports and production/runtime compatibility remain open.
