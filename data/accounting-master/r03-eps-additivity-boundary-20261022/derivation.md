# When the threshold-bonus earnings function is additive

This is a local mathematical derivation for the declared synthetic model.
It is not a general interpretation of IAS 33.44. The original final-selection
refusal and the three earlier discriminators remain unchanged.

For finitely many series, assume fixed interest savings I_i >= 0 and share
increments b_i > 0. Write I(S)=sum_{i in S} I_i and take n>0 ordinary shares.
Pretax profit P and bonus threshold H are real, and 0<=q,t<=1. The supplied
bonus is q max(P+I(S)-H,0), and complete proportional tax is t times post-bonus
profit. Thus

    N(S)=(1-t)[P+I(S)-q max(P+I(S)-H,0)],
    D(S)=n+sum_{i in S} b_i.

The earnings function is additive over subsets if fixed numbers a_i exist such
that N(S)=N(empty)+sum_{i in S}a_i for every subset S. Necessarily
a_i=N({i})-N(empty). Additivity is consequently testable independently of any
selection algorithm: isolated increments must reconstruct every conditional
world. Legal conversion dependence, attribution, other earnings effects and
actual tax treatment are separate assumptions, not consequences of this test.

## Necessary and sufficient conditions

N is additive if and only if at least one of these conditions holds:

1. q(1-t)=0;
2. P>=H;
3. P+I(all)<=H;
4. at most one I_i is strictly positive.

The conditions overlap and are not distinct economic categories. Equality at a
threshold is included. Series with zero interest savings still add shares;
they have zero earnings increments and must remain in any separately justified
dilution inventory.

Sufficiency follows directly. If q=0, the bonus vanishes and a_i=(1-t)I_i.
If t=1, all net earnings and increments are zero. If P>=H, nonnegative savings
put every world at or above the kink, so

    N(S)=(1-t)[(1-q)P+qH+(1-q)I(S)],
    a_i=(1-t)(1-q)I_i.

If P+I(all)<=H, every world stays at or below the kink, giving
N(S)=(1-t)[P+I(S)] and a_i=(1-t)I_i. These arguments use nonnegative savings:
without them, endpoint bounds do not control every subset. Finally, if at most
one saving is positive, the numerator has only two possible values. Assign
their difference to that series and zero to all others; every subset then has
the required representation. This last case can cross the kink and is missed
by an endpoint-only sufficient test.

For necessity, suppose none holds. Then q>0, t<1, c=H-P>0,
I(all)>c, and at least two savings are positive. Baseline profit is below the
threshold and its bonus is zero. The numerator reconstructed from isolated
increments is

    N_iso(all)=(1-t)[P+I(all)-q sum_i max(I_i-c,0)],

whereas the complete full-set numerator is

    N(all)=(1-t)[P+I(all)-q(I(all)-c)].

Subtract the second expression from the first. Since
I_i-max(I_i-c,0)=min(I_i,c),

    N_iso(all)-N(all)
        =q(1-t)[I(all)-c-sum_i max(I_i-c,0)]
        =q(1-t)[sum_i min(I_i,c)-c].

The bracket is strictly positive. If every I_i<c, its sum is I(all)>c.
If any I_j>=c, its capped contribution is c and at least one other positive
saving adds a strictly positive contribution. This also covers I_j=c exactly.
Multiplying by q(1-t)>0 preserves strict positivity. The isolated increments
therefore fail to reconstruct the full-set world, proving nonadditivity.

This proves the equivalence for the entire stated domain. No finite enumeration
is needed for the proof. The finite checks below test the transcription,
boundary handling and its relation to existing evidence.

## A useful higher-order failure

Take P=90,H=100,q=1/2,t=1/5 and three savings of 4. Baseline earnings are72;
each singleton has earnings376/5, and every pair has earnings392/5. The
isolated 16/5 increments reconstruct all singleton and pair worlds. The full
world has bonus1, tax101/5 and earnings404/5, rather than isolated total408/5.
The exact overstatement is4/5. Thus checking only pairs at the empty world is
not enough to certify additivity. The full-set gap detects this interaction
without enumerating the 2^m worlds. This is an existence example, not an
assertion about company prevalence or materiality.

## Relation to conditional selection

Under the additional premises already required by OrderedEPS/1, an additive
numerator and additive positive share increments allow its fixed-ratio proof.
Admission decreases N/D exactly when a_i/b_i<N/D, since all denominators are
positive. Sorting fixed ratios then gives the minimum over all conditional
subsets, with neutral items excluded by strict admission. This is the prior
mathematical theorem, conditional on independent admissible instrument effects.
The new result establishes one premise for this supplied earnings model; it
does not prove that an issuer's inventory satisfies all the other premises.

For threshold-crossing inventories with two or more positive savings and
q(1-t)>0, the additive theorem's premise is false. Its application there would
be wrong relative to the declared earnings function. That classification does
not choose between standalone, marginal or repeated-screening interpretations.
P80 has an isolated-overstatement gap8 and P90 has gap4; the strict ordering discriminator
has gap8; the final-deletion-instability example has gap8. All stay outside
the additive method's scope. Their alternative conditional selections remain
diagnostics, not final diluted EPS.

The proposed engineering use is a documentary precondition check, not a new
runtime or a new default: either record exact fixed increments with the proved
premises, or retain the existing unsupported/non-evaluated selection status.
No numerator or share count is rounded before this decision.
