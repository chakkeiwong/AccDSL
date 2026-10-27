# Common typed preconditions checked against retained methods

24 October 2026. MethodRequirements/1 now supplies a reusable, closed typed
expression evaluator in scripts/method_requirements_v1.py. It validates context
and types, preserves dependency identities and unknown reasons, resolves an
immutable caller-selected manifest, and records every requirement outcome.
It does not execute accounting methods or grant source/accounting admission.

The deterministic increment passes 197 checks, including an independent suite
of 11 test methods and 35 differential cases against unchanged company-operation
and return-module functions. Eighty-eight protected inputs remain unchanged.
The tests cover explicit truth tables, exact fractions, boolean/numeric type
confusion, date validity, context mismatches, repeated unknown dependencies,
malformed definitions, changed hashes, unavailable capabilities and mutation.

One deliberately mixed case is correctly reported as a difference. With an
unknown tax rate and a known floating share of 2, CompanyOperations.validate
returns unresolved before reaching its fraction-domain check. The common
assessment returns invalid and retains the unknown finding. This follows the
new declared all-findings contract; it is not global behavioral equivalence and
does not modify the original function. Single-condition differential cases
match; full original prerequisites remain explicit residual requirements.

| Decision | Primary criterion | Veto status | Main uncertainty | Next action | Not concluded |
|---|---|---|---|---|---|
| Retain optional reference evaluator and continue authoring | Independent finite semantics and selected original conditions agree | No identity/type/context loss or authority escalation found; mixed precedence difference explicit | Full cross-profile applicability and authoring usability remain untested | Add matched text and immutable exchange through the same core | Full method eligibility, history entailment, actual-company feasibility, complete compiler or production readiness |

The strongest alternative explanation for successful comparisons is narrow
condition coverage. The manifest returns the omitted schema, source, accounting,
state, event and execution obligations, and method_eligible stays false. Empty
authority references and true caller findings cannot remove that boundary.
Unknown x=x stays unknown in this conservative evaluation; no theorem about
admissible histories or probability measure follows.

This is deterministic engineering evidence, with no stochastic ranking or
numerical-policy promotion. Counts measure checked cases, not scientific or
accounting completeness. No global continuation veto fired. S1–S5 remain
partial, S6 held and S7 deferred. Version 3.58 remains protected and not_ready;
the new reusable design has not yet been integrated into that manuscript.

Run python3 -B data/accounting-master/method-requirements-20261024/verify.py --replay.
The manifest retains the actual command, current commit, environment, timings,
input hashes, test code and outputs. The next audited plan is
docs/plans/accounting-method-requirement-authoring-20261024.md.
