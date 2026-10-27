# Surface diagnostics disposition

The root-source audit covers only the 88-line wrapper and PDF metadata;
it does not recursively inspect included TeX. The separate `surface-body.json`
audits the new 104-line section directly: one heading/label, no displays,
no duplicate or missing references, no long-sentence or typo candidates at the
tool's thresholds. The unreferenced `sec:apple-disruption` label is retained as
a stable section target; an incoming cross-reference is not necessary.

The cumulative candidate checker independently checks inherited sources,
display text, all bibliography entries, citations, labels and references.
Rendered inspection covers the new argument and adjacent transitions; none
of these mechanical diagnostics certifies readability or source meaning.
