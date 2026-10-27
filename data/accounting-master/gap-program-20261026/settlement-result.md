# Maturity, partial settlement and missed-payment history

26 October 2026. E01 under the reviewed gap program; MC13/15/16/17/18/24/28/33/34,
W05/W16, SIM-F024/026/028/035/036/044/062 and X02.

The common typed company executor now has a checked, supplied-contract example
that continues through a partial maturity payment, a missed-payment observation
and later settlement. Four programs use two account charts and two funding
dates. Fourteen adverse or omission cases and 179 comparisons pass. The primary
evidence is the complete independent prefix comparison, not these counts.

## Contract and independent calculation

Both paths begin with cash60, inventory100, contractual face100, debt carrying
amount80 and book equity80. The supplied promise is zero-coupon and matures on
30 June2027. A single explicit measurement interval accretes20 to interest
expense and debt on that date. There are no fees, tax, penalties, acceleration,
waiver or endogenous price. These are synthetic modeling choices; no actual
issuer or accounting treatment is admitted.

| Path and date | Cash | Debt carrying amount | Outstanding contractual claim | Overdue amount last recorded | Historical missed amount | New shares |
|---|---:|---:|---:|---:|---:|---:|
| Opening |60|80|100|0|0|0|
| Early funding,29 June |100|80|100|0|0|40|
| Early path, maturity before settlement |100|100|100|0|0|40|
| Early path, full payment30 June |0|0|0|0|0|40|
| Late path, maturity before settlement |60|100|100|0|0|0|
| Late path, partial payment30 June |0|40|40|0|0|0|
| Late path, observation1 July |0|40|40|40|40|0|
| Late funding,2 July |40|40|40|40|40|40|
| Late path, final payment3 July |0|0|0|0|40|40|

The table's debt column is a positive liability; journals use the existing
signed-credit convention. The overdue observation changes memory without a
journal or cash flow. The later payment reduces both debt and the contractual
claim by40. It does not reverse interest expense or erase the earlier missed
amount. The reported 4 July balances are identical: assets100, liabilities0,
equity100, profit−20 and financing cash flow−60. The contract histories differ.

Therefore terminal financial-statement equality does not justify merging these
paths for a query about missed payments. The current unpaid balance and the
history of failing to pay on time answer different questions. This is a local
derivation from the supplied event sequence, not a claim about a real default
definition, regulatory classification or insolvency law.

## What execution checks

`settlement_cases.py` constructs immutable CompanyBookMethod/1 definitions and
runs DeclaredCompanyProgram/2 through its unchanged typed monetary/memory
evaluator. The independent table in `expected_path` does not evaluate those
method expressions. For every event it checks the entire resulting book:
all balances, all memory including unrelated retained fields, types and schema,
period/context, exact event order and cash-flow history. It also compares every
journal and gross cash flow, report totals, replay and unchanged inputs.
Native `Engine.apply` is disabled during execution. Ten inspected predecessor
source files keep their original hashes; the evaluator verifies its own pinned
dependencies as usual.

An attempted payment beyond available cash is invalid and leaves the prior
state intact. An unknown settlement amount is unresolved. False applicability
is unsupported. Premature payment, repeated accretion, payment above the claim,
an overdue assessment on the due date, duplicate IDs and reversed settlement
chronology refuse. Removing the contractual principal reduction is caught by
the postcondition and cannot partially post. An omitted required amount fails
structural validation. Full refusal payloads and stopped commands are retained.

Two deliberate omissions still produce balanced, completed generic programs:
removing share-memory updates, or removing the historical missed-amount update.
The independent financial-state comparison rejects both. This is evidence that
generic arithmetic and structural validation cannot establish domain completeness.
It is not a previously hidden claim that the general engine already enforces
every contract invariant. The next reusable financing profile must expose those
invariants and its opening-admission obligations explicitly.

## Decision and remaining work

| Decision | Primary criterion status | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain E01 as bounded reference evidence | Independent complete prefix/state/journal/flow and report comparisons pass | No lost input, source change, unexpected fallback or unexplained mismatch | Supplied single-interval convention and synthetic rights | Add reusable source/invariant admission and compose with date-controlled funding | General maturity/default engine or accounting compliance |
| Reject memory-omitting variants | Full-state comparator detects both omissions | Domain completeness fails despite balanced journals | Wider histories and transformations | Require explicit share/claim/history invariants | Generic engine proves financial correctness |
| Keep W05/W06 open | Only the declared case is checked | Actual authority/rights and dynamic equilibrium remain unsupported | Multi-creditor, interest, grace, remedies and control | Source-specific methods and independent multi-date strategy comparison | All financing gaps closed |

The run was CPU-only, deterministic exact rational arithmetic: no statistical
ranking, stochastic uncertainty interval or performance claim applies. The
manifest records command, Python/platform, hashes, wall time, data and scope.
Artifacts: `settlement-cases.json`, `settlement-controls.json`,
`settlement-checks.json`, `settlement-source-lock.json`,
`settlement-run-manifest.json`.

Post-run red team: an observer may infer that recording a missed payment proves
legal default, or that a single terminal accretion is a general measurement
schedule. Neither follows. The supplied dates and no-penalty convention make
the local question determinate. The strongest alternative explanation for
matching reports is that the oracle checks too little; complete retained states
and two deliberately successful accounting-only mutations address that concern
within this fixture. Actual issuer facts, scalable profiles and independent
implementation acceptance remain open. No continuation veto fired.
