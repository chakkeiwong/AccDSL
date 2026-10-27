# Text authoring and immutable requirement exchange

The protected MethodRequirements/1 core remains the typed-library comparator.
The frontend uses named, semicolon-terminated declarations, following existing
return and statement-context frontends, with a small prefix expression grammar.
It reuses the core validator/evaluator and does not implement new truth rules.
This is authoring/transport conformance, not a usability or DSL-superiority result.

Each declaration occupies one LF-delimited line. Blank lines are permitted;
comments, imports and arbitrary expressions are not. JSON strings encode names
without Unicode normalization. Contexts and reference lists are strict JSON
objects/arrays with duplicate-key and non-finite-number rejection. Scalar types
are explicit and no numeric or boolean coercion occurs.

    requirements "MethodRequirements/1" "method.id" "1";
    input "amount" rational reported_measurement {"unit":"USD"} "reading:amount";
    require "nonnegative" invalid unresolved ["amount"] [] (le (const rational {"unit":"USD"} "0/1") (ref "amount"));
    capability "method.id";
    residual "Legal opening and accounting admission remain separate.";
    select "<canonical manifest SHA256>";
    bind "amount" unknown "not admitted as legal state";
    available "method.id";
    end_requirements;

The expression forms are (ref STRING), (const TYPE CONTEXT VALUE),
(eq EXPR EXPR), (le EXPR EXPR), (lt EXPR EXPR), (add EXPR EXPR),
(sub EXPR EXPR), (all EXPR ...), (any EXPR ...), and (not EXPR).
all/any require at least one operand. A binding is known VALUE or unknown REASON;
the literal text unknown remains an ordinary known text value when quoted.
Booleans are JSON true/false, not integers or quoted words.

The exchange contains profile MethodRequirementExchange/1, definition,
selected_digest, values and available_capabilities. The selected digest must
match the manifest content, including context, source roles, requirements and
residuals. It is a content identity, not authentication or factual authority.
The trusted caller owns registry selection and capability availability;
transporting these fields does not verify code installation or trust an
untrusted sender. Assessment always retains the core's no-admission boundaries.

The parser rejects missing/duplicate headers, selections, input identities,
bindings and terminators, unknown declarations/operators, trailing content,
extra operands, malformed JSON, duplicate nested keys, noncanonical rationals,
context/type mismatches and stale selection hashes. Text size, declaration
count and expression depth/node limits are explicit engineering limits.

Independent examples cover retained company operations and returns, legal
cash versus a reported consolidated measurement, and an insurance-cohort
context with unknown review findings. The latter examples are constructed
language cases, not accounting-method demonstrations. The same numeric amount
in different book contexts cannot be compared without an explicit conversion
outside this fragment. No source mapping, accounting finding or company fact
is invented. Each typed example is written independently before rendering.

Pass requires identical typed/text records and evaluator outputs plus
adversarial refusals. A matching roundtrip alone cannot rule out a shared bug;
independent token/string and expected-result cases complement the protected
core tests. No full requirement closes; source/authority admission, generic
method eligibility, history reconstruction and production remain open.
