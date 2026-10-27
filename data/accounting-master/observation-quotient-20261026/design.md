# Finite observation-preserving state aggregation

26 October 2026. MC08/09/10/11/12/14/18/24/25/33/34; S2/S4.
Plan: docs/plans/accounting-observation-quotient-20261026.md.
Baseline: Version 5.4 simulation/08-compression.tex.

## Skeptical audit before implementation

The supplied plan survives with one explicit refinement: current requested
outputs are part of the retained information history, and the initial input is
a joint state/initial-observation law or relation. A state-only initial law would
lose information that can affect the first action. Scenario sequences are fixed
and explicitly supplied in these conformance cases; no scenario probabilities
are implied. Hidden-state policy keys are unsupported. The exact comparator is
an independently enumerated full observable path law/relation, never equality
of means, counts or separate marginals. The checker is a sufficient-condition
checker over all declared states, including unreachable states, and may reject
a merge that happens to preserve one selected initial path law. Such rejection
is not evidence that every weaker aggregation criterion is impossible.

No inherited numerical default becomes a scientific default. Exact rational
arithmetic follows the explicit finite rational inputs; deterministic policy
tables are a bounded conformance choice. State/action/scenario/horizon limits
are supplied scope. A finite state is assumed to contain all persistent memory
required by the supplied dynamics; this helper cannot validate that assumption
against an actual company. The declared information interface has full retained
history, with no inferred private observation. The smallest checks are a valid
duplicate-state merge, signal-dependent second action, and a joint-dependence
counterexample whose separate marginals coincide.

## Supplied model and information

At dates t=0,...,H let X_t be an explicitly enumerated finite state set. Each
state x has a current requested output c_t(x) and permitted action set A_t(x).
At H the permitted action set is empty. Scenario controls belong to a finite
declared set S. At each earlier date, every (x,a,s) has a complete finite kernel
K_t(x',o,y | x,a,s), or an unweighted relation R_t(x,a,s). Outcomes jointly name
successor state, next observation and immediate requested output. Requested
outputs and observations are exact JSON values: integers, strings, booleans,
null, arrays or objects; floating point values are refused. Probability masses
are positive exact rational strings, and each complete kernel sums to one.
Relations have no probability field; their multiplicity has no meaning.

Initial entries jointly specify x_0 and o_0, with exact masses or no weights.
The retained initial history is h_0=(o_0,c_0(x_0)). After a decision a_t and an
outcome it becomes h_{t+1}=(h_t,a_t,o_{t+1},y_{t+1},c_{t+1}(x_{t+1})).
The action table is keyed only by this observable history. A policy must define
an action at every reached nonterminal history and that action must be permitted
in every reached hidden state sharing the history. Missing entries or invalid
actions refuse evaluation; they are not implicit waits. All scenarios in these
fixtures are supplied fixed sequences of length H.

## Proposed quotient and finite induction

A supplied partition phi_t maps every x in X_t to one named block. For x_1,x_2
in the same block require A_t(x_1)=A_t(x_2) and c_t(x_1)=c_t(x_2). For every
permitted action and every scenario require equality of the joint pushforward:

Q_t(b,o,y | x,a,s) = sum over x' with phi_{t+1}(x')=b of K_t(x',o,y | x,a,s).

In relation mode Q_t is the set of (phi_{t+1}(x'),o,y) triples; no count becomes
a weight. The quotient's action/output and kernel/relation are thus independent
of the representative. Its initial joint law is the pushforward of (x_0,o_0).
The next current output is determined by the successor block, so the joint
condition also preserves its dependence on the observation and immediate output.

Proof for rational laws: at H no decision remains and blockwise current-output
equality supplies equal terminal records. Suppose that for every retained
history, continuation laws from any two members of a date-(t+1) block equal the
quotient continuation law. A fixed observation-adapted policy selects the same
action at date t for equal histories. Equal action sets make it valid in either
state. Equal Q_t assigns the same mass to each successor block, observation and
immediate output. The successor block supplies the same next current output.
Multiply each mass by the continuation law at the correspondingly extended
history and sum over the finite triples. Termwise equality proves equal
remaining path laws at t. Finally sum against the mapped initial joint law.
This proves the full observable path law for every admissible deterministic
history policy and supplied scenario sequence. A common randomized history
policy follows by another finite sum over its explicitly supplied action law;
the helper's enumerator tests deterministic tables only.

For relations replace products and sums by compatible concatenation and union.
Every quotient step can be lifted from each member of its source block because
their pushed-forward successor relations coincide. Induction therefore both
preserves and reflects complete observable paths. Memoryless recombination of
separate date-wise output sets lacks this lifting property: persistent types
with paths (5,5) and (7,7) must not acquire (5,7) or (7,5).

## Failure, resource and reuse semantics

Malformed models, missing kernels, invalid mass, partition coverage failure or
unsupported information are invalid inputs. A valid model failing an equality
returns rejected with date/block/states and the unequal component. Rejection
means this sufficient condition fails, not impossibility of every aggregation.
A comparison budget counts explicit state/action/output/joint-kernel obligations.
Exhaustion returns unknown and every unfinished obligation identifier, with no
quotient. Validation is a prerequisite; budget zero does not hide malformed
inputs. This is not a streaming or production resource guarantee.

Accepted certificates bind exact model bytes after canonical JSON encoding,
partition, information, requested outputs and horizon. The certificate stores
the complete quotient. Reuse verifies these hashes and recomputes the condition
and quotient; a hash alone is not trusted approval. Model, information, outputs,
partition, horizon or certificate edits refuse stale reuse. Source provenance
remains separate from semantic identity.

## Evidence roles and stop conditions

Full path equality on accepted fixtures and precise adverse refusals are the
primary finite engineering checks. Hidden weights, accepted lost dependence,
invalid input silently normalized, stale certificate reuse or exactness after
budget exhaustion veto the checker. A failure triggers a repair with retained
evidence; no candidate failure rejects simulator research as a direction.
Counts and wall time are explanatory only. Preservation hashes cover the
baseline chapter and existing uncertainty result; their alteration is a
continuation veto. Deterministic exact cases do not support a stochastic ranking.
No source/accounting admission, production readiness, minimal-state algorithm,
real signal calibration, whole-company state sufficiency or forecast accuracy
is concluded. Results go in checks.json, cases.json, path-comparisons.json,
controls.json, result.md and run-manifest.json.
