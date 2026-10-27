# Strict positive return quantity

The original selected settlement predicate in
scripts/typed_return_transition_v1.py:95 uses 0 < n, followed by n <= sold.
Version3.67 equation eq:method-family-selected-conditions displays 0 <= n <= s.
That is a necessary but weaker condition, and is wrong if read as the exact
selected quantity restriction. The implementation and retained cases use the
strict original predicate. Change the manuscript successor to 0 < n <= s and
retain a zero-quantity regression explicitly. The monetary parent domain may
still include zero before intersection. Preserve Version3.67 and its hashes.
