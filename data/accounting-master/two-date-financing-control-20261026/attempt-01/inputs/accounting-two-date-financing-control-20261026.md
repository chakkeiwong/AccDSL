# W06 two-date financing and control after conversion

26 October 2026. MC13/14/17/20/24/25/28/33/34; W06/W16.
Continue independently of the concurrent inference-vintage work. Preserve
Version 5.17 and all successful financing/carry/inference evidence.

## Research intent and evidence contract

Question: can an explicit finite financing decision use the control rights
actually established by a dated conversion, price the resulting creditor
payoffs, and refuse an offer that cannot settle with available owner cash?

The inherited baseline is the exact senior-40/junior-80, investment-60 example
in literature-closure-20261026/persistent-financing.py and its frozen result.
That script is a one-shot writer and must not be imported or rerun. Its
one-period policy/quote comparison does not answer the two-date control question.
The new unit is a separately labelled synthetic extension, not an empirical
financing model or production implementation.

Primary criterion: backward induction under explicit date-1 information and
current control rights must match an independent enumeration of all four
nonanticipating pure strategies and all local deviations. Use independently
authored branch-payoff tables and exact rational prices, owner contributions
and participation values. The result retains every tie, never an arbitrary
winner. Complete state/rights/payoff records must show conversion and creditor
priority; a reduced financing-accepted flag is insufficient.

Vetoes: inconsistent dated cash legs, wrong discount horizon, double-counted
converted debt, stale ownership/control, future information, invalid probability
mass, unsupported control selection, missing liquid funds or owner participation
failure. Funding/participation veto acceptance of a candidate, not continuation
of the investigation. Hash drift or disagreement between the independent
comparators invalidates the harness and requires repair. Counts/runtime are
explanatory only. No stochastic ranking, actual accounting, legal admission,
unique general equilibrium or empirical pricing validity is inferred.

## Explicit new synthetic premises

Dates are 2027-01-01 (offer and funding decision), 2028-01-01 (signal,
conditional conversion and policy choice), and 2029-01-01 (terminal cash).
The supplied gross discount factor is 21/20 per interval. A date-2 payoff
therefore has date-0 value divided by (21/20)^2; no date-1 cash payment is
invented. The probability law is a fully specified hypothetical risk-neutral
pricing law, also used for the actors' expected cash utility.

Existing senior face is 40, new convertible face 80 and investment 60.
The two date-1 signals each have probability 1/2. Under the debt signal,
the new claim remains debt and the old owner controls policy. Safe terminal
estate is 100; risky estate is 20 or 220 with equal probabilities, reusing
the old one-period cash table. Under the conversion signal, the supplied
contract extinguishes the new debt and issues 120 shares to its holder
alongside 40 existing shares: cash and vote fractions are 3/4 and 1/4.
The new majority holder controls the date-1 policy. Safe estate remains 100;
risky estate is 20 or 140 with equal probabilities.

The lower conversion-branch upside is a new counterexample hypothesis. The
old owner also receives a terminal non-cash private benefit worth four utility
units if the risky policy is chosen in that branch; it is not part of estate,
creditor recovery, a cash flow or accounting equity. It makes control
consequential: after conversion the new holder prefers safe cash 45 to risky
cash 75/2, while the old owner's utility prefers risky 33/2 to safe 15.
At private benefit zero, both prefer safe; this limiting case will be checked.
No statement about actual managerial incentives follows.

The date-0 owner can decline at outside utility zero. Available cash 20
reuses the inherited funding-failure case; cash 22 is a new boundary-side
diagnostic, not a selected financing default. Competition is represented only
by an offer equal to the declared discounted expected new-holder cash payoff.
No market-clearing, bargaining or mixed-policy solution is asserted.

## Derivation to check

The debt branch chooses risky, giving expected new-holder cash 40 and old-owner
cash 50. The conversion branch under current control chooses safe, giving
new-holder cash 45 and old-owner cash 15. Thus proceeds are
(40+45)/2 divided by (21/20)^2 = 17000/441. Required owner cash is
60−17000/441 = 9460/441. Old-owner discounted payoff is 13000/441;
net participation value is 3540/441. Cash 20 is insufficient; cash 22 is
sufficient and participation is positive.

Keeping old control after conversion instead selects the risky conversion
policy. Expected new-holder cash there is 75/2, so the price is 15500/441.
Using that policy at the correct-control quote leaves lender value short by
1500/441. The old-control quote requires owner cash 10960/441, exceeding 22.
These exact differences discriminate control/price/funding consistency,
not economic superiority of conversion.

## Skeptical/default audit and execution

The scientific question is distinct from implementing an optimizer. Since
the original owner contribution is sunk at date 1, this finite example's
continuation preferences are independent of the posted price. State this
limitation; matching enumeration is not a general fixed-point existence proof.
Private benefit, branch payoffs, probabilities, dates, conversion ratio and
outside option are explicit fixture hypotheses with the failure modes above.
Priority and cash conservation use a separately authored literal payoff table
as the first diagnostic. Minority ownership cannot be silently reused as control;
a vote tie requires a supplied governance rule or remains unsupported.

First inspect baseline hashes and record the literal model under
data/accounting-master/two-date-financing-control-20261026/. Implement a small
finite exact reference, not a production solver. Compare backward induction
with independent exhaustive strategies, funding thresholds, the zero-benefit
limit, and adverse prior/discount/rights/information controls. Preserve every
attempt and the baseline writer. Record source locks, commands/environment,
time, exact outputs, decision table, limitations and next action.

CPU only: env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 with
an explicit script path. No agents, commits, installs, GPU, outreach, fees or
publication. S1–S5 partial; S6 held; E3 forecasting deferred. No broad package
or whole requirement closes. Typed accounting conversion/control execution
remains a later composition task even if this finite decision benchmark passes.
