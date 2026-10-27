# Pre-execution audit — two-date financing control

26 October 2026. MC13/14/17/20/24/25/28/33/34; W06/W16.

The saved plan passes after the following operational clarifications. The
question is whether dated conversion rights, continuation choices, lender
value and owner funding agree in the declared finite example. The primary
criterion is exact agreement between backward induction and an independent
literal-payoff enumeration of all four strategies and their local deviations.
Assertion counts and run time are explanatory only. Neither method is an
empirical model, a production solver or a proof of general equilibrium.

The one-period baseline is inspected, not imported or rerun. Its writer hash
is e387ac1cfa2d9bbe4282a7e561890ee2c4c3b58cd05bc2c63eba4d448d0efa82; its frozen
result hash is cd1adb9be85da66cdec5e9d0d1811e4df79786240415c40e2a73bf9db26af2e2.
These establish provenance, not a two-date comparison. Literal terminal
cash allocations are independently authored before candidate code. All
cash/utility values use exact fractions. Dates mark discrete intervals; no
day-count convention or intervening cash leg is inferred.

## Assumptions and earliest discriminators

| Choice and provenance | Justification/status | Failure mode | Earliest diagnostic |
| --- | --- | --- | --- |
| Senior40, new face80, investment60; inherited fixture | Baseline only | Mistake old one-period price for new price | Two discount intervals and literal branch recoveries |
| Equal positive signal and risk probabilities; saved plan | Hypothetical pricing/utility law | Unstated real-world inference or invalid mass | Reject negative/zero branch mass and sums other than one |
| 21/20 each interval; inherited rate extended by plan | Synthetic hypothesis | Wrong horizon or discounting private benefit inconsistently | Price17000/441; terminal utility and cash use the same horizon |
| Conversion extinguishes80 and issues120 against40 old shares | Supplied contract hypothesis | Double debt/equity recovery or stale control | Full dated claims/shares/votes and terminal cash table |
| Lower conversion risky upside140 and noncash private benefit4 | Counterexample hypothesis | Count utility as cash or attribute actual behavior | Cash conservation; private-benefit zero limit |
| Majority votes determine controller | Explicit selected governance rule | Arbitrary tie or minority selection | No majority is unresolved unless a named tie controller is supplied |
| Cash20 and diagnostic22; outside utility0 | Baseline and boundary diagnostic | Confuse positive value with available funds | Exact threshold, below/at/above threshold, participation rejection |
| Signal observed at date1, terminal realization at date2 | Nonanticipating finite strategy space | Select policy after observing its own payoff | Reject leaf-conditioned strategies or future-known inputs |
| Contribution sunk at date1; no policy commitment | Declared scope | Claim a general price-policy fixed point | Quote cannot enter date1 payoff rankings |

## Risks, stop conditions and disposition

Wrong baseline, unfair information sets, proxy promotion, hidden defaults and
environment mismatch were inspected. No stochastic comparison or external
source claim is used. A baseline hash change or candidate/oracle disagreement
invalidates this attempt and triggers a localized repair. Liquidity and
participation failures reject an offer, not this research direction. Correct
outputs must preserve all ties; unsupported governance remains unresolved.

Bounded budget: at most three one-shot numbered attempts, under five minutes
total CPU runtime. Preserve failed attempts and refuse existing output paths.
Use standard-library Python only with CUDA_VISIBLE_DEVICES=-1 and
PYTHONDONTWRITEBYTECODE=1. No installs, agents, commits, GPU or external actions.
The run manifest records the actual command, Python version, hashes, wall
time, inputs, plan, result path and Git revision. Inspection finds a usable
Git checkout on main at 03fea070f089821f4759e49a4466a3399b7fc078; the older
unusable-marker note is stale. Many unrelated tracked changes exist and are
preserved; no commit is made.

The governing manuscript remains Version5.17. Successful carry /3 compatibility
has 406 checks and is a companion pending integration. Concurrent inference
work is preserved. S1–S5 partial, S6 held, E3 deferred; no whole requirement
or broad package closes.
