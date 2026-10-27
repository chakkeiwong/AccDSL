# Derive state dependencies from native accounting operations

28 October 2026. Unified T01/T03/C04; MC08/09/10/11/13/18/19/20/28/33.
Continues the reviewed recovery program using the existing complete typed
insurance history. The actual Apple measurement adapter remains separate.

## Skeptical audit and intent

The construction specification calls for operation dependency closure but does
not yet compute it from a native history. A fresh registry of invented operation
dependencies would risk drifting from the executable contracts. Derive the
closure directly from TypedAffineHistory/1 instead: event incidence, accounting
memory, snapshots, measurements and per-state constraints already declare reads
and writes in an exact affine fragment.

Question: which opening values and event amounts determine each requested
snapshot quantity, and which additional inputs remain necessary to check the
declared history's feasibility? Comparator: full native replay of the existing
independently supplied histories and hand-derived dependency sets.

Material risk: a quantity may cancel algebraically while its event or earlier
cash path still affects feasibility. Keep output dependencies and constraint
dependencies separate. Retain every domain, original definition, obligation
and excluded mechanism; never delete native variables or claim state reduction.
Generic operating preconditions are not in this native profile. The result
must continue to say operational_preconditions_checked=false.

Audit verdict: proceed with an audit-only symbolic adapter, not a new company
simulator. No forecast, policy action, standards admission or default changes.
Unknown queries are unsupported, not zero. A reported Apple measurement is not
an eligible native history and cannot silently become a legal opening.

## Evidence contract

Primary criterion: exact sparse affine forms evaluate to every requested native
snapshot under both independently retained complete witnesses. Opening and
same-day event order, account and memory roles, all constraints at all event
prefixes, and original domains/obligations remain explicit. Hand-derived cash,
held-claims and component-memory dependencies agree with the algorithm.

Vetoes: mismatch with full native replay, lost intermediate constraint, hidden
scope expansion, wrong source/profile identity, erased unknown or mutation of
retained inputs. Failure triggers a preserved-attempt repair, not rejection of
company-state construction. Counts and runtime are explanatory only.

Assumption audit: affine additive incidence is the existing profile's reviewed
scope, not a universal model of firms; inspect the exact native validator before
lowering. Finite event order and dates come from the retained synthetic family;
the first diagnostic compares before/opening and each date's final prefix.
The existing native CPU budget is a convenience bound; exceeding it must not
be interpreted as economic infeasibility. No stochastic ranking is planned.

Premortem: correct output formulas could conceal invalid intermediate cash or
unsupported nonlinear controls. Preserve per-prefix constraint formulas and
global domain obligations, and return no executable reduced program. A constant
zero aggregate does not prove that its underlying transactions can be removed.

## Execution and artifacts

Implement under data/accounting-master/company-state-operation-dependencies-20261028/.
Use native validate_and_lower before analysis. Generate full scalar dependency
records for opening/accounts/memory, event effects, snapshot queries, declared
measurements, balance and state constraints. Retain exact source/profile hash.
Check native witnesses, missing/foreign/incorrect queries, cancellation, unseen
fields, observation-only inputs, input immutability and exact all-prefix coverage.

Command: python3 -B .../check_dependencies.py --output .../attempt-01.
Preserve fresh full outputs, exact comparisons, manifest, source hashes, command,
commit, CPU-only environment, elapsed time and result decision note. Then update
the live master without closing general industry/basis composition or release.
