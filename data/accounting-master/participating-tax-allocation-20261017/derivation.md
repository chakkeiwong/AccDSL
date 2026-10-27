# Participating dividend tax: derivation and source boundary

Primary support: the complete June 2017 IFRS Interpretations Committee IAS 33
participating-equity tax decision and its five-page example, retained under
`../dependent-eps-source-selection-20261017/`. IAS 33.A14 and the interpretation
require ordinary holders' share of hypothetical-distribution tax benefits in
basic EPS, independently of the accounting recognition location of actual
benefits. The source's printed Steps 1–3 are the reference algorithm.

Let P be current profit before the participating-dividend tax benefit, r the
participating-to-ordinary base-distribution ratio, t the tax rate, n the
positive weighted-average ordinary denominator, and D the actual base dividend.
Set a=r/(1+r), b=1/(1+r). Supplied rights assign all tax benefits to ordinary
holders. Actual class dividends are Dp=aD, Do=bD and H=tDp. The source profile
distributes the entire actual benefit H to ordinary holders in the same period.
Opening undistributed base profit U funds prior-year distributions; require
P>=0, U>=0, D>=0 and U+P-D>=0. This is an accounting-allocation example, not a
legal distribution-capacity determination or general loss-DTA method.

Reported profit Y is P+H if the actual benefit is recognized in profit, and P
if it is recognized directly in equity. Step 1 adjusts to G=P+H in both cases,
then subtracts every declared dividend:

    R = G - Dp - Do - H = P - D.

Step 2 allocates the signed remaining base profit as aR and bR. Ordinary holders
also receive the hypothetical tax adjustment t*aR. R can be negative when the
current payout includes earlier earnings. That negative adjustment prevents
counting a prior hypothetical benefit again; it is not a negative cash dividend
or a newly inferred loss-tax recognition entry.

Step 3 adds declared and hypothetical allocations:

    ordinary N = Do + H + bR + t*aR,
    participating M = Dp + aR,
    basic EPS = N/n.

Substitute Dp=aD, Do=bD, H=taD and R=P-D:

    N = bD + taD + (b+ta)(P-D) = (b+ta)P,
    M = aD + a(P-D) = aP,
    N+M = P + taP = G + taR.

These are local algebraic deductions from the specified rights and the source
procedure. The direct formula provides an independent check of the multi-step
calculation and makes the timing invariance explicit. Total EPS allocations
include a hypothetical tax amount and need not equal reported accounting profit.
They must not be posted as a tax asset, dividend, reserve or profit adjustment.

Published r=10, t=3/10, P=(330,550,110), D=(0,330,660) gives R=(330,220,-550),
H=(0,90,180), residual tax=(90,60,-150), N=(120,200,40), M=(300,500,100).
With U initially zero, the closing base balances are (330,550,0). The ordinary
denominator 100 in local fixtures is an authored convenience; the source
specifies numerators, not this share count.

The zero-tax case reduces to N=bP. With r=0, N=P. Paying no dividend and paying
the full current base dividend give the same N. Full historical payout may
make R negative but still leaves N=(b+ta)P. None of these deductions establishes
arbitrary benefit-sharing, capped/senior terms, changing rights, current legal
applicability, actual tax recognition, or nonadditive diluted selection.

The earlier CappedParticipationEPS/1 requires fixed supplied after-tax earnings
and excludes other attribution. Its results do not calculate this additional
tax effect. Do not feed a participating instrument with unrepresented deductible
distributions to that method under its simplifying findings. Its frozen evidence
is preserved; this separate contract represents the newly inspected mechanism.
