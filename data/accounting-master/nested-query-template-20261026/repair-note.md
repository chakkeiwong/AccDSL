# Comparator provenance correction

The first complete-instance comparison found equal declarations and captures
but different coverage hashes and nested query results. The reference called
the preserved composition fixture with its default provenance label rather
than the template run's explicit supplied population provenance. Those are
different inputs, so different result hashes were correct.

Attempt-01 preserves the failed comparison and code. The reference now receives
the same explicitly constructed population declarations. No output field is
masked, and no candidate algorithm is changed. Every full instance result
remains subject to exact comparison.
