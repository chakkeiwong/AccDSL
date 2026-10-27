# OrderedEPS/1: source and mathematical boundary

16 October 2026. MC02/04/05/16/17/19/24/25/28/30/32/34/35;
P17-05.04, with P17-05.03 and P5 dependencies retained.

The retained original EU Regulation 2023/1803 text has SHA256
`37f207b1ecdde43e3971cf076f127576d3d7810c791385ba5b1c35f110f17664`.
IAS33 technical paragraphs 33–50 (printed pages 237–240) and integral
Appendix A3 (printed page 245) were inspected for this continuation. The
earlier lifecycle unit inspected the complete IAS33 text and Appendix A;
its source records remain unchanged. This is historical-source method work,
not admission of an operative standard for a real issuer.

| Source | Rule used | Consequence for this contract |
|---|---|---|
| IAS33.33–35 | Adjust for after-tax dividends/items, recognized interest including costs/discounts, and other consequential earnings changes | Continuing and total earnings increments are separately supplied and evidenced. A coupon or assumed tax rate cannot replace them. |
| .36–38 | Add weighted dilutive potential shares; start at period opening or later issue; stop at conversion/lapse; actual shares enter basic after conversion; assess each presented period separately | Period-bound preprocessing must establish potential windows and actual conversion windows without overlap. An interim result cannot be averaged into the annual result. |
| .39–40 | Alternative conversion terms and investee instruments need additional analysis | Fixed independent effects are premises; the selector does not solve conversion choices or group attribution. |
| .41–43 | Dilution decreases continuing EPS, including an increase in loss per share; continuing ordinary earnings control | Use a strict signed comparison. Zero/positive increments are not automatically dilutive in a continuing loss. Negative increments are not categorically forbidden. |
| .44 | Consider each issue/series separately in ascending earnings per incremental share | Sort continuing earnings increment divided by positive weighted share increment; compare against the updated ratio. |
| .45–47A, A4–A5 | Option proceeds/average price and future-service value determine incremental shares | These are preprocessing methods, not outputs of this selector. A supported no-effect finding remains visible in the inventory. |
| A3 | Use the continuing-operations selected population for the other EPS measures even if their individual EPS becomes less negative | Carry total and discontinued earnings through the same selected list. Do not run a second selection on total profit. |
| .70(a)–(c) | Reconcile numerator/denominator and disclose antidilutive instruments | Retain every inventory item and each comparison, not just the final EPS. |

## Local derivation

Let current continuing ordinary earnings be N, the positive weighted ordinary
denominator D, and the candidate's independently fixed increments a and b,
where b>0. Both denominators are positive, so

    (N+a)/(D+b) < N/D
    iff D(N+a) < N(D+b)
    iff aD < Nb
    iff a/b < N/D.

No multiplication by a possibly negative numerator is used. Equality is
neutral and excluded by the strict decrease required by .41. Total earnings
increments never enter this comparison. Monetary and share units are fixed
by the reporting context before these rational operations.

For independent additive series, sort their ratios r_i=a_i/b_i. Whenever a
series is included, the updated ratio is a weighted average of the previous
ratio and r_i, strictly between them. It remains above r_i. Thus previously
admitted ratios remain below the final ratio q. At the first excluded ratio,
r_i>=q; all later ratios are at least as large and are excluded too. Equal
ratios below the current ratio are all included; ratios equal to the current
ratio are all excluded. Identifier order only stabilizes the trace.

To prove the final value minimizes over subsets, for the selected set S write
N-qD+sum_{i in S}(a_i-qb_i)=0. Every selected summand is negative and every
unselected summand is nonnegative. Replacing S by any subset T can only
increase the left-hand side. As D+sum_{i in T}b_i>0, its ratio is therefore
at least q. A neutral series may produce another minimizing subset; the
strict IAS33 convention excludes it. This proof is local algebra under the
independence premises, not a theorem that arbitrary instruments have fixed
additive effects. Exhaustive small-subset checks test implementation of this
target and cannot establish those accounting premises.

## Residuals

Participating or changing dividend rights, mutually exclusive conversions,
interacting earnings effects, investee attribution, zero-share/nonzero-earnings
adjustments and unmeasured consequences require further methods. Known complex
terms must remain unsupported; missing findings remain unresolved. Actual
terms, valuation, complete inventory and current authority are supplied
evidence obligations. EPS remains read-only and creates no journal or share.
