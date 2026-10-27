# A three-series ordering discriminator

This is a project derivation for supplied synthetic terms. It does not select
diluted EPS under IAS 33. The admitted ConsequentialEPSWorlds/1 contract still
accepts exactly two series and returns selection_status=not_evaluated.

Profit before employee bonus is 90. The bonus is half of profit above 100;
complete tax expense is one fifth of profit after that bonus. There are 72
nonparticipating ordinary shares. Continuing and total earnings coincide;
all three series cover the whole period and have no other effects. A saves 10
interest and adds 40 shares, B saves 60 and adds 34, and C saves 10 and adds 8.
These are supplied expense, tax and instrument terms, not actual company facts.

For hypothetical conversion set S, define x=90+sum(I_i). Earnings are

    N(S) = (4/5)[x - (1/2)max(x-100,0)]
         = (4/5)x                 if x <= 100,
         = (2/5)x + 40            if x >= 100.
    D(S) = 72 + sum(b_i),         r(S) = N(S)/D(S).

The two expressions agree at x=100. The second follows by substituting
bonus=x/2-50 into post-bonus profit x/2+50 and multiplying by 4/5.

| Assumed conversions | Pretax x | Bonus | Tax | Earnings N | Shares D | Conditional r |
| --- | --- | --- | --- | --- | --- | --- |
| None | 90 | 0 | 18 | 72 | 72 | 1 |
| A | 100 | 0 | 20 | 80 | 112 | 5/7 |
| B | 150 | 25 | 25 | 100 | 106 | 50/53 |
| C | 100 | 0 | 20 | 80 | 80 | 1 |
| AB | 160 | 30 | 26 | 104 | 146 | 52/73 |
| AC | 110 | 5 | 21 | 84 | 120 | 7/10 |
| BC | 160 | 30 | 26 | 104 | 114 | 52/57 |
| ABC | 170 | 35 | 27 | 108 | 154 | 54/77 |

For a current set S and absent issue i, let a_i(S)=N(S union i)-N(S).
The complete incremental earnings/share ratios from the empty set are

    A: (80-72)/40 = 1/5,
    B: (100-72)/34 = 14/17,
    C: (80-72)/8 = 1.

Their strict order is A/B/C. After A, the remaining ratios become

    B: (104-80)/34 = 12/17,
    C: (84-80)/8 = 1/2.

Their order has reversed. A reaches the bonus threshold, so every subsequent
saved unit of interest raises earnings by 2/5. C's standalone increment had
been 8; after A it is 4. B's increment changes from 28 to 24. The differing
changes explain the reversal without an arbitrary dependency graph.

## Two fully specified candidate traces

The fixed candidate sorts the standalone ratios once. It then recalculates
the complete current and trial worlds for each issue, accepting only a strict
decrease. The marginal candidate re-sorts the remaining issues by their
complete increments against the current accepted world before each trial.
Rejected issues leave the queue. Neither definition is attributed to the source.

| Candidate | Trial issue | Current r | Trial r | Decision |
| --- | --- | --- | --- | --- |
| Fixed A/B/C | A | 1 | 5/7 | Accept |
| Fixed A/B/C | B | 5/7 | 52/73 | Accept: 364 < 365 after cross-multiplication |
| Fixed A/B/C | C | 52/73 | 54/77 | Accept: 3942 < 4004 |
| Marginal A/C/B | A | 1 | 5/7 | Accept |
| Marginal A/C/B | C | 5/7 | 7/10 | Accept: 49 < 50 |
| Marginal A/C/B | B | 7/10 | 54/77 | Reject: 540 > 539 |

The final ratios differ by 54/77 - 7/10 = 1/770. All ranked comparisons and
evaluated acceptance decisions in these two traces are strict. C alone ties
basic EPS, but neither trace tests C first. That unused standalone equality
does not cause their disagreement; the n=73 case below also removes it.

Every accepted addition decreases its then-current ratio in the fixed trace.
Nevertheless, removing B from its final set lowers that ratio to 7/10. To see
why, write the current numerator/denominator as M/D and one increment as a/b,
with D,b positive. Direct subtraction gives

    (M+a)/(D+b) - M/D = (aD-Mb)/[D(D+b)].

Thus an addition raises the ratio exactly when a/b > M/D. After AC, B has
increment 24/34=12/17, which exceeds 7/10 because 120>119. Its addition then
raises the ratio, although it lowered the earlier ratio after A. A single pass
under frozen ranks need not remain stable when its earlier selections are
re-screened in the final context.

All eight worlds show that AC is the unique minimum for these supplied terms.
That is a mathematical envelope only. The inherited P80 example already shows
why a minimum over all worlds cannot silently replace individual-series rules.
This example disproves equivalence of the two candidates; it does not prove
that marginal ranking is a generally valid accounting algorithm.

For completeness, the six prescribed trial permutations give the following
sequential diagnostic results. The other four orders are not asserted to be
allowed accounting sequences.

| Prescribed order | Accepted set | Final conditional r |
| --- | --- | --- |
| ABC | ABC | 54/77 |
| ACB | AC | 7/10 |
| BAC | ABC | 54/77 |
| BCA | ABC | 54/77 |
| CAB | AB | 52/73 |
| CBA | AB | 52/73 |

## An interval and the additive control

Hold the terms fixed and write n for the ordinary share count. A remains the
first ranked issue. After A, fixed-order B is accepted precisely when

    24/34 < 80/(n+40)
    24(n+40) < 2720
    n < 220/3.

After marginal-order C, B is rejected at or above

    24/34 >= 84/(n+48)
    24(n+48) >= 2856
    n >= 71.

Within this range the other required acceptances hold. A is accepted whenever
n<360. C after A is accepted whenever n<120, and C after AB whenever n<134.
The difference between the final ABC and AC worlds is

    108/(n+82) - 84/(n+48)
      = [108(n+48)-84(n+82)]/[(n+82)(n+48)]
      = 24(n-71)/[(n+82)(n+48)].

Consequently the strict-disagreement interval is 71<n<220/3. Both integer
counts 72 and 73 lie inside. At n=73 the fixed result is 108/155 and the
marginal result 84/121, differing by 48/18755. C alone is then strictly above
basic EPS, while all evaluated decisions remain strict. At n=71 the final
ratios tie; at n=74 both candidates select AC. These boundary checks verify
the inequalities, not a parameter search or a claim of typical behavior.

Finally set bonus rate q=0 at the original n=72. Earnings become (4/5)x
throughout. Increment ratios are now A=1/5, C=1 and B=24/17 and do not depend
on the current set. Both candidates use A/C/B and select A only, with ratio
5/7. The disagreement in the main case therefore comes from freezing ranks
across the supplied consequential expense, rather than from denominator
rounding, a different tax rate or a different implementation of the world.
