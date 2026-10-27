# Sector evidence revisions: composed specification traces

14 October2026. P17-08/10/11; MC02/04–07/09–14/18–20/24–28/32–35.
This supplement instantiates evidencev3, timev2, H5, persistencev1 and interfacev1
with the existing bank commitment and connected insurance cases. It adds no
runtime endpoint and changes no common OperationRequest schema.

## Composition and preserved ownership

The local trace format is SectorRevisionTrace/v1. A trace has identity,
operation kind, query time/layer/selection, candidate view, frozen-result or
dependency-graph reference where applicable, exact book snapshot and an
expected result. It composes the already proposed operations:

| Local trace action | Existing operation and responsibility |
|---|---|
| select_and_assess | time.select@1 then accounting.assess@1; temporal admission does not itself grant accounting authority |
| current_use | history.query@1/report.build@1 dependency checks; current-view use must match complete semantic ancestry |
| frozen_explain | record.explain@1; always use output's frozen view, with current stale warning separately |
| correction_request | accounting.assess@1; missing correction treatment gives TREATMENT_UNSUPPORTED and no proposed/committed journal |
| replay_existing | exact prior accounting.commit@1 request/receipt from the pinned2.88 complete portable exchange |
| changed_retry | pinned2.88 changed-request-ID conflict; a retry must preserve original request bytes |

The fixture embeds the previously checked insurance replay's complete committed
world and retains a hash lock to its request, result and receipt package. The
two replay cases consume the prior complete portable requests/results; the other
traces are semantic compositions, not new portable operation encodings. Runtime
implementation and general schema/API conformance remain separate obligations.

Every read/assessment produces not_committed and no additional commit. A current
model projection can differ from the book's frozen calculation without changing
that book. A known current error requires a separate correction work item; it
does not justify replacing the prior immutable receipt. A valid historical retry
checks its original bindings/admission before lookup, not fresh accounting under
today's evidence. Corrupt historical dependencies still reject before lookup.

## Concrete finite assumptions and failure boundaries

All new evidence text, timestamps, reviewers and byte-link receipts are authored
fixtures, conspicuously marked as synthetic. They establish no real historical
availability or factual truth. The underlying accounting methods and conditional
quantities remain pinned to the inspected prior cases.

Bank: irrevocable commitment and draw occur in ordered moments on1January2024.
The supplied probability tree, separately supported SICR finding, classification,
valuation and method remain fixed. The restored baseline identifies original
commitment risk, not draw-date risk. Missing original baseline returns unresolved;
restoration makes the supplied SICR comparison admissible and retains funded
allowance4/equity16. No rule infers SICR by merely doubling a probability.
The later documentation can support reconstruction at its information cutoff,
not a policy decision before its public availability.

Insurance: timely treaty R precedes B's recognition and gives initial asset85,
equity85 and year-one equity83. Later treaty R follows recognition and gives
initial asset70, equity70 and year-one equity74.75. These are mutually exclusive
conditional histories from the retained case. Neither changes ultimate cash88.3
on the supplied unchanged claim path. Unknown order leaves these amounts
unresolved rather than assuming timely eligibility.

Publication, verified byte vintage, system ingestion and accepted review are
separate checks. Investor admission permits later ingestion but requires exact
public-byte linkage at its cutoff; system-as-of requires actual ingestion and,
for accepted layers, review visibility by its own cutoff. Raw system access
does not return an accounting amount. A known later revision is excluded before
supersession, preserving the earlier eligible assertion. An unknown relevant
competitor remains an unresolved obligation even when an older assertion is
selected. IDs never break conflicts.

A corrected extraction has the same source bytes and a new reading/review.
The deliberately wrong old reading is retained only to reproduce the historical
error. A later issuer correction has new source bytes and a supported scoped
supersession edge. Neither change automatically becomes a retrospective
accounting correction.

Dependency manifests include the candidate-set membership revision even if the
chosen assertion is unchanged. Changing membership stales the existing selector,
interpretation, measurement and result. A fresh selector may exclude the new
candidate on time grounds and reproduce the same quantity under a new manifest.
New descendants check ancestors; they cannot bypass a completed invalidation
scan. An unrelated dependency closure remains reusable only if every recorded
dependency version still matches. Cycles, absent targets and incomplete closure
reject or leave reuse unestablished; an unchanged displayed amount is no proof.

The independent verifier must derive temporal admission from timestamps, perform
eligible-graph supersession, traverse every ancestor and reproduce the bank/
insurance amounts from fixed formulas. Expected results are separately authored.
All read-only traces preserve the embedded committed world byte-for-byte.
Counts and hashes are engineering evidence only. No current accounting
correction authority, runtime durability or actual historical truth is claimed.
