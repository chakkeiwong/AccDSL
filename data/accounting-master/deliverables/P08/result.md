# P08 authority and corporate methods result

The bounded P08 implementation covers an Australian for-profit Tier 1 issuer
compound convertible bond under the retained 31 December 2022 AASB
compilations. It recognises the issue, separates the liability and residual
conversion equity, accrues effective interest, pays two annual coupons, and
settles at maturity by either cash redemption or fixed-share conversion. Exact
`Fraction` arithmetic, atomic state transitions, journal balancing, and note
roll-forwards are implemented in [corporate_financing_v1.py](../../../../scripts/corporate_financing_v1.py).

## Supported operation

The supported contract is synthetic and deliberately narrow. The issuer is a
party to the contract at issue; proceeds equal whole-instrument fair value; the
conversion right exchanges a fixed number of ordinary shares for a fixed cash
amount; the instrument is non-puttable and convertible only at maturity; the
functional and presentation currencies are AUD; and the ordinary liability is
measured at amortised cost. Issue dates are 1 January, coupons are 31 December,
and all rates and amounts are exact rational inputs. Fees, taxes, derivatives,
options, early repurchase, modification, default, foreign currency, and
consolidation are rejected before state mutation.

At issue, the engine debits cash for proceeds, credits the liability for the
present value of coupons and principal at the supplied comparable
non-convertible yield, and credits residual conversion equity. Each period
credits the liability and debits interest expense at the opening carrying amount
times the exact effective yield, then debits the liability and credits cash for
the coupon. Cash redemption debits the liability and credits cash. Maturity
conversion debits the liability and credits share equity for principal, increases
the issued-share count, and leaves the original conversion equity within equity.
The sign convention is `postings_debit_positive`; every journal and total state
must sum to zero. Selected carrying-amount and effective-interest note rows link
to `note_carrying`, `measurement`, `note_interest`, and `interest` in the
authority register. They are not a complete financial-instrument disclosure.

The default two-period case has principal and proceeds 100, coupon 5, and
comparable yield 10%. The independent present-value calculation gives initial
liability `11050/121` and residual conversion equity `1050/121`. Total effective
interest is `2260/121`. After coupons, redemption leaves cash 10; conversion
leaves cash 110 and issues ten shares. A second case with principal 240,
proceeds 245, coupon 12, yield `2/25`, and 24 shares is also parameterised and
reconciled. The full dated journals, state snapshots, notes, and formulas are in
[authority-and-methods.json](authority-and-methods.json).

## Authority and jurisdiction limits

[authority-and-methods.json](authority-and-methods.json) links every claimed
paragraph to retained bytes and a SHA-256 hash in
`docs/design/research/p08-v1/authority-register.json`. The inspected sources
are AASB 132 paragraphs 22, 22A, 25–27, 28–32, 35, and AG30–AG35; AASB 9
paragraphs 3.1.1, 3.3.1–3.3.3, 4.2.1, 5.1.1, and the Appendix A definitions
of amortised cost and effective interest; and AASB 7 paragraphs 7, 8(g), and
20(b). Their common compilation applies to annual periods beginning on or after
2023-01-01 and before 2026-07-01. The register records the jurisdiction,
for-profit entity scope, Tier 1 basis, retrieval paths, inspected page anchors,
quotes, and transition limits. The source register is the authority boundary;
the implementation does not turn Australian adoption into universal IFRS
authority.

The attempted primary routes for US GAAP (ASC 470/815 and ASU 2020-06), ASBE
(CAS 22/37), and EU-endorsed IFRS (IAS 32/IFRS 9) remain unavailable or
uninspected. The recorded FASB 403, Ministry of Finance 502, and empty
EUR-Lex 202 responses are preserved in `source_access` and `access_blocks`.
The same economic facts are carried into four comparison rows, but only the AASB
row has amounts and claims. The other rows remain null and unresolved. No
company disclosure or unofficial reproduction is used as a substitute, so no
cross-standard numerical difference or equivalence is claimed.

The retained ACTUS technical specification was inspected only for dated events,
state variables, and payoff functions. Integration is deferred; no ACTUS
algorithm, official code equivalence, behavioural parameter, or forecast claim
is adopted.

This engineering result does not establish professional accounting validity,
empirical forecast validity, or human acceptance.

## Decision table

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Implement the bounded AASB issuer slice; leave the cross-standard comparison criterion incomplete | Inspected source anchors plus independent PV, cash-flow, journal, state, note, rejection, and matched-fact checks | Source hash/anchor failure, period or jurisdiction mismatch, unsupported term, chronology error, imbalance, negative funding, or note roll-forward mismatch | Synthetic eligibility, comparable yield, exact annual timing, and lack of a second inspected applicable standard | Obtain legitimate primary ASC/ASBE/EU text or keep those cells unresolved; extend the six queued methods with their own authority and cases | Professional accounting validity, empirical forecast validity, production readiness, human acceptance, superiority, and whole MC01–MC35/G1–G18 closure |

## Inference status

| Evidence class | Status | Interpretation |
| --- | --- | --- |
| Hard veto screen | Pass for the declared AASB engineering slice | The 12 unit tests and deterministic checker exercise source admission, invariants, failure atomicity, exact cases, and unresolved comparison handling. |
| Statistically supported ranking | Not applicable | This is not a stochastic comparison or forecast experiment. |
| Descriptive-only differences | None claimed | No second inspected standard supports a numerical difference or equivalence. |
| Default readiness | Not ready | Synthetic assumptions and a single inspected jurisdiction cannot establish a production accounting default. |
| Next evidence needed | Primary US GAAP, ASBE, and EU-endorsed texts; real contract eligibility and market-yield evidence; independent human review | These are required before extending or promoting the method. |

## Remaining corporate-method queue

Revenue, tax, leases, FX, and complex groups remain specific follow-up entries
with an operation boundary, missing authority, unresolved interpretation, exact
next case, and MC/G links in the deliverable. The bond queue covers early
repurchase, inducement, modification, default, embedded terms, and complete
disclosures. No professional engagement, paid data, outreach, or publication
was used.

## Verification and manifest

The required command is `python3 -B scripts/check_accounting_p08.py --check`,
with the focused suite also runnable as
`python3 -B -m unittest discover -s tests -p 'test_accounting_p08.py' -v`.
The checker independently recomputes present values and cash flows for both
settlements and the second parameter set; it does not import expected values
from the tests or report. The final checker run passed: authority admission found 3 retained primary
sources and 12 linked claims; all 12 focused tests passed; 3 independent
present-value/cash-flow oracles passed; the matched comparison preserved four
rows with three unresolved cells; and both declared deliverables passed schema
and text checks. The retained unit-test output is in
`docs/design/research/p08-v1/unittest-output.txt`. The run uses the Python
standard library, exact deterministic fixtures, and no accelerator framework.
Git provenance is unavailable because the existing marker is not a usable Git
repository; content hashes and source paths are recorded in the JSON manifest.

Changed phase files are `scripts/corporate_financing_v1.py`,
`scripts/check_accounting_p08.py`, `tests/test_accounting_p08.py`,
`data/accounting-master/deliverables/P08/progress.md`,
`data/accounting-master/deliverables/P08/authority-and-methods.json`, and
`data/accounting-master/deliverables/P08/result.md`; retained P08 source records
under `docs/design/research/p08-v1/` are listed with hashes in the deliverable.
