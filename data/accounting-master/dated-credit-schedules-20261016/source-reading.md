# Retained primary text and local deductions

Source: docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt;
its bytes are bound by input-lock.json. This is the retained historical EU
2023/1803 original text, not a claim about current law or a specific issuer.
The online official-source query returned no usable result. No new web text
is relied upon. Relevant source text was inspected directly before execution.

| Anchor / retained text lines | Inspected rule and its use |
|---|---|
| IFRS9.5.4.1(a),35178–35193 | POCI interest applies the original credit-adjusted EIR to amortised cost from initial recognition. |
| IFRS9.5.4.4,35221–35228 | Directly reduce gross carrying for the entire asset or identified portion with no reasonable expectation of recovery. |
| IFRS9.5.5.13–14,35392–35422 | Recognize subsequent cumulative lifetime-loss changes; favorable changes may exceed the initially embedded loss reduction. |
| Appendix A,37430–37448,37510–37603 | Amortised cost, CAEIR and ordinary EIR definitions; initial loss expectations distinguish the two rate targets; integral fees and costs belong in rate calculation. |
| B5.4.1–4,40076–40147 | Classify fees by their substance, distinguish non-integral services, and amortise integral items over the appropriate expected period. |
| B5.4.6–9,40159–40205 | Separate non-credit receipt estimates from modifications and credit revisions; original-rate catch-up; classification is not inferred from high risk alone; partial write-offs are required where the finding applies. |
| B5.5.44–45,40798–40825 | Discount to the reporting date; use original CAEIR for POCI. |

Local deductions: define N=G−L. Under the supplied ACT/365F annual compound
convention, G and signed L accrete by the same factor, so interest on N is
N(F−1). Revisions use direct remaining-cash PV; a subsequent loss change is
the change in N. A proportional whole-claim financial write-off removes the
supplied gross carrying allocation from both G and L. The identified portion
must have zero expected cash; expected surviving receipts cannot exceed its
remaining contract. The example's proportional allocation is an explicit
finite assumption, not a universal allocation rule imported from IFRS9.

After a terminal receipt, clearing the residual signed allowance changes G and
L equally and therefore creates no additional profit. This settlement origin
must appear in the direct gross reconciliation. Financial write-off and
settlement do not establish legal forgiveness; removed and uncollected
contractual cash remains separately recorded.

The integer-power enclosure proof is local arithmetic: for exponent p/q>0,
monotonicity on positive reals gives lo^q≤(1+r)^p≤hi^q iff lo≤F≤hi.
For positive future receipts, PV is continuous and strictly decreasing for
r>−1. Opposite certified endpoint signs thus enclose a unique EIR. A bracket
is not an exact point rate, and is not silently admitted by the financial
profile, which currently requires exact initial PV equality. These deductions
remain subject to independent technical/domain review.
