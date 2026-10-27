# P15 provenance repair v4

This bounded repair addresses the timeout follow-up recorded for P15. It does not
expand the substantive audit and does not choose an initial profile.

The active MC34 evidence previously pointed at `docs/plans/accounting-master-program.md`
with the hash of the five-retries before-image
`fe942be68cb07f2eebcf1e81bf9dda3914c3bcc75b86d473939a2827225e6b16`. The live
file now hashes to
`2fdb532a1d94fa9083cc1641dc017f622564440f9954a46b11fdd0c53fc14c5a`. The
captured current bytes are preserved at
`docs/plans/accounting-proposal/evidence-v4/master-program.md`; MC34's two
source references now use that snapshot and its current hash. The exact older
bytes remain at
`docs/plans/accounting-proposal/evidence-v4/master-program-before-retry-policy.md`
and at the protected five-retries before-image. The captured comparison records
that the changed passages concern the retry allowance and its explanation; the
MC34 traceability passages used by the assessment remain present.

`evidence-v4/capture-manifest.json` preserves byte-identical before-images of the
P15 coverage, result and progress files, hashes retained v3 records and protected
inputs, and records stable current-source capture. The only coverage assessment
change in this repair is MC34's two provenance references. MC25 and G18 remain
partial with the P07 reconciliation unchanged.

The earlier result and progress text claimed a
`p15-p07-completion-v3.json` file that does not exist. This repair identifies that
absence explicitly and records the actual v3 validation/process captures as
historical evidence. It does not create a retrospective v3 event. A new v4
completion record is written only after the v4 reports and registered checker
capture pass.

The v4 validator and reports check current paths and hashes, historical v2/v3
inputs against preserved bytes, the MC34-only scope change, retained P07
provenance, and the existing catalog/PDF/reference counts. These are integrity
and structure checks. They do not establish accounting validity, forecast
validity, architecture approval, independent implementation equivalence, human
acceptance or full P15 completion.
