# InsuranceAssessment/1

15 October 2026. A finite documentary specification, not an executing service.
Exact canonical JSON uses sorted keys, UTF-8, no floats or duplicate keys and
reduced signed rationals with positive denominators. Record digests are SHA256
of `accdsl.portable.v1/SCHEMA_ID`, a NUL byte and canonical record bytes.
The complete direct reference set is sorted into dependencies; all transitive
dependencies and exact source/fact blobs must exist. Schemas are closed.

## Admission and mathematical target

Every basis binds context, historical source, exact evidence bytes, evidence
view, model identity, method anchor, expected accounting head and any previous
assessment. Evidence bytes equal the complete AssessmentInput body, rather
than a generic synthetic-premise label. Both availability and ingestion must
precede the view's respective cutoffs. Model fields bind group, triangle,
process law, backward law, conditioning information and horizon; unused fields
use `not_applicable`. All facts are supplied illustrative premises. Historical
EU2023 source support establishes neither current law nor actual applicability.

Transition dates use January annual starts in this finite profile. The preceding
annual start is included in the adjusted comparative list. C25 moves transition
to the earliest adjusted start. Supplied impracticability is admitted only with
documented reasonable effort. Missing evidence is unresolved; missing workbooks
alone never establish impracticability. C5/C6 and C5A determine permitted routes;
C5B applies separately to acquisition assets. Full retrospective support must
be contemporaneous; a later-created estimate with that support is not hindsight.
No route assessment performs a full or modified retrospective valuation.

C20A transition recovery requires remaining coverage, admitted recognition and
systematic allocation of covered group loss. The ordinary B119C timing check
is waived only at transition. Covered loss times expected share is a component
of a separately measured held asset; it is never an additional asset. Opening
assessments with a nonzero embedded component require a resolved matching
recovery assessment for the same transition date, an identified group and its loss. C20 is applied per
group before aggregation. Other assets less net insurance liabilities determine
opening equity; cash and current profit do not change. Tax and accumulated OCI
are uncomputed/excluded and FX is absent in these examples.

Triangle inspection supports exactly the retained three-origin, three-annual-
development upper triangle, explicit structural mask and tail factor one.
Volume factors project the no-tail point reserve. Origin/development design
rank is checked; Pearson residual dispersion uses fitted backward increments
and N minus rank. Zero dispersion is unresolved predictive evidence, not a
deterministic claims law or a risk adjustment. Larger/irregular/signed triangles
require a successor method and are refused here.

Finite predictive assessments require fit masses summing to one, normalized
conditional joint outcomes for each successful fit, nonnegative values, unique
attempt/fit IDs, consistent cell counts and each cell's conditional mean equal
to the declared fit mean. Fit dependence is shared; the supplied joint outcomes
retain any conditional dependence. Every failed fit remains with its original
mass and an explicit cause. Known mass, unresolved mass and unconditional known
mean contribution are reported. A failed attempt with positive mass withholds
the full distribution, mean, variance and tail. This is exact finite-law
arithmetic, not a resampling run or calibrated bootstrap.

Backward conditioning multiplies the explicit prior by forward conditional
probabilities and normalizes only by the observed-event mass. Without a prior
it is unidentified; zero condition mass is unresolved. Reserve error uses
matched conditioning and subtracts paid claims from both simulated and fitted
ultimate totals. One-year CDR uses opening reserve minus payments minus closing
reestimated reserve. The two-claim stop-loss method admits only claims 0/40,
marginal probability one half and attachment 60. It preserves the unweighted
parameter interval within [0,1/2]; no probability over that interval is created.

## Publication, replay and recovery

Request identity is (client_id, request_id); request digest identifies its exact
content. A submitted byte blob must equal the referenced canonical request
record. On an already-published identity, check exact request digest first:
equal content replays the same output/receipt without freshness checks; different
content is an identity conflict. A new request must pass schema, byte, source,
fact, view, model and accounting-head bindings. `require_current=false` admits
a frozen view but never bypasses expected-head equality. Output and receipt
are published together with their entire dependency closure and identity entry.
An unresolved result publishes its complete diagnostics as a partial response.

Accounting heads, balances, journals and unrelated owners are identical before
and after every assessment. Query publication has `additional_commit=false`:
it publishes query records and makes no financial commit. A replay changes
neither identity entries nor published records. Rejected requests change
nothing. Lost acknowledgement gives unknown publication knowledge. Both worlds
must remain representable: no publication followed by a first successful retry,
and complete publication followed by an exact replay. Partial receipts,
missing dependencies, changed finance or extra publication on replay are wrong.

Independent verification derives all nine calculations without importing the
fixture builder or expected results. Schema success and check counts establish
integrity only. Unknown facts, valuation, calibration, risk adjustment, current
authority, runtime durability, universal migration and human acceptance remain
separate obligations. No continuation veto is presently supported.
