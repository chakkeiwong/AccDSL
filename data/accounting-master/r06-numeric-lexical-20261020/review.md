# Numeric interpretation review

The comparator is the frozen exact candidate, not a float or canonical
spelling. The claimed and computed quantity agree within the narrow scope:
the numeric value denoted by admitted decimal/integer text under the retained
2004 specification. This does not equate the candidate with a complete
processor-supplied or financially valid fact.

All selected derivation paths were checked against the retained XML with
per-element namespace scopes. The initial assumption that namespace
declarations occur only at the root was wrong and was repaired before
construction. Likewise, the saved regex initially contained a wildcard
instead of a literal point because a transport escape was lost. The final
pattern uses a character class, and the negative fixtures demonstrate the
intended rejection behavior. Positive source observations alone would have
missed this defect; they were not used as the sole parser acceptance test.

The parser is intentionally narrow. XML whitespace collapse does not remove
NBSP, Unicode digit predicates do not define ASCII decimal digits, and Decimal
construction does not establish XSD lexical membership. The independent
Decimal calculation begins only after the lexical rule passes. Integer
membership is checked independently of whether a decimal value is integral.
Signs and zero spellings are retained even when their rational values coincide.

Nil is checked on its own branch. The two retained empty elements support
the selected no-content condition without relying on whitespace collapse.
An explicit space is not empty character content. The declaration is
nillable and has no fixed constraint; the remaining local-element/type and
XBRL obligations remain untested. Altered fixtures cannot grant full validity.

The six source ledgers describe a bounded specification inquiry and its
dependency trace. They do not claim a new comprehensive literature survey.
The historical specification edition is explicit; the local checker is not
an installed processor, a resource-budget policy, or a dependency admission.
There is no statistical or performance claim.

Preservation and one-time lifecycle rules survived restart. No completed
predecessor was reconstructed. E3's target-direction question remains pending,
with population, weights, margin, confidence, sample size and inference
unselected. That pending choice does not block independent R03–R06 work.
