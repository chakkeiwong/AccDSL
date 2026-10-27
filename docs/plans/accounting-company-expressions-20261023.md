# Typed expressions feeding the company settlement policy

23 October 2026. S3/S4; MC10/13/14/18/23–26/28; G2/6/14/15.
Current candidate remains Version 3.53, not_ready. Authored scenario families
are a separate bounded reference increment, not a general expression system.

## Question and skeptical audit

Can a company policy declare exact typed expressions instead of opaque host
functions, then produce the same explicit settlement-policy and accounting
results? Compare with the protected SettlementPolicyDraft/1: a 9/10 collection
fraction and two 1/2 installment shares. Use its existing path, policy, changed
allocations and full result. Reuse company-family paths for scenario variation.

The risk is calling a generic arithmetic evaluator a complete policy language.
This increment is a finite pure expression DAG and an explicit adapter to
fraction/share policy inputs. It does not select new event dates, discover
contracts, infer behavior or implement an endogenous company policy engine.
Core 0 and portable contracts guide exactness, types, context and dependency
checks; their debt-only checker is not the implementation baseline.

Primary pass criterion: text/typed DAGs preserve identical canonical content;
static checks reject wrong types, contexts, cycles, missing references and
unknown operations; exact evaluation matches independent small examples;
the policy adapter reproduces the protected policy, generated path and all
financial results. Unknown required values remain unresolved. An output with
the wrong type cannot be used as a dimensionless collection fraction.

Use exact rationals, Boolean values and explicit unknowns. Numeric types are
declared by dimensional exponents and an explicit context identifier. Addition
and comparison require equal dimensions and compatible contexts. Multiplication
and division combine dimensions; only a context-free dimensionless scalar may
scale a contextual quantity. No automatic currency conversion, cross-entity
aggregation, date arithmetic or implicit rounding is supported. Type checking
examines both conditional arms; evaluation selects one arm only after a known
Boolean guard. An unknown guard remains unknown, even for equal-looking arms.
This conservative choice avoids claiming symbolic equivalence.

Promotion vetoes: Boolean/numeric aliasing, noncanonical rationals, cycle
acceptance, missing references, incompatible context/unit arithmetic, division
by known zero, execution of arbitrary text, dropped unknown dependencies, wrong
policy output types, false temporal admission or changed protected files.
An unselected conditional arm may contain a valid but numerically undefined
calculation; its syntax and type still must be valid. Unknown guard is a
retained unresolved result, not false. Counts/runtime are explanatory. Missing
immutable comparator bytes is a continuation veto for dependent work. A local
implementation failure triggers repair. No predictive evidence is sought.

## Defaults and smallest checks

| Choice | Provenance / reason | Failure mode | Early diagnostic | Status |
|---|---|---|---|---|
| Finite acyclic graph | Core contract's pure expressions | Evaluation order masks a cycle or unresolved reference | Cycle, forward reference and undefined-name examples | Bounded language design |
| Exact dimensional arithmetic and explicit context | Mission numeric meaning | Cash, units and rates silently mixed | Money plus units and cross-context tests | Required distinction |
| Lazy known conditional; conservative unknown guard | Explicit decision semantics | Unknown treated as false or branch error hidden by type checking | Both-arm type tests and selected/unselected zero division | Design hypothesis |
| Same protected settlement generator | Existing exact comparator | New policy language changes accounting unnoticed | Complete policy/path/report comparison | Protected baseline |
| All inputs remain explicit assumptions | No real source/admission evidence added | Pure evaluation becomes as-of-valid forecasting | No temporal/historical/forecast flags promoted | Required scope |

Create data/accounting-master/company-expressions-20261023 with grammar,
typed schema, evaluator, matched example, adapter, adverse checks and manifest.
CPU-only deterministic smoke, then recording and read-only replay. A full suite
should remain below five minutes. Preserve any failed candidate before repair.
No network, external source claim, installation, paid review or public release.

Audit verdict: proceed with the bounded DAG and existing policy adapter.
Remaining general syntax, source maps, richer types, policy information
admission and module interfaces stay explicit. After this increment, review
company recovery dependencies and integrate settled authoring changes into a
protected manuscript successor; S6 stays held and S7 deferred.
