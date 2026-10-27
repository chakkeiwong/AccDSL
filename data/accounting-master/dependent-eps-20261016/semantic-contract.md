# ConsequentialEPSWorlds/1 and ContingentOptionEPS/1

Historical source: EU2023/1803 original IAS33.33–57, especially35 and57.
Both are read-only documentary methods. Source bytes and exact reporting
context must match. Rational values use reduced canonical strings; unknown
findings are unresolved, false scope findings unsupported, malformed or
inconsistent requests rejected. Refusal returns no basic result, worlds, final
EPS, selection, trace or mutations. Neither method posts a conversion or bonus.

## Complete consequential worlds

`ConsequentialEPSWorlds/1`, operation `worlds`, accepts pretax profit before the
bonus P, nonnegative threshold H, rate q in[0,1], tax rate t in[0,1), positive
integer ordinary count and exactly two distinct whole-period debt series.
Each supplies nonnegative interest saved and positive incremental shares.
Findings establish complete bonus/tax terms, independent interest savings,
nonparticipating rights, equal continuing/total earnings and no other effects.
Negative P with nonzero t is outside the profile; no loss DTA is presumed.

For each of the four subsets S, calculate P(S)=P+sum(I_i),
bonus(S)=q*max(P(S)−H,0), tax(S)=t*(P(S)−bonus(S)), then earnings and denominator.
Return all four hypothetical worlds in stable ID order, `diluted=null`,
`selected=null`, and `selection_status=not_evaluated`. Asking this operation for
a final report returns `unsupported/nonadditive_selection_not_specified`.
These output limits are part of the mathematical target, not missing fields.

The formula calculates the supplied contract, not an IAS19 recognition method,
tax-law determination, or arbitrary nonadditive dilution ordering. Raw subset
minima are explanatory only. The P80 case demonstrates why they cannot silently
become a promotion criterion: each standalone conversion raises EPS, although
the combined hypothetical world lowers it.

## One contingent option and its similar outstanding prerequisite

`ContingentOptionEPS/1`, operation `report`, accepts one named outstanding option
and one named contingently issuable option. Each supplies a whole-period count
and nonnegative strike; they share a positive period-average market price.
No service proceeds, earnings effects, participation or further dependency is
allowed. Similarity is explicitly admitted by a supplied finding and is not
inferred from names or equal/different strikes. Unknown similarity prevents a
result. The contingent potential option is separately found absent from basic.

The supported condition is a nonfinancial store count, observed at2025-12-31,
against a positive required count. The agreement begins2025-01-01; its
contingency period remains open at the2026-01-01 exclusive report end. No future
forecast count or earlier stale observation is accepted.52/56/57 apply the
period-end count rather than a forecast at the actual contingency end.

Free shares are max(0,count−count*strike/average_market_price). Test the similar
outstanding series first. Its zero-earnings increment is strictly dilutive only
with positive earnings and positive free shares. The contingent series additionally
requires its period-end condition to qualify and the similar series to have
been selected. Otherwise preserve `condition_not_satisfied` or
`similar_not_assumed`; an isolated hypothetical EPS cannot override57.
With zero numerator effects, ordering the prerequisite first is consistent with
the tied incremental-earnings ratios. Return basic/diluted EPS, both candidate
trials, reasons and selected IDs. Actual exercise is never posted.

## Residual obligation

The source-grounded contingent dependency is specified for this finite family.
Arbitrary exercise graphs, nonadditive final dilution selection, actual
similarity/classification judgments, and changing participation/valuation terms
remain outside the delivered method. They are recorded as source/derivation or
actual-fact obligations; they must not be passed into OrderedEPS/1 or
CappedParticipationEPS/1 under false independence findings.
