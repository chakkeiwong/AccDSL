# Conversion, priority and exclusive preference rights

28 October 2026. C04/T08; SIM-F027/031/032. Attempt04 passes136 checks over12
native programs and29 solver cases. Native code and solver budgets are unchanged.
These are distinct conditional accounting and finite-rights exercises, not a
single admitted company model.

## Conversion

The synthetic opening has cash10, inventory160, debt160 and equity10. Conversion
extinguishes debt160 and its face memory, creates16 shares alongside100 old
shares, and increases equity by160 without cash flow or profit. Two account maps
give assets170, liabilities0 and equity170. New holders own16/116=4/29. Dividing
by the old100 shares is wrong for the stated post-conversion ownership target.

Duplicate conversion, inconsistent face and wrong share count refuse atomically;
an unknown count remains unresolved. A deliberate missing face-memory update
still produces balanced reports and zero book debt while retaining a contractual
face160. The independent contract-state criterion detects this error. No real
contract, basis-specific recognition or arbitrary conversion library is admitted.

## Shared collateral and nonparticipating preference

For claims40 and30 against one collateral pool50, the supplied first priority
produces recoveries40/10 or20/30. Unknown priority retains both alternatives;
there is no pro rata default or invented probability. Paying each independently
against the same50 would allocate70, an excess20, and violates the shared-pool
constraint. These are two explicit strict-rank cases, not an inferred legal
waterfall or a full universe of recovery arrangements.

For the authored nonparticipating preference60 with conversion fraction1/4,
exit values40,100,240 and400 give holder payments40,60,60 and100 respectively.
At240 both exclusive elections remain feasible because they pay the same60.
The retained choices are legally distinct assumptions despite equal scalars.
The model explicitly assumes terminal-value maximization with full terminal
knowledge; it does not model earlier information or actual investor behavior.

Paying preference and conversion together is wrong relative to the stated
nonparticipating right. At exit40 it overdraws the pool. At100,240 and400 the
combined payment can conserve the pool while still violating the exclusive
right. Thus conservation is necessary here but insufficient for correct rights.
No participating-stock conclusion is inferred from a nonparticipating fixture.

## Failed attempts and repair

Attempt01's checker assumed duplicate refusals contain transition hashes. Early
duplicate detection has no transition; exact current-state comparison to the
last successful transition or opening repairs the check. Attempt02 used arithmetic
ITE outside the native rational solver's supported fragment. The solver correctly
returned Unknown, while the checker incorrectly assumed complete coverage.
Attempt03's guarded affine equalities were supported but generated1458 sign
cells:50 were checked and1408 remained unresolved. No bound was certified; the
checker again assumed a bound existed. Original code and failure records remain.

The final representation uses exact affine interpolation over the explicit binary
domain: recoveries are40−20r and10+20r for r in{0,1}; exclusive preference payment
is P+(C−P)e for e in{0,1}. Direct substitution gives precisely the two predeclared
outcomes; no fractional election is admitted. This changes representation, not
rights or budget. The unsupported ITE is retained as a negative control, and
zero-budget tests preserve Unknown, the formula and unresolved coverage. Neither
resource exhaustion nor unsupported syntax is labeled economic default.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain SIM-F031 conversion discriminator | Full balances/memory and116-share denominator match independent expectations | Refusals atomic; stale-face negative control detected | Actual terms and accounting treatment | Bind supported contracts and broaden explicit conversion cases | Generic conversion admission |
| Retain SIM-F027 shared-pool discriminator | Exact two-rank family and one50 pool | Double-count recovery infeasible | Actual priority, collateral ownership and other claims | Supply those dependencies explicitly | Universal waterfall or inferred priority |
| Retain SIM-F032 exclusive-rights discriminator | Low/high/tie payoffs and alternatives match finite oracle | Combined rights detected even when conservation passes | Actual election rules and information | Test supplied rights rather than infer from aggregate payout | Investor behavior or general preference valuation |

| Inference status | Finding |
| --- | --- |
| Hard veto screen | Wrong state/rights detected; unsupported arithmetic and insufficient budget preserve Unknown |
| Statistically supported ranking | Not applicable: exact deterministic conditional cases |
| Descriptive-only differences |136 checks,12 native cases and29 solver calls describe the selected scope |
| Default readiness | No solver, native method-library or policy default changed |
| Next evidence needed | Actual instruments, populations, priority, elections, information and accounting admission |

Post-run red team: the binary priority and preference outcomes were authored.
Exact finite enumeration proves only their supplied meanings; it does not discover
missing claimants or rights. The weakest evidence is applicability to an actual
company. Equal payoffs cannot collapse different rights, and balanced accounts
cannot establish contract extinction. These limits remain explicit. No global
continuation veto fired; continue remaining failures, sources and ordered review.

Final verification matches all1,179 protected hashes, including997 files across
the two frozen releases. Nine program regression tests pass. Navigation verifies
29 source hashes and preserves all40 task statuses/criteria/dependencies. Original
case coverage advances to35/201, with166 outside this pass. Native implementation
hashes remain unchanged from the preceding56-test regression pass. Main reading
remains336/831, resume337; source/survey/construction and release review remain open.
