# P03 bounded source lowering result

PASS: 11 unittest methods executed 101 of
101 catalogued obligations. This is deterministic
Core0.1 engineering evidence; G2, G12 and G15 remain open beyond this profile.

Source programs pass through parsing, name binding, package/type/context checks
and shared IR construction. Independently authored typed declarations enter the
same semantic stages. The independent validator checks the resulting IR. Both
entrypoints preserve package locks, source context, assumptions and alternatives.
The executed checks cover renamed programs, changed principal and stress rates,
let arithmetic, formatting, unsupported operations and schema-valid corruptions.
The compiler does not read authored expected IR to produce its results.

The generated expressions give the following exact one-year interest amounts in
USD at fixed-fraction endpoints 1 and 0. These arithmetic diagnostics are separate
from accounting execution and empirical forecasting.

| Input | Expected interest | Observed interest |
| --- | --- | --- |
| borrowing_crlf_comment | 5, 7 | 5, 7 |
| decimal_spelling | 5, 7 | 5, 7 |
| borrowing_baseline | 5, 7 | 5, 7 |
| borrowing_stress_09 | 5, 9 | 5, 9 |
| borrowing_principal_200 | 10, 14 | 10, 14 |
| renamed_independent | 15/2, 12 | 15/2, 12 |
| borrowing_let_arithmetic | 5, 7 | 5, 7 |

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| PASS for bounded engineering conformance | frontend agreement, input sensitivity and semantic rejection jointly tested | missing=0; uncatalogued=0; duplicate=0; failed observations=0; test failures/errors=0; skips=0; protected inputs passed=True; changed check inputs=0 | language breadth and shared-implementation bugs | independent result review if PASS; focused repair if FAIL | full G2/G12/G15 closure, accounting validity, forecast validity or human acceptance |

Protection uses the durable historical inventory `data/accounting-master/runs/20261002T181809-4cb566e0/P03/phase-entry-inventory.json` and current
supervisor execution inventory `data/accounting-master/runs/20261002T221346-d54a6552/P03/execution-0/pre-edit-files.json`. There are
8 historical differences predating this execution, attributed by
those two records rather than ignored or treated as new worker edits. Missing
inventory evidence, absent protected paths, changes since execution entry or
changes during the check prevent a pass. No temporary snapshot is required.
Conformance JSON preserves the inventory hashes, per-file baselines, actual IR,
bindings, source maps, input hashes, diagnostics and the complete unittest output.

Specification is recorded in the versioned profile. The two versioned modules
implement the declared slice; the catalog enumerates tested invariants. Accounting
validity and empirical forecast validity are not established; human acceptance is
pending. History families remain Unknown/PartialSearch, with zero completed cells,
one unsearched cell and no invented witnesses or solver results. MC02/MC04/MC10/
MC20/MC23/MC24 receive bounded evidence, while all MC01–MC35 and G1–G18 retain wider
obligations.

The strongest alternative explanation for frontend agreement is a shared compiler
bug. Independent arithmetic, comparison with corresponding authored IR fields and
schema-valid corruptions constrain that explanation without proving the general
language. An in-profile counterexample would overturn this engineering result.
No stochastic ranking, performance comparison or authoring superiority is claimed.

Actual command: `python3 -B scripts/check_accounting_p03.py --output-dir data/accounting-master/deliverables/P03`. Approved plan:
`data/accounting-master/runs/20261002T221346-d54a6552/P03/approved-plan.json`. Environment: Python 3.11.15, Lark
1.3.1, jsonschema 4.26.0; CPU only, no accelerator
framework imported. Check wall time: 2.615 seconds.
Git commit unavailable; content hashes provide file provenance. Changed phase
files and this execution's source changes are enumerated in the manifest. The
standalone unittest outcome and final integrity inspection are in progress.md.

Residuals: general package loading and overrides, events, rules, postings, journals and runtime execution, records, arrays, field selection and finite choices, multiple books/entities/observations, other currencies and calendars, cross-company mappings and broader uncertainty categories, reconstruction, feasibility proof, accounting validity and forecast validity. General language support, arbitrary
and cross-company mappings, broader uncertainty, reconstruction, accounting
execution and human acceptance require separate evidence.
