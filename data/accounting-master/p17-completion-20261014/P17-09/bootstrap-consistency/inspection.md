# Mack bootstrap: target, version and proof-dependency audit

14 October 2026. MC11/12/19/20/23/26/29/30/32/35; E07/E08.
Author documentary review, not independent mathematical certification.

## Exact sources and notices

Primary source is the 39-page final published Steinmetz/Jentsch article,
Insurance: Mathematics and Economics 115 (2024), 83–121, DOI
10.1016/j.insmatheco.2024.01.001. Institutional handle 2003/44429 links the
retained bitstream. First page says available online 17 January 2024; the
OpenAlex date is 21 January 2024. Preserve these distinct metadata fields.
The final PDF is CC BY. The existing 65-page arXiv2303.05913v1, 10 March
2023, remains a separate source and is not substituted for the publication.

Crossref's exact record has no update-to or relation entry identifying a
correction. A title query returned the article and seven unrelated records.
The inspected arXiv record exposes v1 and no withdrawal notice. No correction,
retraction or expression of concern was found in these bounded checks; this
is not proof that none exists. Institutional UI translations containing the
word "withdrawn" are not notices about this item.

No author-code link was located in the article, arXiv record or inspected
institutional record. The journal's data statement says no data was used.
It is not a software availability statement. No author was contacted.
The previously inspected ChainLadder package is not established as the code
for this article.

The backward search also retained Steinmetz's February 2023 dissertation,
oral examination June 2023, handle 2003/41966, 207 physical pages. Its Chapter
2 contains the earlier Mack theory under different numbering. Physical
64–65, printed 42–43, were inspected for Assumption 2.18 and Example 2.19.
The latter explicitly gives backward-moment approximations, not exact
reciprocal identities. The dissertation is not asserted byte-equivalent to
the 2022 journal article, DOI10.1016/j.insmatheco.2022.08.007. The remaining
dissertation and full 2022 proofs have not been independently checked.

## Technical inspection and permitted interpretation

Preprint: substantive portions of Sections 2–7, algorithm and theorem
statements; Appendix B.3/C and selected Appendix D. Published article:
Sections 2.1–2.3, Sections 3–6 target/algorithm/assumption/theorem passages,
Section 7.1.1/7.1.2 and descriptive Table 3/Figures 1–3; relevant proof
structure and dependencies in Appendix A, B.1/B.2/B.3, C and D.
Physical pages 14/15/18 (printed 96/97/100) were rendered and inspected.
Mathematical extraction was cross-checked there; PDF structure-tree warnings
did not prevent readable page rendering.

This is a claim-focused inspection. The long remainder bounds in B.1/B.2
and the inherited 2022 conditional CLTs were not reproduced line by line.
Do not label the article or its algorithm independently proved, or claim
that every appendix/table has been technically verified.

The target is the conditional law of R-Rhat given the latest diagonal Q.
The full upper triangle D contains additional information. Rhat(D) remains
random conditional on Q, but is fixed conditional on D. The authored
four-atom example in check_cases.py demonstrates that these targets differ.
The paper's asymptotic scheme keeps calendar boundary I fixed and grows the
triangle through older accident rows and development observations as n grows.
Increasing bootstrap replications B is a different limit.

Assumptions 2.2–2.5 require initial positive cumulative amounts with finite
variance, the stated conditional independence and forward moments, summable
factor excesses, summable (j+1)^2*sigma_j^2 and finite higher moments.
Assumptions 4.2/4.3 impose further controls on development tails and backward
conditional quantities. These are substantive model restrictions.

Theorems 4.1/4.4, adopted from the earlier theory, distinguish an order-one
process term from a square-root-scaled estimation term. Assumptions 4.6/4.7
require a continuous, correctly specified process family: identification by
the first two moments is within that family, not across all distributions.
Theorem 4.8 states process-law consistency under those assumptions.
Theorem 4.10 identifies the generally wrong conditional mean/covariance of
the original bootstrap estimation component. Theorem 4.11 still states
validity for the unscaled root because that component vanishes at that scale.
Do not call the entire method universally inconsistent or transfer this Mack
result to the incremental ODP procedure.

