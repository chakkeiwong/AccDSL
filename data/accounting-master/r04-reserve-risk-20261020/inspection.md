# Technical source inspection

20 October 2026. Accepted manuscript 21270, DOI
10.1016/j.insmatheco.2018.12.002. Original bytes remain unchanged.

New reading covers §§5–7 and Appendices2–3 completely, supporting §2–3
definitions and §4 comparisons, and all45 reference entries as discovery.
The prior Appendix1/early-bootstrap reading is inherited, not repeated as a
new full-paper review. Six physical pages were actually viewed:2,21,23,35–37.
Their hashes and observations are in `render-review.json`. Text extraction
loses mathematical indices; the rendered appendix controls the formula reading.

Section5 distinguishes the projected capital profile from the runoff of an
already-calculated risk margin. Its best-estimate, standard-deviation and
quantile profiles share an opening capital amount for comparison. The capital
costs use year-end discounting; expected payment timing in the reserve example
is midyear. The paper's six-percent capital charge, three-percent discount,
99.5% loss-tail level and historical regulatory discussion are not current
policy. Section4 defines the source's positive capital tail as the negative
of a lower CDR quantile; CDR itself uses the profit sign.

Section6 presents lifetime risk functionals and the relative amount obtained
by subtracting the mean. Its VaR/TVaR/PHT choices and parameters are alternatives;
some levels are chosen to approximately match amounts or opening capital.
That numerical matching does not identify an insurer's preferences or
establish equivalence. Tables8–13 and Figures1–2 are descriptive source
illustrations. No uncertainty analysis supporting a model ranking is imported.
Table4 reports500,000 source simulations; none ran locally.

For future capital, the paper distinguishes the law of remaining payments
under today's information from the law conditional on what will be known
at a future date. Appendix3's Jensen/total-variance bound concerns expected
future standard deviation. Its fixed-origin CorollaryA3.2 additionally uses
the conditional CDR structure. The final paragraph explicitly connects the
variance to an estimated MSEP under Merz/Wüthrich's Bayesian representation.
This is not a universal identity for fitted reserves or a quantile bound.
The local derivation in `method-note.md` states stronger conditional-mean
assumptions explicitly and retains aggregate dependence without importing
the uninspected estimator theorem. Section7 itself warns that general
refitting need not yield zero-mean or independent future CDRs.

Appendix2's survival-integral definition and printed empirical weights do not
agree. On paper34/physical35, weights for ordered observations after the first
are printed with the survival differences reversed. They are nonpositive,
and at rho=1 with two observations their sum is zero. The source's assertion
that they sum to one is therefore wrong relative to that printed formula.
Corrected differences follow directly from the transformed survival function.
Figure2 displays positive weights but cannot prove which formula the software
used. The acknowledgement names proprietary ResQ and Igloo; this artifact
supplies no inspectable execution implementation. The final published edition
and any later correction are unverified. The verdict is confined to the
retained accepted manuscript; no numerical-table failure is inferred.

The finite expected-shortfall and quantile examples are local deductions,
not accusations about the source's actual simulation code. They make boundary
mass and exact-quantile-equivalence behavior explicit for a future discrete
AccDSL interface. The source's broad claim that equivalent confidence is
straightforward does not specify these conventions.

Section7 restricts its payment-triangle illustration: expenses, other relevant
fulfilment flows, unexpired risks, gross/reinsurance distinctions, dependence
and group allocation require additional work. The proposed method preserves
those requirements. The current3.44 text already warns that a reserve
distribution is not a justified RA; its genuine gap is a specified finite
transformation and future-information treatment, not a false claim that such
calibration was completed.

Metadata observations remain dated14October:51 OpenAlex citations,
is_retracted=false, empty Crossref relation and no checked update fields.
They are not fresh correction clearance. Original Wang1995 and Merz/Wüthrich
2014 sources, general coherence/allocation theory, alternative model and tail
assumptions, current authority and actual entity risk preference remain open.
The six additive ledgers classify these separately from the inspected source.

The semantic source-anchor audit caught a newline/form-feed indexing defect
after the first integrity check. `anchor-repair-note.md` preserves the first
attempt and explains the repaired21 passages. Numerical findings did not
change. This illustrates why hash/count checks do not establish claim support.
