# InsuranceRetrospective/1

Read-only deterministic documentary exchange; report only. Closed top-level
keys: wire, operation, context, route, dates, cash_history, measurement,
acquisition, history, modified, treaty, prior_basis, findings. Exact examples
and outputs are protected in authored-cases.json and attempt-01/exchanges.json.
The input lock binds the plan, historical EU authority and predecessor text.
Canonical reduced rational strings, at most80 characters and absolute value
10^12, encode amounts. Missing values remain unresolved. All refusals have
report=null,posts=false,mutations=[]; no partial financial state is published.

Context contains nonempty entity,group,currency,unit,rule; unit currency units
and rule EU2023/1803-original-IFRS17. Routes are full or modified. Dates are
acquisition_payment≤recognition, transition at its first anniversary and
initial_application at the next anniversary. No publication-date claim follows.

Common findings independently admit nonparticipating scope, grouping, complete
cash including expired contracts, supported zero rates, no tax/FX/OCI, equal
service units, unchanged remaining expectations, no incurred unpaid claims,
prior-basis balances and unchanged transition cash. These do not establish
actual evidence. False scope findings are unsupported; unknown unresolved.

Cash_history contains capital,premium_received,acquisition_paid,claims_paid,
reinsurance_premium_paid,recoveries_received, all nonnegative. The actual cash
identity retains each origin. Measurement contains remaining_claims,remaining_ra,
rate,coverage_units_past,coverage_units_remaining; rate0, units1/2 and positive
remaining claims define this finite profile. Nonzero rates refuse, not default0.

Acquisition has allocation_mode,recognized_group,future_group,findings. Supported
allocation requires both amounts to sum to known paid cash and findings for
allocation, recoverability and the same post-transition allocation method.
C14D_nil is modified-only: both unknown allocations are null, findings explicitly
admit missing C14B information and C14D applicability, and the prescribed
measurement adjustment/asset become0 while cash paid remains unchanged.

Full history has initial_claims,initial_ra,expected_past_claim_release,
expected_past_ra_release,information_date,findings. Findings admit contemporaneous
information, no hindsight and practicability. Information is no later than
recognition. Initial less expected past release equals remaining measurement;
the finite population has equal expected releases over three periods. Actual
claim experience can differ without changing future expectations or CSM.
The modified field must be null.

Modified route has history=null. Its modified record contains modifications,
similar_contract_past_ra_release,information_date,findings. The exact list is
C12,C14,C15b and C14B or C14D according to acquisition mode. Findings admit
impracticability, supportable modified information, unavailable history for each
specified modification, acquisition modification, similar-contract RA evidence
and maximum use of available historical information. Information is available
by transition. Initial expected claims=remaining claims+known claims paid;
initial RA=remaining RA+supported similar-contract past release. No general
replacement of old assumptions with current assumptions is authorized.

Initial margin=premium−initial expected claims−initial RA−recognized acquisition.
CSM=max(margin,0),loss=max(−margin,0). Transition CSM=2/3×initial CSM. The
supplied systematic loss allocation retains initial loss×remaining FCF/initial
FCF. Issued liability=FCF+CSM; the loss component is within that amount.

Optional treaty has quota,initial_ra,remaining_ra,recovery_mode,information_date,
findings. Admit timely treaty, all claims covered, quota terms, separate RA,
ordinary held measurement and matching service pattern. Initial/remaining held
RA follow the supplied2/3 service pattern; actual recovery=quota×claims paid.
Full historical treaty information predates recognition; modified information
is available by transition. Ordinary initial cost CSM=premium paid−initial
expected recovery−initial RA must be nonnegative in this finite cost profile.
Remaining ordinary cost CSM is2/3. Supported recovery mode additionally requires
supported loss recovery and gives transition loss×quota; C16C_none additionally
requires unavailable C16A information and C16C applicability, and is modified-
only. Held CSM adds that identified recovery to ordinary remaining CSM; held
asset adds FCF. Missing ordinary valuation never becomes0 under C16C.

Prior_basis has liability,acquisition_asset,held_asset. Transition equity and
prior equity use the same actual cash. The difference is independently
old_liability−new_liability+new_acquisition−old_acquisition+new_held−old_held.
Transition journals balance, with no cash entry. No treaty permits unexplained
treaty cash. Full no-treaty history additionally reconciles initial loss,
expected service releases, actual claims and CSM revenue to final equity.

Success returns conditional_complete, source origins, initial and transition
measurements, held components, equity bridge, zero transition cash flow and
proposed journals. It is not a posting engine. General discounting, acquired
incurred claims, VFA, interim estimate elections, OCI, losses with changing
estimates, partial coverage, and arbitrary service patterns remain separate.
