The first ten-method unit run had one comparator-construction error:
Core 0 rational accepts Fraction values or decimal strings, not the new profile's
n/d strings. The new evaluator's other tests passed. The original test file is
preserved in before-comparator-repair/. The corrected adapter supplies exact
Fraction(a) and Fraction(b) to Core 0. Neither evaluator semantics nor expected
products change. This was an interface mismatch in the independent comparator,
not evidence against dimensional multiplication.