The proof mechanism was traced to the relevant obligations: B.1 truncates
the sums/products to a finite K, uses continuity and parameter consistency
for the finite part, then controls two remainders. B.2 equation B.13 uses
original fixed weights; conditional on D its bootstrap factors do not acquire
the Q-conditioning covariance. Appendix A's conditional Lyapunov CLT and
delta method therefore yield the unconditional parameter covariance there.
B.3 uses a zero inner conditional expectation for the process/estimation
cross-covariance. Appendix D records the earlier covariance decomposition.
These inspected steps explain the claimed distinction; they do not discharge
the unverified remainder and inherited-proof obligations independently.

## Proposed repair and an unfulfilled implication

Section 5 reconstructs the upper triangle backwards from Q, refits it,
generates the future using the original estimates, and changes the center.
Assumption 6.2 stipulates conditional CLTs/covariances for that backward
construction. Appendix C.2 invokes those properties and the earlier proof
technique; it does not prove them for an arbitrary gamma reverse generator.

Section 5.1 Step 2 specifies E[G|C_next]=1/fhat and
Var(G|C_next)=sigmahat^2/C_next. These are proposed backward moments.
They do not follow from E[Y|X]=fX and Var(Y|X)=sigma^2 X.
The positive finite law in check_cases.py has f=2, sigma^2=1, but at Y=3
the true backward mean/variance are 11/7 and 12/49, rather than 3/2 and 3.
Claimed equality is wrong for this example. A separate asymptotic argument
would be needed to justify an approximation in a specified family/regime.
The example is not a counterexample to a theorem whose complete assumptions
it has not been shown to satisfy.

## Literal centering formula

Printed page 96, equation 5.3 sums projected ultimates, while Step 4 defines
reserve as ultimate minus latest paid cumulative claims. Read together
literally, reserve minus that center differs from the displayed Step 5
product-difference root by minus the diagonal sum. At q100, ultimate130,
fitted ultimate120, the intended reserve error is 10; the literal
equation5.3 substitution gives -90.

Verdict: the literal centering formula is wrong relative to the stated
reserve-error target and is quarantined from implementation. The adjacent
Step5 difference and equation6.1 provide a reviewed internal source
cross-check for the intended cancellation. Local algebra supplies the
explicit corrected reserve center. This scoped exclusion does not turn a
typographical inconsistency into a rejection of every theorem in the paper,
and no execution-code error is inferred.

## Final publication changes the simulation question

The preprint's Section7.1 fixed-estimate future simulation is not the final
published conditional experiment. The journal Section7.1.1 simulates full
triangles for unconditional interval coverage. Section7.1.2 reconstructs
1000 past triangles per diagonal using an approximate same-family backward
law with true forward parameters, equation7.4, then simulates futures.
The article acknowledges the true backward conditional distribution is
difficult to obtain. Its conditional coverage is thus measured under that
constructed reverse experiment, not an independently established exact
conditional law of the original forward model. Repeating a convenient
reverse assumption in both candidate and reference can hide its error.

The study describes I10, n0/10/20/30/40, 500 outer triangles, 10,000
bootstrap replicates and gamma/lognormal/truncated-normal families. Published
table labels use 10/20/30/40/50; no local replication resolves that labeling
difference. There are unconditional coverage/length tables and conditional
coverage box plots. Their reported differences are descriptive here; no
local paired uncertainty analysis or statistically supported ranking is
available. No default, calibrated tail or IFRS17 risk adjustment follows.

## Snowball and source limits

OpenAlex W4391074055 reports four citations on 14 October2026. All four
returned citing metadata records were screened and ordered by both citation
count and date in the ledger. A frequency-severity conformal paper is a
potential comparator with a different target; hurdle-GARCH is peripheral
to this conditional triangle question. Tea and cardiac graph-prediction
papers are peripheral metadata results, not actuarial validation.
No direct correction/replication appeared in this four-record result.

Backward candidates and explicit dispositions are appended to the six
research ledgers. This bounded inquiry does not close the entire literature
frontier. The 2022 underlying theory, England/Verrall2006, robust/calendar
effects, Bayesian/Bornhuetter-Ferguson and target-specific empirical
validation retain separate obligations. No blocked original was relabeled
as inspected.
