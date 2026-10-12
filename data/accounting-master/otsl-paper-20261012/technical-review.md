# OTSL representation and the limits of syntax validation

12 October 2026. E08/C06, E14/C07; MC23/25/29–35, G8/G9/G10/G18.
The identified technical source is **arXiv:2305.03393v1, 5 May 2023**, by
Maksym Lysak, Ahmed Nassar, Nikolaos Livathinos, Christoph Auer and Peter Staar.
All fourteen PDF pages, including references, were read; ten selected renders
were inspected. The archive comment says twelve pages; the retained PDF has
twelve main-text pages with references continuing through fourteen. This
describes the inspected bytes, not an inferred page-for-page published match.

The exact Springer DOI and Crossref records identify the ICDAR 2023 paper,
pp. 37–50; the publisher gives first online 19 August 2023. The purported
publisher PDF route returned the same HTML landing, not PDF bytes. The
exact-title arXiv query identified one result and its versioned PDF. Published
full-text equivalence remains **not checked**. The publisher, arXiv history
and Crossref relation fields revealed no correction/withdrawal notice in this
bounded reading; comprehensive correction clearance is not established.

## Fair account of the paper's mechanism

Sections 3–4 (pp. 5–8) replace HTML markup with a row-major sequence over an
atomic rectangular grid. C starts a cell, L joins the left neighbor, U joins
the upper neighbor, X joins both, and NL ends a row. Compared with the paper's
HTML vocabulary, this has five tokens and shorter example sequences. Figure 1
has 55 HTML versus 30 OTSL tokens; Figure 5 has 258 versus 135. These are
specific examples, not universal ratios or measured local speedups.

Section 4.2 prints six rules: L's left neighbor is C/L; U's upper neighbor is
C/U; X has U/X to its left and L/X above; the first row uses only C/L; the
first column only C/U; all rows have equal length and terminate with NL.
The authors argue that backward-looking rules permit validation during
generation and thereby guarantee syntactically valid sequences. Section 4.3
explicitly says valid syntax does not guarantee correct prediction. It offers
as an example heuristic trying the next-highest-confidence token until the
rules are satisfied. This is an illustrative correction procedure, not evidence
that every later implementation uses it. Section 4.1 also claims capability
for lossless conversion to HTML.

The useful positive result is a compact representation with checkable local
conditions. Correctly encoded rectangular tables can use these tokens, and a
rectangular merge is illustrated by `C L NL / U X NL`. What does not follow
from the six printed conditions is a guarantee that **every accepted sequence**
describes rectangular merged cells. That stronger target must be checked
separately before a source-preserving HTML conversion is claimed.

## Counterexample in the paper's notation

Consider `C L NL / U C NL`, a two-row, two-column grid. The first L has C to
its left; the U has C above; there is no X to violate rule 3. The first row
contains C/L, the first column C/U, and both rows have two slots followed by NL.
Thus all six rules pass. Under Section 4.1's merge meanings, the top-left C,
top-right L and bottom-left U belong to one cell. The bottom-right C begins a
different cell. The first cell occupies three corners of a 2×2 rectangle and
omits the fourth: it is L-shaped.

Ordinary HTML rowspan/colspan describe Cartesian rectangles. Giving the first
cell rowspan=2 and colspan=2 would also occupy the bottom-right slot assigned
to the second C. Splitting it into two HTML cells changes the cell partition.
The claimed target is a nonoverlapping rectangular-cell partition preserving
the grid and cell identity; the quantity actually guaranteed by these six
checks is weaker local token admissibility and equal row lengths. They are
different. The universal sufficiency inference is **wrong relative to that
stronger target**. This does not refute the five-token encoding for valid tables
or the narrower definition of syntax as merely satisfying the printed rules.

`finite-diagnostic.json` checks each rule and independently joins the atomic
slots. Three positive rectangular examples and one known invalid first-row
example check the transcription. This is a reproducible finite counterexample,
not a complete replacement grammar, exhaustive proof, stochastic experiment,
or evidence that a trained model emits the example. The repair trigger is an
explicit rectangular-cell/coverage/overlap check. A previously uninspected
additional constraint excluding this grid, or a different explicitly defined
merge semantics, would overturn the claim-specific counterexample.

## Later official code: different vocabulary and partial correction

The retained 4.0.2 commit is d1569fdffee1d09cb3111d6d5490991cb59d59fd. Its
newly acquired `docling_ibm_models/tableformer/otsl.py` exactly matches Git blob
60b9151ef419aa3e8f45a640fd6a0c9839105736 in the previously retained tree.
Lines 1–241 were read in full: module context, token cleaning, row-width check,
padding, tag/cell count check, directional span searches and OTSL-to-HTML
conversion. `html_to_otsl` at 244–550 was not audited. No upstream module was
imported or executed.

