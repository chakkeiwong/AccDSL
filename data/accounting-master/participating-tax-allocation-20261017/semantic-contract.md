# ParticipatingTaxEPS/1

Read-only basic EPS allocation. Historical source: June 2017 IFRS IC IAS 33
participating-equity tax decision/example, read with IAS 33.A14. Product runtime
and actual accounting recognition remain held.

The request has exactly `wire`, `operation`, `context`, `amounts`,
`benefit_location`, and `findings`; wire is `ParticipatingTaxEPS/1`, operation
`basic`. Context has exactly `entity`, `book`, `currency`, `ordinary_class`,
`participating_class`, `start`, `end_exclusive`, `information_date`,
`facts_available_on`, and `rule`. Class IDs are distinct; identifiers are
nonempty strings. Dates are canonical ISO dates with start < end <= information
date and facts_available_on <= information_date. Rule is the fixed
`IFRS-IC-2017-IAS33-participating-tax` source profile. This admits supplied facts
at the cutoff; it does not reconstruct actual historical availability.

`amounts` has exactly ten canonical rational strings: `profit_before_benefit`,
`opening_base_balance`, `participating_ratio`, `tax_rate`,
`weighted_average_ordinary`, `participating_dividend`, `ordinary_base_dividend`,
`ordinary_tax_dividend`, `actual_tax_benefit`, and `reported_profit`.
Denominator > 0; 0 <= tax_rate < 1; every other input >= 0. The ratio gives total
participating-to-ordinary base rights, not individual share counts. Actual base
dividends must follow it. Full contemporaneous distribution of the actual tax
benefit is required; tax benefit = rate * participating dividend. Reported profit
must match the stated benefit location (`profit` or `equity`). Actual base payout
cannot exceed opening base balance plus current base profit. A negative residual
after a supported prior-period payout is allowed.

The exact findings are `equity_classification`, `fixed_proportional_rights`,
`ordinary_only_tax_benefit`, `tax_deduction_supported`,
`actual_benefit_recognition_supported`, `full_actual_benefit_distributed`,
`complete_dividends`, `no_other_entitlements`, `denominator_complete`,
`base_balance_supported`, and `same_rights_on_residual_allocation`.
Every finding must be true. Null findings/amounts are unresolved; false findings
are unsupported. Malformed types, unknown fields, inconsistent amounts/dates,
wrong rule, stale retained sources or invalid denominators are rejected.
Negative base profit is unsupported because no loss-tax rule is admitted.

Success is `conditional_complete`. Return original context, adjusted profit,
signed residual, its two base allocations and tax adjustment, declared ordinary
dividend, total ordinary/participating earnings, hypothetical total EPS earnings,
closing base balance and basic EPS. `diluted` and `selected` remain null with
`selection_status=not_evaluated`; this is not a diluted-selection operation.
`trace` identifies the source's three calculation steps. `journals` and
`mutations` are always empty. Refusal returns result null and an empty trace,
so no rejected request can expose an apparently usable partial numerator.

Admission also checks the preserved source bytes against `input-lock.json`.
The method is deterministic rational reference arithmetic. It makes no
recognition entry, probability estimate, tax-law judgment or operative-law
admission. Retained tax benefits, other sharing/caps/seniority, loss cases,
changing rights and dependent dilution need separately supported methods.
