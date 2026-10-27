# A marginal-ranking result that becomes unstable after inclusion

The question is mathematical: does the previously defined forward recomputed
marginal candidate always finish with a set from which deleting any included
series cannot lower the conditional earnings/share ratio? This is not a proposed
interpretation of IAS 33. The supplied model and continuing/total earnings
convention are the same as the prior discriminator; only the instruments and
ordinary shares change. All denominators are positive and all tested comparisons
are strict.

Initial pretax profit is 90, ordinary shares are 178, bonus expense is half the
profit above 100, and tax expense is one fifth of post-bonus profit. Series A
saves 975 interest and adds 1000 weighted shares. B saves 10 and adds 20 shares.
C saves 10 and adds 199/10 weighted shares. These deliberately uncalibrated
terms test existence of a failure, not typical accounting outcomes.

For set S write I(S) for saved interest. Then

    x(S) = 90 + I(S),
    bonus(S) = (1/2) max(I(S)-10, 0),
    tax(S) = [x(S)-bonus(S)]/5,
    N(S) = (4/5)[x(S)-bonus(S)],
    D(S) = 178 + sum(b_i : i in S),  r(S)=N(S)/D(S).

At the empty set N=72. Every nonempty set here has I>=10, so substitution gives
N(S)=76+(2/5)I(S). At I=10 this agrees with (4/5)(90+I)=80.

| Set | Pretax | Bonus | Tax | Earnings | Shares | Ratio |
| --- | --- | --- | --- | --- | --- | --- |
| Empty | 90 | 0 | 18 | 72 | 178 | 36/89 |
| A | 1065 | 965/2 | 233/2 | 466 | 1178 | 233/589 |
| B | 100 | 0 | 20 | 80 | 198 | 40/99 |
| C | 100 | 0 | 20 | 80 | 1979/10 | 800/1979 |
| AB | 1075 | 975/2 | 235/2 | 470 | 1198 | 235/599 |
| AC | 1075 | 975/2 | 235/2 | 470 | 11979/10 | 4700/11979 |
| BC | 110 | 5 | 21 | 84 | 2179/10 | 840/2179 |
| ABC | 1085 | 985/2 | 237/2 | 474 | 12179/10 | 4740/12179 |

The standalone incremental earnings/share ratios are A=394/1000=197/500,
B=8/20=2/5, C=8/(199/10)=80/199. Their strict order is A, B, C. A is accepted
because 233/589<36/89. After A, the remaining increments are B=4/20=1/5 and
C=4/(199/10)=40/199. Their order is B before C. Both additions lower the
current ratio. Recomputing the ranking therefore still finishes at ABC.

Cross-products trial_N*current_D-current_N*trial_D are -1868, -4608 and
-4561 respectively. None is zero. Re-ranking was actually done at each step;
the example does not rely on freezing standalone amounts or denominator rounding.

At BC, A's complete increment is (474-84)/1000=39/100, whereas
r(BC)=840/2179<39/100. A would now raise the ratio. Thus removing A from ABC
strictly lowers it:

    4740/12179 - 840/2179
       = [4740*2179 - 840*12179]/[12179*2179]
       = 98100/26538041 > 0.

The same addition/removal identity used in the earlier discriminator explains
the sign. For numerator M, denominator D>0 and increment (a,b) with b>0,

    (M+a)/(D+b) - M/D = (aD-Mb)/[D(D+b)].

Here the first selection includes a shared four-unit earnings transition from
72 to the nonempty-set intercept76. After BC that transition is already present,
so A's final-context increment is 390 rather than its standalone394. The later
series jointly reduce the base ratio below 39/100; forward re-ranking never
revisits an accepted series.

An analytic range shows this is not a rounding artifact. Holding the instruments
fixed and writing n for ordinary shares, A initially lowers the ratio exactly
when 394/1000 < 72/n, or n<36000/197. Removing A after BC lowers the final
ratio when 84/(n+399/10)<39/100, or n>22813/130. The selected n=178 satisfies
both strict inequalities. These two inequalities explain the initial/final A
reversal; they are not asserted to be a complete parameter characterization of
all other trace decisions, which are checked explicitly at n=178.

The prescribed alternate B/C/A sequence accepts B, accepts C, then rejects A;
its cross-products are -16, -800 and +981. It finishes at BC. That sequence
violates the initial most-dilutive-first ranking because A initially ranks
first. It is a diagnostic path, not an accounting-admissible workaround. The
eight-world enumeration also finds BC as the unique minimum, which likewise
does not answer the source's individual-series/ordering requirements or P80.

With bonus rate zero, N(S)=(4/5)[90+I(S)], and increments are context independent:
B=2/5, C=80/199, A=39/50. Fixed and marginal algorithms both accept BC and
reject A, giving 880/2179. Every tested additive-control decision is strict.
This control isolates the consequential shared expense; it does not prove a
general accounting selection theorem.
