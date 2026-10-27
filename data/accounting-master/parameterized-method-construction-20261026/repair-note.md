# Adverse type fixture corrected

The first verification run completed retained and new-intent full-request and
transition comparisons, then a wrong-type control expected a reason containing
date. The input instead failed the earlier ISO date value check. The corrected
control supplies a valid date value under the deliberately wrong type, reaching
the intended declared-parameter type mismatch. This is a test-target correction;
no constructor acceptance rule is relaxed.

The next run reached the intentional half-collection algorithm but its new
dimensionless constant used an empty context. The existing dimensional compiler
correctly refused product_context_mismatch. The authored constant now carries
the same declared chart context as the amount. This fixes the variant's typing
without weakening the retained compiler or constructor.
