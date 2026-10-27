# Add identified receivables without preallocating fictitious claims

25 October 2026. S2–S4; MC02/05/08/09/11/13/15/17/23–28/34/35.
Question: can a declared credit sale atomically create one typed receivable
identity, amount and due date, then preserve that identity through partial
collection, dated assessment, reporting and period carry?

Baseline: frozen CompanyBookTransition/1 scalar replacement behavior,
MethodMemoryEffects/1 insert/append staging and DeclaredCollectionClock/1 fixed
opening claims. Exact accounting comparator: the retained operating delivery and
collect methods under the same synthetic cost/revenue premises. No source facts,
impairment or tax treatment will be inferred.

Before implementation inspect exact memory-type, schema, binding, staged-write,
registry, report and carry contracts. Record why the old fixed-leaf map cannot
describe a new claim. Compare a bounded typed-map extension with a separate
collection component; choose the smallest interface that preserves shared-state
atomicity and type checks. Do not represent a nonexistent claim as a preallocated
zero slot, loosen closed schemas globally, or copy a legacy native state into an
incompatible company context. Preserve all frozen versions and result packages.

Research intent: the mechanism is explicit identity creation with structural and
monetary checks. Expected failures are duplicate creation, mismatched customer or
currency, orphan receivable balances, hidden replacement, malformed dynamic
paths, altered due dates and loss of claims at carry. Primary acceptance is exact
independent lifecycle and journal results, original-profile compatibility, two
charts and matched authored execution. Every unsupported or unknown event must
retain its successful prefix. Balanced journals, counts and runtime are
explanatory, not general type or admission evidence.

Promotion vetoes: schema/type bypass, untracked monetary effects, loss of event
identity or history, guessed facts and changed frozen dependencies. Repair the
candidate. Continuation vetoes: corrupted inputs, unavailable required runtime
dependencies or a material design decision that cannot be resolved from the
existing contracts. No generic human-review veto on provisional internal work.

Stages: (1) bounded contract audit and default review; (2) minimal structural
successor with independent type/path/refusal tests; (3) credit sale creates a
claim, partial receipt, state-only assessment and next-period receipt; (4) exact
text/report/carry/replay checks; (5) integrate only checked behavior and refresh
complete 53/6/46 coverage. Source-backed histories, broader tax and group/sector
composition remain subsequent dependencies. No forecasting or background run.
