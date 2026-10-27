# Exact origin matching and cessation: source and derivation

17 October 2026. Historical official-text profile, not a current-law opinion.
Source retained at `docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt`;
its exact bytes and the earlier finite contracts are bound by `input-lock.json`.
No new academic-paper, software-reuse or literature-coverage claim is made.

## Inspected rules and limits

| Inspected IFRS9 text in EU2023/1803 | Permitted use here | What it does not establish |
|---|---|---|
| 6.2.1/4–6; 6.3.1; 6.4.1 | Eligible instruments/items, designated proportion, documentation and qualification are required facts | The synthetic facts do not prove actual eligibility or qualification |
| 6.5.6–7; B6.5.22–28 | Cessation is prospective when qualification fails; a still-qualifying relationship cannot simply be de-designated | A user choice of a stopped amount is not sufficient authority to stop |
| 6.5.11(a–c) | One relationship's cumulative signed lower-of and residual ineffectiveness | No general formula attributing a heterogeneous reserve to particular stopped items |
| 6.5.11(d), 6.5.12 | Basis transfer for the eventual nonfinancial asset; reserve retained if cash flows expected; immediate signed release if not expected; unrecoverable loss released immediately | Lack of high probability is not the same fact as cancellation |
| B6.5.16–20 | Keep original measurement on continuing quantities; added quantities have their own reference date/price; a retained undesignated instrument portion enters profit subsequently | Nominal fractions do not recover the histories of different item origins |
| 6.6.1–3; B6.6.1–8/11–15 | Individual eligibility, group management, proportional variability and tracking matter | An arbitrary heterogeneous net-position or untracked bottom layer is not admitted |
| B6.6.14 | Systematic/rational presentation allocation across income-statement lines | This is not a stopped-reserve measurement/allocation rule |

Text inspection inherited from the prior source investigation and checked in
this continuation at lines36093–36124 (lower-of/basis),42138–42247 (volume
origins/cessation),35963–36033 (prospective cessation),36257–36324 (group/layer).
The prior inspection also covered36015–36188,42328–42400,42645–42740 and
42812–42865. Paragraph anchors, not extraction line numbers, identify authority.

## Local deduction: a recorded effective gain, not an allocation of a residual

The request supplies a documented match from each separately tracked purchase
origin j to its own external instrument. It supplies dates d_j, quantities q_j,
and zero-value/zero-cost entry at the origin's price f_j. Under the admitted
zero-discount, no-carry/credit/basis linear model, its actual gain at price S is
G_j=q_j(S-f_j), and the named item-risk change is exactly -G_j. The request
must supply both marks; inconsistent values refuse. This values a synthetic
linear profile only; it does not price an actual contract from spot alone.

For every supplied measurement, all active origins' G_j have the same weak
sign and every pair is exactly effective. The relationship totals obey
G=sum_j G_j and H=-G, so signed lower-of gives R=G and ineffectiveness0.
The independently identified, fully effective origin gains sum to R. Recording
them by their pre-existing instrument/item match therefore loses no pooled
ineffectiveness term and does not replace the relationship's calculation.
This justifies one traceable attribution in this exact history. Neither the
standard nor this deduction establishes uniqueness for general histories.

At a same-date measurement and stop S_d, choose0<z<q_k from named origin k.
Its complete, directly matched accumulated gain is F_0=z(S_d-f_k). Continuing
quantities are q'_k=q_k-z and q'_j=q_j otherwise, with original d_j/f_j.
At any later admitted measurement, continuing G_c=sum_j q'_j(S-f_j), H_c=-G_c
and R_c=G_c by the governing lower-of. The full actual instrument value is
D=sum_j q_j(S-f_j). The stopped instrument portion is still owned. Its change
after cessation is U=z(S-S_d), giving D=R_c+F_0+U.

Let L denote cumulative signed reserve releases to profit, including canceled
cash flows or unrecoverable loss. Remaining stopped reserve is F=F_0-L.
Profit is P=U+L. Thus D=R_c+F+P. A negative unrecoverable amount u is recorded
as L increasing by -u, with0<=u<=-F when F<0. It cannot exceed the remaining
loss, be released twice, or reverse a previously released loss through a price
change. Cancellation releases the whole remaining F; a canceled forecast cannot
be reinstated in this finite method. Continuing loss recoverability is supplied
throughout; a new failure of that finding is outside this method.

At maturity buy Q=sum_j q'_j+z if stopped cash flows remain expected, otherwise
Q=sum_j q'_j. Supplier payment is Q*S; every full actual instrument settles
separately for its supplied mark. The attached reserve B=R_c+F reduces inventory
basis to I=Q*S-B. Cash C=C_0-Q*S+D; equity E=C_0+P. Since D=B+P,
C+I=E. Supplier payment precedes gross settlements; this finite order may need
more cash than the final net cost. No missing financing is manufactured.

## Discriminating example and remaining gap

Two origins of10 at8 and9 give30 and20 at11. Five units from the first
carry15, whereas five from the second carry10. The aggregate fraction5/20
would give12.5 in either case and cannot answer which named history stopped.
At maturity12, actual receipts70 are unchanged. Cancellation of the first
leaves continuing reserve50 and total profit20; cancellation of the second
leaves55 and profit15. Purchase15 costs180: inventory130 versus125, cash190
from capital300. If the stopped purchases remain expected, buy20 for240;
both histories carry total reserve65 to inventory175, cash130 and profit5.

Historical ineffectiveness, unmatched component valuation, opposed active
origin gains, acquired nonzero origins, new designations, multiple stops and
general group/layer allocation remain open. Their absence is a scope condition,
not evidence that they can be omitted from a wider implementation.
