# Finite syntax and cell-geometry check, before execution

12 October 2026. This is a focused documentary/mathematical diagnostic under
the active OTSL source plan, not product implementation or upstream execution.
The inspected author copy is arXiv:2305.03393v1, Sections 4.1–4.3, pp. 6–8.

Question: do the six printed local syntax rules suffice for the stronger
claim that every accepted grid describes nonoverlapping rectangular merged
cells? The exact comparator is the six rules, with the token meanings in
Section 4.1. The candidate counterexample is two rows `C L NL / U C NL`.
The positive rectangular comparator is `C L NL / U X NL`; a simple 2×2 table
and a simple horizontal span provide additional positive cases, and a top-row
U provides a known rule violation.

Primary criterion: evaluate every printed rule, then independently apply the
declared merge directions to atomic grid slots and check whether every cell's
member slots equal the Cartesian product of its occupied row/column intervals.
An accepted rule list with a nonrectangular merged cell refutes sufficiency for
that stronger target. This is deterministic counterexample evidence, not a
statistical estimate. A token-semantic mismatch, a mistranscribed rule or
unread relevant source condition would veto the counterexample. Re-read the
visible rule list before deciding; the main technical text and all references
have been read, and no appendix is present in this copy.

Default audit: atomic slots and directional merging come from Section 4.1;
ordinary HTML rowspan/colspan rectangles are the explicitly stated target,
not an assumption that every imaginable table must have rectangular cells.
The 2×2 size is a minimal explanatory example, not representative sampling.
Use only a local standard-library checker and AST inspection of retained code;
do not import/execute any upstream module or framework. The code check asks
whether the sole assignment to line_num is zero in the complete predict body,
not whether an installed model emits an affected sequence.

Skeptical audit passes: local grammar acceptance is kept separate from geometry
and correct source prediction; the finite comparator cannot establish a general
positive theorem. A counterexample rejects only the rule-sufficiency claim.
It does not invalidate the token language for properly constrained grids or
the paper's reported experiments. The next repair is an explicit rectangular
cell validation requirement, not a runtime rewrite. Record the derivation,
all cases and code-source boundary in finite-diagnostic.json and the technical
review before any manuscript use.
