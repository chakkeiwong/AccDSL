# Availability uncertainty preserves alternative histories

28 October 2026. Unified T03/C04, under the audited clock-uncertainty plan.
All 950 exact checks pass. The result adds a bounded uncertainty construction;
it does not infer actual publication dates or promote source admission.

## What is established

The target is the set of feasible active-source sets at one specified cutoff,
given inclusive integer date intervals, publication no later than ingestion,
and independent feasible date rectangles across distinct sources. The code
computes each source's feasible active/inactive alternatives by restricting its
date rectangle, then takes their Cartesian product. An explicit witness date
pair accompanies each alternative. This equals direct enumeration of date
assignments in all 800 tested small interval/cutoff/view combinations.

The full insurance history is replayed at 22 public/system cutoffs. Each
availability branch retains the complete native conditional result and exact
known-witness replay. Reversing source order leaves the family unchanged.
An H=5 assertion and H=6 assertion with uncertain publication produce four
availability patterns: neither, either alone, and both. Only the both-active
pattern reports a conditional conflict. No branch is selected as the true one.

The minimum publication day and maximum ingestion day characterize whether
a restricted rectangle contains a pair with p<=i. Its witness uses the minimum
allowed publication and the larger of that day and minimum ingestion. Every
feasible exact assignment belongs to one active/inactive pattern, and every
retained pattern has such a witness. Independence of feasible clock rectangles
then makes the product complete for this declared finite source family.
This is a feasibility argument, not a probabilistic independence assumption.

The output reports sources that are definitely active, possibly active, and
each conditional branch. It preserves original bounds, source identities and
the assumed chronology. Identical duplicate records represent one uncertain
source event. Identity collisions, invalid intervals and impossible chronology
refuse; missing clocks remain unresolved. Revisions and shared/unknown clock
dependence are unsupported. A branch budget below the required family size
returns budget_exceeded without silently truncating alternatives.

## Decisions and limits

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Retain finite clock-family reference | Exact agreement with direct date enumeration and complete conditional histories | No failed checks; order, conflicts, duplicates and budgets preserved | Supplied interval/chronology/family assumptions | Bind a supported real-source availability interval or retain unknowns | Actual actor knowledge or general source admission |
| Preserve multiple information alternatives | Every feasible activity pattern remains | No probability or single-history selection | Reliability and revisions outside domain | Develop authority-specific revision semantics and joint clocks | Equal probability of branches or which source is true |

The 950 count combines 800 local feasibility checks with 150 native/negative
controls; it is not a coverage or acceptance measure. The strongest alternative
explanation for an apparent information conflict is an incorrect model domain,
mapping or chronology premise. Ingestion can precede public release for private
or embargoed data; such data violate this declared public-source chronology
and need another explicitly reviewed domain. Inter-source shared event dates
need joint constraints. The present family is per cutoff: it is not a jointly
coupled multi-date information process, and a policy must not see the branch
label unless that information is separately supplied to the actor.

No Monte Carlo sampling or stochastic ranking is performed. These rational and
finite checks establish local engineering/derivation results only. Statistical
calibration, reporting truth, causal effects, standards compliance and release
readiness remain unestablished. Expected nonidentification supports the next
source/revision task; no global continuation veto has fired.

Actual command, Python/Z3 versions, HEAD, changed-code hashes, elapsed time,
plan and result paths are retained in attempt-01/run-manifest.json. Complete
native outcomes and authored checks are in the same attempt. The older bridge,
conjunction successor, selected manuscripts and their evidence are unchanged.
