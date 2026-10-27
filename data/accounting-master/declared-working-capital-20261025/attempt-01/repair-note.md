The first offsetting-posting diagnostic exceeded the inherited structure bound,
so it did not test the intended question. The reduced one-method/two-command case
was valid and exposed the actual bug: an unclassified +1/-1 receivable posting
pair was accepted because the net account change was zero. The schedule now checks
gross monetary posting diagnostics as well as net journal changes. This repairs
classification completeness without changing the frozen engine or weakening bounds.
Earlier14 tests passed but did not cover this same-event cancellation. Preserve
both diagnostic logs and the pre-repair implementation. The candidate failed;
the research direction and baseline remain valid,so continue the planned repair.
