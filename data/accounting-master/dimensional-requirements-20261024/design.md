# Dimensional products for finite method requirements

MethodRequirements/2 adds explicit dimensional rational types and multiplication
while retaining v1 consequences, identities, separate known/unknown bindings and
no-admission results. The v1 core, frontend and binder are protected and unchanged.
The v2 type is kind=rational, context, dimensions and scale. Other kinds retain
the v1 shape. A dimensional map gives named bases integer exponents; absent
bases have exponent zero, and explicit zero exponents are rejected. A scale is
a positive reduced rational relative to those bases. A supplied numeric value
is the coefficient at that scale. Units, scale and currency must not also appear
as informal context keys. Entity, book, date, basis and contract/cohort identity
remain explicit context fields and must match exactly for numeric operations.

Examples use currency:USD and goods:returned_unit as distinct named bases. A
price has dimensions {currency:USD:1, goods:returned_unit:-1}; units have
{goods:returned_unit:1}; their product has {currency:USD:1}. A rate has an empty
dimensional map, scale 1/1 and the same relevant context as the amount. It is
not automatically universal across entities or measurement dates. Currency
names are nominal dimension identifiers; the interpreter never supplies FX.

For A=a*s_A*D_A and B=b*s_B*D_B, multiplication gives coefficient a*b,
scale s_A*s_B and exponents d_A+d_B. The rule follows directly by collecting
the products of named bases. Addition/comparison require identical dimensional
maps, scales and contexts. Thus 1 USD million cannot be compared with 1 USD
without an explicit conversion outside this fragment. USD*USD is a legitimate
derived USD-squared type but cannot satisfy a currency-amount comparison.
Scale multiplication is representational arithmetic, not a rounded posting rule.

Negative coefficients remain allowed. Scales must be positive; dimension
exponents are bounded nonzero integers. Unknown operands remain unknown even
when multiplied by zero; no inhabited-domain or source-truth theorem is inferred.
All original dependency identities and unknown reasons survive. The result
records inferred product types and values separately from source inputs.

## Implementation and reuse

The v2 checker validates dimensions and every expression before arithmetic.
It evaluates product nodes as pure exact intermediates and lowers remaining
operations to the protected v1 interpreter. Encoded v1 contexts carry explicit
dimension and scale strings under reserved keys; callers cannot supply those
keys. This is an internal lossless type encoding, not a migration of source
meaning. Generated input identities are private, deterministic and forbidden
for caller inputs. The public result restores original dependency and unknown
identities and preserves v2 manifest/value hashes and all original declarations.
No Python callback, arbitrary code or solver is introduced.

Every intermediate has an auditable inferred type and dependencies. Tests must
ensure a product dependency does not disappear when lower-level v1 inputs are
pruned as unused, that a decisive Boolean still retains unknown branch inputs,
and that caller input names cannot collide with generated names. The v1 check
semantics remain the actual comparator for expressions without products.

Core 0 supports rate*amount and fully known scalar products, but its validated
profile explicitly rejects products of two dimensional quantities. Compare
known coefficient arithmetic only and record that limitation. Its evaluator's
symbolic/observation semantics are not inherited. The current extension makes
no claim that Core 0 already supports units*price as a typed financial product.

## Compatibility and evidence

No implicit v1 migration exists. A caller must supply an exact old-type to
new-type declaration, preserving non-unit context and making units/scale
explicit. Validate that mapping independently before adding a public conversion.
This increment uses independently authored v2 records; v1 records remain
unchanged and replayed. Text and binder support for v2 remain separate work.

Retained refund, recovery and deferred-balance equalities provide discriminating
known-value examples under explicitly supplied unsettled/zero-base premises.
Evaluate unknown and wrong quantities as well. Those premises are not discharged
by multiplication and remain residual requirements until guarded semantics are
implemented. Products, equality and context correctness are the primary criteria;
counts and speed are explanatory. No full method eligibility, source/accounting
authority, actual-company feasibility, complete DSL or production follows.
