# Cumulative rebalancing: inspected source and local derivation

16 October2026. Retained EU2023/1803 original text:
`docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt`, SHA256
`37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664`.

IFRS9.6.5.11(a)–(c), local36084–36115, requires the cash-flow hedge reserve to
equal the lower absolute cumulative gain/loss of the instrument and item from
inception. The effective portion is OCI; the balancing amount is profit/loss.
Paragraphs6.5.11(d)/6.5.12,36115–36160, separately specify basis adjustment,
reclassification and expected/no-longer-expected cash flows on discontinuation.
Those endpoints are outside the present continuing observation method.

B6.5.7–8,41991–42002, defines rebalancing for effectiveness requirements and
requires old-designation ineffectiveness to be recognized immediately before
the adjustment. B6.5.9–14,42005–42101, distinguishes a changed relationship
from ordinary fluctuation or counterparty default. The offset numbers alone
cannot establish this judgment. B6.5.15–21,42103–42213, requires unchanged
objective, describes the four volume-change directions and updates the
expected sources of ineffectiveness/documentation.

The admitted method follows B6.5.17 only: increasing hedged-item volume does
not change measurement of the instrument or old item volume. Added volume
starts from its new designation date. The paragraph's100@80 plus10@90 example
therefore becomes1550 at price95 under explicit zero discounting. B6.5.18–20
describes decreasing instrument, increasing instrument and decreasing item
volume; those need distinct allocation/origin/discontinuation methods and are
not silently admitted by this implementation.

Local derivation, in a single common price risk with zero discounting: let
layer l have quantity q_l and designation forward price f_l. At current price
p, the cumulative hedged purchase loss is H=−sum_l q_l(p−f_l). D is the
separately supplied cumulative derivative gain from original designation.
If D and H offset, signed reserve R=sign(D)*min(abs(D),abs(H)); if one is zero,
R=0. Same-sign nonzero cumulative values are outside this finite profile.
Cumulative profit is I=D−R. Observation postings are ΔD to derivative,
−ΔR to reserve, and −ΔI to gains (debit-positive signs). They balance because
ΔD=ΔR+ΔI. Adding a layer at current p gives its initial change0; no journal or
reset of previous D/R/I is generated. Repeated additions therefore preserve
the origin formula by induction, independent of observation cadence.

This induction and formula are local deductions under supplied valuation and
eligibility findings. The source supports the cumulative/origin rule, not the
diagnostic market path or proof of an actually admissible ratio. Missing
objective/economic-relation/forecast/valuation/documentation findings remain
unresolved; false findings or other layer operations need another method.
