# P17-01 execution note and skeptical audit

14 October 2026. E08; MC08–12/23/26/29/30/32–35; G1/G3/G6/G8/G15/G16.
This completes the source-specific inquiry from the retained local paper, text,
response headers and Crossref search response. No retrieval or runtime SQL test
was needed. Version 2.72 and its negative assessment are the starting baseline.

The question is whether Libkin's modified three-valued evaluation provides a
sound, complete or transferable method for AccDSL's financial-history queries.
The exact comparator is the current proposal's query contract in
`chapters/11-contracts.tex` and `sections/certain-answer-semantics.tex`, not
ordinary SQL's behavior or an unbounded financial solver. The primary source
criterion is reconstructible definitions, theorem hypotheses, proof steps,
counterexamples and limitations. A mismatched source, wrong variable,
unproved completeness or financial theorem transfer vetoes the affected claim.
Source bytes, venue metadata and a successful local calculation explain or
support the reading but cannot establish accounting or runtime validity.

The audit found two material risks in the preliminary note. First, it treated
`1/2` too loosely as an epistemic third truth value. Theorem 5.3 explicitly
assigns no guarantee to that output; it may arise from incomplete evaluation.
Second, the note's “no transfer veto” phrase conflicts with its own financial
domain limitation. The theorem does **not** transfer to AccDSL financial
queries without the relational/data/query assumptions. A further extraction
risk was confirmed: in the printed page A:7 false-negative example the guard
uses `y=1`, not the `x=1` yielded by the text layer. The source-page render was
inspected before the example was used.

Audit decision: proceed with a source-specific closeout and a narrow
manuscript explanation. Retain the existing exact/mixed/undecided financial
query contract because it already makes the correct distinction. Add the
direct approximation competitor and its limitation where the reader compares
query meanings. Do not change a solver default or claim the paper solves the
financial query problem. Absent publisher bytes and notice history remain
version/authority limitations, not reasons to discard the retained author
paper. A later P17-09 survey must consider this source with other direct
alternatives; this one reading does not close that wider literature workstream.
