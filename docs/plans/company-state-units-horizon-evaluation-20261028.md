# Units, terminal obligations and evaluation: SIM-F061–065

28 October 2026. C04;MC05/09/10/11/12/13/14/18/25/28/33/34.
This unit tests engineering and interpretation distinctions. E3 forecasting
remains deferred; there is no real-company forecast or empirical score.

Skeptical audit: a currency transformation must rescale monetary residuals and
their normalizers together. A short-horizon cash receipt cannot erase its
contractual repayment. Matching imposed reports is reconstruction evidence,
not out-of-sample validation. Equal means do not imply equal breach probability.
Dropping failed paths conditions on successful execution, which can remove
distress mass. Keep these targets separate from actual economic admission.

F061 uses two incompatible residuals theta and theta-1, one monetary and one
dimensionless. Dollars-to-millions scales the monetary residual by10^-6. A raw
sum of squares changes the minimizer from1/2 toward1; scaling the monetary
normalizer by the same factor restores1/2. Exact square completion supplies
the independent comparator, not a trained optimizer.

F062 reuses declared_financing_methods_v1 and declared_company_program_v2.
The supplied transaction borrows20 on31 December2027 and pays principal20 plus
interest2 on31 January2028. Under explicit actual-days/365 simple interest,
rate73/62 yields2 over31 days. Split accrual at the year boundary, preserve
liability/memory through native carry, and build the next-period methods from
the actual carried opening. Two account maps and opening cash3/1 distinguish
successful repayment from genuine liquidity shortfall. Independent journals,
full reports, replay and no-debt-erasure controls determine the local verdict.
This high synthetic rate encodes a specified cost; it is not a market assumption.
The explicit event schedule supplies maturity, which must not be claimed to
have been inferred from the generic debt method or a balance-sheet total.

Setup refinement: native opening must equal period start. The31 December
opening therefore defines a one-day2027 stub, not a full-year report. The2028
report is through31 January only. Preserve both period limits explicitly.

F063 reuses hash-verified original-debt evidence: fixed and floating histories
both reproduce imposed historical interest5 but future interest differs5/7.
No forecast score follows. If source timestamps are mentioned, retain the
existing unresolved chronology rather than inventing historical availability.

F064 derives the declared uniform-alpha example C=90-2alpha analytically:
mean89, breach below89.4 probability7/10, versus equal endpoint masses with
the same mean and breach1/2. Four midpoint nodes give3/4; a node at the boundary
distinguishes strict/inclusive tests. All probabilities are supplied teaching
premises, never observations or source-derived priors.

F065 uses an explicitly supplied finite law with successful nonbreach mass.6,
successful breach mass.1 and unresolved mass.3. Exact complete enumeration
preserves the known weighted contribution, conditional-on-success mean and
unconditional breach interval[.1,.4]. If missing cash is bounded0–100, carry
that assumption into mean bounds; if no bound is supplied, no finite mean bound
is claimed. Unknown is not cash0, default or a renormalized success. A separate
finite summarizer may be used only if existing helpers do not provide this
contract; it is not a general probability service.

Primary pass: exact unit-invariant normalized target, native carried debt and
cash consequences, accurate evidence classification, correct threshold law and
retained unresolved mass. Generic balance, counts and runtime are explanatory;
they cannot promote economic correctness. Wrong target, dropped liability,
unacknowledged conditioning or invented outcome vetoes the affected candidate
and triggers repair. Corrupt protected inputs or invalid harness vetoes this
unit until repaired; candidate failure does not stop independent work.

Premortem: complete native execution can still follow a wrong supplied rate or
schedule; a correctly weighted finite example can still have unjustified
probabilities. Preserve premises, all attempts, manifests and source hashes.
Run bounded CPU-only python3 -B checks, saving complete native data compressed
under company-state-units-horizon-evaluation-20261028/attempt-01. No default,
release, real rights or broad simulator-readiness claim follows.
