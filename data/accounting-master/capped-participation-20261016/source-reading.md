# Senior/capped participation: source and local deduction

16 October2026. Historical EU2023/1803 original IAS33 text, paragraphs9–15
(15108–15162),33–47 (15318–15446),A13–A16 (15908–15946). Relevant primary PDF
and text are retained under docs/design/research/p08-v3-preparation. No current
issuer law or rights are established by the synthetic inputs.

Paragraph14(b) includes the period's cumulative preference entitlement whether
declared or not, excluding prior-period arrears. ParagraphA14 allocates the
remaining profit/loss by the actual rights, includes dividends in each class's
earnings and includes assumed potential shares in the ordinary population.
ParagraphA13 explicitly mentions caps. This finite participating class has a
senior cumulative entitlement and no residual loss sharing. Its equity
classification, cap, rights and tax-adjusted period amount are supplied.

Paragraphs33–35 require complete after-tax direct and consequential effects;
36–38 require dated share weighting;41–44 use continuing earnings and ordered
individual dilution. The finite cases have equal total/continuing earnings,
whole-period windows and unchanged rights. Option treasury shares are derived
separately under45–47. State-dependent gross effects, contingent exercise and
changing rights are not supplied to the additive family as if they were fixed.
Paragraph35's profit-sharing consequence is the next concrete dependence lead.

Let E be earnings before the two-class allocation, n ordinary shares, m total
participating residual weight, f the cumulative entitlement, and c the maximum
additional participation. The supplied rights give p=min(c,max(E−f,0)*m/(n+m));
class earnings are f+p and E−f−p. For E≥f, ordinary EPS is
max((E−f)/(n+m),(E−f−c)/n). That expression is a local derivation, not source text.
For E<f, absence of residual loss sharing gives (E−f)/n.

An assumed series adds complete nonnegative gross after-tax earnings a and
positive ordinary shares b. For any current nonnegative EPS r, both branches
fall below r iff a−r*b<0. If a−r*b>0 the previously active branch exceeds r.
Equality leaves it unchanged. Sorting a/b and applying that strict comparison
therefore selects successively dilutive series. Independently, a trial bound r
on both branches imposes the same subset sum of a_i−r*b_i against two constants;
including every negative term minimizes that sum. Hence a minimum exists in
the sorted prefixes. Exhaustive subsets check the finite examples separately.
For E<f, nonnegative a and positive b cannot make the negative EPS more negative.

Existing comparators: awards-participation proportional example and
OrderedEPS/1's separate nonparticipating additive contract. Neither is altered.
This method does not replace the existing lifecycle/date/attribution engines;
it admits their complete full-period effects for a distinct rights profile.