The later vocabulary distinguishes fcel/ecel and header-related ched/rhed/srow,
plus lcel/ucel/xcel/nl and control tokens. It is not literally the paper's
five-token vocabulary. The broad directional correspondence is visible, but a
complete representation equivalence is not proved. `otsl_sqr_chk` (35–61)
checks equal nonempty row-group lengths; it does not check all six paper rules,
required final NL, or rectangular merged-cell occupancy. The predictor has a
separate same-named local checker (52–86), rather than importing this helper;
its width result is called but not used as a validation verdict at the inspected
prediction site. No signature-mismatch inference is made between these distinct
functions.

`otsl_to_html` (121–241) pads unequal rows using lcel, then independently
searches right and down for spans. A direct source trace on
`fcel lcel nl / ucel fcel nl` yields a first cell with colspan=2 and rowspan=2,
followed by another cell in the second row. It does not check that the
bottom-right fcel is already inside the first rectangle. This is a static
trace of one helper on a stated input; no installed conversion or frequency
measurement ran. Valid HTML markup is a different target from preserving the
original two-column partition. Padding is itself a structural change requiring
provenance, not evidence that the missing cell was observed.

The complete `TableModel04_rs.predict` body (110–328) uses argmax and two
specific substitutions. It replaces xcel by lcel under `line_num == 0`, and
replaces lcel following ucel with fcel. There is no ranked-valid-token search
in this body. More seriously, line_num is initialized to zero at line 170 and
has no subsequent assignment. The first-line guard therefore remains true
throughout generation. If a raw xcel is chosen on any later row, it is still
rewritten to lcel. This is **wrong relative to the comment's stated first-line
scope**, as established by complete-body reading and an AST store check. It
does not establish that a particular checkpoint emits affected tokens, or that
the complete later pipeline fails on a specified report. Correcting upstream
runtime or selecting another release is outside this source-preparation unit.

## Evaluation and default audit

Section 5 compares OTSL and HTML within TableFormer. Table 1 varies encoder /
decoder depth among 6/6, 4/4, 2/4 and 4/2 on PubTabNet. Section 5.2 selects
6/6 with eight heads, then independently trains on PubTabNet (395k samples),
FinTabNet (113k) and PubTables-1M (about 1M). The reported metrics are TEDS
after converting predictions back to HTML and cell-box mAP at IoU 0.75.
The content treatment is not specified as clearly as the original paper's
Table 4; do not compare these TEDS values with its structure-with-content row
as if they were one common measurement. Timings use a single core on one
AMD EPYC 7763 at 2.45 GHz. No local hardware/performance inference follows.

Table 2 reports overall TEDS of 0.955 versus 0.955 on PubTabNet, 0.959 versus
0.920 on FinTabNet and 0.977 versus 0.966 on PubTables-1M (OTSL/HTML). Its
simple PubTabNet row is 0.965 versus 0.969. The paper's phrase "outperforms
HTML across the board" is too strong if interpreted as every reported entry.
Table 1 also includes lower OTSL overall TEDS at 4/4 and 2/4. Retain exact
rows rather than universalize the narrative. Source-reported timings and mAP
are descriptive here; no seeds, uncertainty intervals or local paired test
establishes a statistical ranking of AccDSL candidates.

The selected depth is a source-reported HPO result on PubTabNet, not a reviewed
financial-corpus default. The later accurate/fast config depths resemble the
6/6 and 4/2 rows but do not identify experimental checkpoints. Training budgets,
loss details, split choices and seed replication are not sufficiently specified
in this copy to reproduce training from it alone. The 2022 box-loss ambiguity
is not resolved by this follow-up. A target-specific protocol remains necessary
before any local learned component is promoted. Figures 5–6 are named,
selected examples, not a random sample or a proof of better general accuracy.

## Disposition

Use the paper to explain the token representation and attributed evaluation.
Quarantine the stronger six-rules-imply-rectangular-cells claim from proposal
support; retain the exact counterexample and source's own validity/correctness
distinction. Do not quarantine the entire method or invent an observed runtime
failure. The source/code findings warrant a narrow Version 2.46 paragraph
showing the missing cell-geometry condition and recording that later decoding
also needs separate verification. Keep model selection and runtime held.

The paper offers a concrete mechanism to investigate, while source-to-release
equivalence and real-file validation remain open. This is a repair trigger for
the proposal's specification, not a continuation veto for the research or a
reason to restart the closed TableFormer inquiry.
