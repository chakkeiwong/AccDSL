# Scenario-family authoring result

23 October 2026. The corrected recorded run and read-only replay both pass
96 checks, with 311 protected files unchanged. Record/replay times are 20.310
and 19.492 seconds. A preceding 24-check smoke matched all six existing paths.

The text and typed forms retain four complete conditional paths and two partial
paths, including unknown payroll and supplier failure. All member accounting
results and report bytes match their saved standalone counterparts. Joint
queries retain full report vectors and later unexecuted years. Duplicate member
IDs, probability fields, changed openings/horizons and rehashed false reports
are rejected. An empty authored selection and two names for the same path
retain their explicit meanings without probability or feasibility claims.

The first 92-check record and replay missed a non-ASCII identity discrepancy:
the wrapper emitted literal Unicode while the existing engine escaped it.
A direct non-ASCII probe exposed different hashes for the same path. The first
sources, record, replay observations and exact discriminator are preserved in
before-unicode-canonical-repair. Matching the engine's existing convention and
adding four Unicode checks repaired this local implementation defect. Neither
version establishes accdsl.portable.v1 record identity; that remains a distinct
encoding and import contract. This finding rejects the first wrapper's identity
claim for non-ASCII inputs, not the scenario-family design.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
|---|---|---|---|---|---|
| Retain corrected bounded reference design | Exact text/typed and six standalone-result correspondence; every joint outcome retained | Opening, identity, type, forged-result, partial and protected-file checks pass | Independent implementation and wider language coverage remain incomplete | Typed expressions feeding the existing settlement policy | Complete DSL, historical reconstruction, portable/durable runtime, compliance or forecast accuracy |

The strongest alternative explanation is a defect shared with the existing
path engine. Exact correspondence establishes preservation of that comparator;
its earlier independent financial arithmetic supplies the accounting check.
No new accounting-rule validation is inferred. A changed member result, lost
partial state or further cross-layer identity mismatch would require repair.

Reproduce with CUDA_VISIBLE_DEVICES=-1 python3
data/accounting-master/company-family-20261023/verify.py, without --record.
manifest.json records the command, commit, environment, source locks and timing.
checks.json retains adverse and joint-result witnesses. The one-time corrected
recording must not be rerun. Version 3.53 stays protected and not_ready; this
increment awaits integration. S1–S5 remain partial, S6 held, S7 deferred.
No whole requirement closes and no continuation veto fired.
