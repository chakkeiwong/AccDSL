# InsuranceOrigins/1

Read-only documentary rational exchange. Frozen input-lock-v2.json protects
the plan, retained authority, canonical authored cases and predecessor prose.
attempt-01 preserves two noncanonical rational-input refusals; attempt-02 is
the successful financial attempt. The original lock/cases remain unchanged.

Top-level keys exactly: wire, operation, context, findings, data. Wire is
InsuranceOrigins/1. Context contains entity, group, currency, unit and rule;
nonempty strings, unit currency units, rule EU2023/1803-original-IFRS17.
Common findings independently admit applicable source profile, opening balances,
complete events, information view and absence of tax/FX/unrecorded cash.
Canonical reduced rational strings encode amounts; no decimal or float inputs.
Each is at most80 characters with absolute value≤10^12. Dates are ISO days.
Exact supplied findings must be Boolean; unknown is unresolved, false scope is
unsupported, contradictions reject. All refusals have report=null,posts=false,
mutations=[]; no partial report escapes.

Four operations have distinct closed shapes, fully illustrated by the canonical
authored cases and attempt-02/exchanges.json:

loss_schedule: opening_date, cash, liability, loss_component, periods, findings.
Findings admit proportional allocation, zero CSM, no new estimates, supported
claim/RA releases, all finance in profit and no investment/acquisition component.
Opening0≤K≤L,L>0. At most32 periods, strictly increasing dates and information
available by each date. A period has date, information_date, finance_expense,
claim_release, ra_release, actual_claims, coverage_end. Fixed k=K/L assigns
k×finance to K; finance remains finance expense. Claim/RA release assigns k of
each to loss reversal and the rest to revenue. Actual claim expense and payment
are separate. Finance cannot exhaust L, release cannot exceed L, cash cannot be
negative. Only the final period has coverage_end=true and both L/K must be0.
The return includes independent loss origins, rational journals, service/finance
profits and final cash/equity. No new-loss estimate change is accepted here.

recovery_change: cash, issued_claims, issued_ra, issued_loss, covered_claims,
covered_loss, quota, held_ra, held_cost_csm, held_loss_recovery,
covered_claim_decrease, findings. Findings admit timely treaty, covered loss
allocation, zero rates, no other changes, full remaining service and quota terms.
The favorable claim change cannot exceed covered loss or covered claims. Quota
lies in(0,1]. Opening R=covered_loss×quota. Issued loss reverses by the decrease;
held FCF and profit decrease by quota×decrease. R tracks that same change, while
held cost CSM stays unchanged. No second component expense is posted. Full
remaining issued and held service and actual claims/recoveries then close both
groups. The predecessor covered-loss example is a regression baseline, not a
newly claimed missing method. RA remains a separate supplied measurement.

policy_switch: date, old_policy, new_policy, terminal, years, old_current_rate,
old_allocation_rate, old_allocation_carrying, old_oci, post_change_cash,
new_allocation_rate, periods, findings. Only88b→89b or89b→88b, with1–10 exact
annual periods. Supplied findings admit direct participation at origin, actual
holding change, supported old assumptions, no remaining service/CSM/RA, frozen
assumptions, unchanged comparatives, post-change cash and underlying measurement.
The post-change snapshot is given: acquisition/disposal cash is not fabricated.
Original old_oci must equal old allocation carrying minus the frozen current
PV; old allocation must accrete exactly to the terminal payment. For new88b,
new allocation begins at the change-date liability and its supplied rate must
also reach terminal. For new89b, that field is null and actual underlying
profit determines matching insurance profit finance.

Each period has date, information_date, current_liability, asset_profit_income,
asset_oci_income, actual_holdings and findings admitting valuation, financial-
only changes and no interim cash. Under89b actual_holdings=true and underlying
profit+OCI must reconcile to the asset change; this finite case matches the
asset to the financial obligation. Under88b holdings=false and asset returns0.
Former-policy counterfactuals depend only on frozen rates/payment, never current
valuations. Reclassification expense is the change in that old OCI balance.
Current finance/OCI forms a separate origin. The return keeps period_asset_oci
separate from cumulative asset_oci. Old/new OCI and relevant asset OCI must
exhaust by settlement; gross underlying realization and liability payment close
the financial balances. This is not a general VFA fee or risk-mitigation method.

derecognize: origin_policy, accumulated_oci, cash, other_assets, liability,
transfer_cash, findings. Admit paragraph91 event, homogeneous origin, transfer
at carrying, no remaining service/CSM/RA, unchanged other assets and no pending
policy runoff. Cash payment equals liability. Under88b recycle accumulated OCI
to profit with opposite OCI adjustment; under89b do not recycle through profit.
The chosen presentation retains the89b balance in OCI, within equity. Both signs
are supported; no current-policy inference or mixed-origin shortcut is admitted.

Success is conditional_complete and report includes the operation-specific
stages/origins and closing balances. Accounting measurements, classifications,
allocation support and underlying holdings are supplied facts, not forecasts or
conclusions inferred from balance equality. General malformed-input coverage,
production integration, domain acceptance and human comprehension remain open.
