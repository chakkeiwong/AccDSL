# Bounded integration audit — 26 October 2026

Target readers are financial-system implementers who have just read the native
event-contract example. They need to distinguish authored methods, selected
invariant rules and original event intent in one program. The live gap is
whether the checked typed examples can actually be expressed in source.

Scope: one appendix subsection after A.54.11 plus its adjacent pages. Preserve
all Version 4.48 sources, mathematics, citations and PDF in their original tree;
create a separate 4.49 successor. No source claims or scientific rankings change.
The section moves from the composition problem to explicit ownership, then the
direct algorithm edit and the checked finite result. It leaves general invariant
authoring and accounting acceptance open.

Skeptical audit: exact source preservation and a clean build are necessary but
cannot establish readability or financial correctness. Inspect the rendered
transition and ask: what is authored; what is selected; why are full inputs
retained; what changes under a half collection; what remains missing? These are
author questions only. Independent reader and human acceptance remain pending.

Pre-build review caught one substantive wording issue: unknown inputs are not
structural errors. The source now states their runtime unresolved status.
Parser review improved nested method error locations and removed two inert
diagnostic lines before pinning the final implementation.
