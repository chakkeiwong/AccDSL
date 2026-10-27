# Aligned collar source and local derivation

17 October 2026. Retained primary text/PDF:
`docs/design/research/p08-v3-preparation/eu-2023-1803-original.*`.
Read IFRS9.6.2.1–6 (35733–35809),6.3.1–7 (35812–35898),6.4.1
(35900–35939),6.5.11–12 (36083–36160),6.5.15 (36179–36243),
B6.2.4 (41220–41224),B6.5.5 (41960–41980),B6.5.29–33 (42400–42520).

6.2.4(a) permits designation of intrinsic changes separately;6.2.5 allows
joint designation;6.2.6 prohibits a net-written option combination except as
permitted by B6.2.4. Equal premiums alone do not establish eligibility.
6.3.7 allows identifiable/measurable risk components, including above/below
specified levels.6.4.1 still requires documentation, economic relationship,
credit-risk and ratio findings. All remain supplied in this finite example.

6.5.11 measures the cash-flow reserve by the lower absolute cumulative
instrument/item changes and separately recognizes ineffectiveness. For the
admitted fully matched collar, the supplied hedged-item measurement equals
the opposite of the combined intrinsic change. Therefore the intrinsic
reserve equals that signed change and ineffectiveness is zero. This equality
is a checked finite input constraint, not an inference that matching names
or the eventual capped cash price establishes accounting effectiveness.

B6.5.31 explicitly covers a purchased/written put/call combination with net
nil time value at designation. Time-value changes enter OCI, although the
total time-value change over the complete relationship is nil. For a
transaction-related item the final time-value basis adjustment is nil.
B6.5.32 retains the requirement that time value relate to the item.
The profile is fully aligned as a combination; it does not generalize
B6.5.33(b)'s unmatched/opposed-change comparison.

Let q be the quantity, L<U the put/call strikes and S the current spot.
The actual call asset C and positive put liability P decompose into

    I_C=q max(S-U,0), I_P=q max(L-S,0),
    C=I_C+T_C, P=I_P+T_P.

At inception both intrinsic values are zero and T_C=T_P, with the gross call
premium paid and gross put premium received. Under the admitted matching
conditions, intrinsic reserve R_I=I_C-I_P and time reserve R_T=T_C-T_P.
Thus C-P=R_I+R_T at every measurement. The two reserves can be positive or
negative. They are separate origins, even if their sum is zero. Entries update
the two actual legs and the two reserve differences; no hypothetical asset is
posted. Interim marks can reverse sign without erasing their histories.

At expiry both T values equal zero. With supplier payment qS, call receipt
I_C and put payment I_P, net cash cost and final inventory basis are

    qS-I_C+I_P = q min(max(S,L),U).

For S<L this is qL; for L<=S<=U it is qS; for S>U it is qU. This local payoff
identity follows directly from the stated contracts. The basis adjustment is
minus R_I and minus R_T, the latter zero at expiry. Derivative settlement is
a distinct gross cash flow. No tax or cash-flow-activity classification is
inferred. Cash plus inventory equals initial capital when both reserves and
legs have cleared and no other transactions exist.

Synthetic mark plausibility has a separate diagnostic. Five terminal prices
(6,9,10,11,14) with equal weights have mean10 and q10 option values6 each.
Weights(.1,.1,.1,.2,.5) give mean11.7, call15, put3, hence intrinsic reserve7
and time reserve5. The reversed weights give mean8.3, call3, put15, intrinsic
reserve−7 and time reserve−5. Each calculation is an auxiliary per-date
convex-combination witness under zero discount. No joint transition law,
physical probabilities, calibrated option-pricing method or forecast is claimed.

The primary accounting source is historical. Actual contract rights, combined
eligibility, fair values, operative law and independent domain acceptance remain
external-to-this-calculation facts. The stopped-item allocation residual remains
separate because lower-of aggregation is not generally additive.
