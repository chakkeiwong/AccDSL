# The level at which the minimum is taken matters

These are conditional mathematical results. They neither allocate an actual
cash-flow hedge reserve nor establish eligibility of the synthetic relationships.
Write x_j for cumulative instrument gains and y_j for the negatives of the
corresponding item-risk changes. Let X=sum x_j and Y=sum y_j. When XY>=0,
the diagnostic relationship reserve is R=sign(X)min(|X|,|Y|), with sign(0)=0.
Its cumulative profit is X-R. This signed convention expresses the instrument
gain orientation; it is not a substitute for effectiveness/qualification facts.

Compare R with the proposed shortcut
L=sum_j sign(x_j)min(|x_j|,|y_j|), for individually offsetting pairs x_j y_j>=0.
This shortcut takes a separate lower-of at each origin. The source requires
measurement for the designated relationship, not these newly created units.

## A complete identity on the nonnegative domain

Suppose all x_j,y_j>=0. Define l_j=min(x_j,y_j),
u_j=max(x_j-y_j,0), v_j=max(y_j-x_j,0). For each j,
x_j=l_j+u_j and y_j=l_j+v_j: check separately x_j>=y_j and x_j<=y_j.
Summing gives X=L+U and Y=L+V, where U=sum u_j,V=sum v_j. Therefore

    R = min(X,Y) = L + min(U,V),
    R-L = min(U,V) >= 0.

Equality holds exactly when U=0 or V=0. Since the summands are nonnegative,
this means x_j<=y_j for every j, or x_j>=y_j for every j. Exact matching is
sufficient, but not necessary. If one origin has strict excess instrument gain
and another strict excess item change, both U and V are positive and the
shortcut is strictly too small relative to the declared relationship target.
This is a finite-sum algebraic theorem, not an accounting allocation theorem.

For x=(12,8), y=(6,12), X=20,Y=18. The relationship reserve is18 and profit2.
Separate minima give6+8=14 and apparent profit6. Here U=6,V=4; the missing4
is precisely min(U,V). A balance made using14 can still add up to20, but it
computes a different measurement unit. Balance alone does not validate it.

## Opposed gains invalidate the unsigned inequality

For x=(12,-8), y=(10,-9), the relationship totals are X=4,Y=1. Thus R=1,
profit3. The shortcut gives10-8=2 and apparent profit2. It is now larger than
the relationship reserve. Reversing every sign gives R=-1,L=-2 and profit-3.
Both examples have individually offsetting pairs and offsetting aggregate
changes in the stipulated orientation. Their actual designation/qualification
is not established. The nonnegative theorem must not be exported to them.

For exact origin matches x_j=y_j of any signs, X=Y and R=X. Also each
individual term equals x_j, so L=X. For example (5,-5) gives aggregate zero
with nonzero component gains, and (30,-10) gives20. This proves that opposed
origin signs alone are not an algebraic obstacle to conservation under exact
matching. It does not remove OriginMatchedCessation/1's deliberate same-sign
scope restriction, supply a reserve-release interpretation, or prove eligibility.

## Aggregate conservation does not identify a stopped amount

Return to x=(12,8), y=(6,12), R=18, profit2. Suppose only for this analysis
we impose weak bookkeeping constraints 0<=rA<=12, 0<=rB<=8 and rA+rB=18.
Substitute rB=18-rA. Its upper bound requires rA>=10; its lower bound requires
rA<=18. Intersect with 0<=rA<=12 to obtain exactly 10<=rA<=12. Hence every
solution is rA=10+t,rB=8-t for 0<=t<=2.

The caps are an explicitly chosen analytical hypothesis. They are not sourced
IFRS requirements, and this interval is not an IFRS range of permissible reserves.
Its purpose is to demonstrate what those limited constraints do not determine.

If half the first origin stops, its proposed frozen amount is F=rA/2=5+t/2.
Before any release, continuing reserve18-F plus stopped reserveF plus profit2
equals the same instrument gain20. For no later valuation change and immediate
cancellation of the stopped cash flows, release F to profit. Retained reserve
is13-t/2 and total profit7+t/2; their sum is still20 for every t.

| Diagnostic decomposition | Stopped F | Retained after cancellation | Total profit |
| --- | --- | --- | --- |
| rA=10,rB=8 | 5 | 13 | 7 |
| rA=11,rB=7 | 11/2 | 25/2 | 15/2 |
| rA=12,rB=6 | 6 | 12 | 8 |

The same aggregate source amounts and all stated weak constraints thus leave
different downstream releases. This is underdetermination by these inputs and
constraints, not proof that all three are valid accounting histories or that
no additional source-supported rule can select one. A general method still
needs the documented unit, origin/effective-gain history and an applicable rule
for any shared ineffectiveness. Neither independent minima nor a balance plug
provides that missing argument.
