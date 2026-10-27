# Exact conditional inverse of nearest rounding with ties to even

Let d be an integer decimal-place count and q=10^(-d)>0. Define R_q(x) to
choose the nearest integer multiple of q, with a tie assigned to the multiple
whose integer coefficient is even. This definition is the local mathematical
map checked here. It does not assert that the issuer produced every fact by
applying this map to an underlying economic quantity.

Suppose the reported rational v is kq for an integer k. For
v-q/2<x<v+q/2, v is the unique nearest grid value. Outside the closed interval,
one of the adjacent multiples is strictly closer, so R_q(x) differs from v.
At v-q/2, the tied coefficients are k-1 and k; at v+q/2, they are k and k+1.
If k is even, both ties choose k. If k is odd, both choose an adjacent even
coefficient. Therefore:

    R_q^-1({v}) = [v-q/2, v+q/2]  when k is even;
    R_q^-1({v}) = (v-q/2, v+q/2)  when k is odd.

The argument applies to negative k and zero without changing signs or tie
rules. In particular a single half-open interval is not the exact inverse of
this rounding map. A conservative closed enclosure remains an enclosure when
the tie rule is unknown, but it need not be the exact feasible set.

If v/q is not an integer, v is not in the range of R_q. The exact inverse
of that map would be empty. The record instead withholds an observation-set
interpretation because the source may contain additional lexical digits and
the selected source examples discuss discarding them. Choosing that different
reported representative requires a separate rule; source evidence is not
silently changed to make the precondition hold.

The checker computes q, endpoints and membership using exact Fractions. A
separate Decimal ROUND_HALF_EVEN quantization with adequate explicit context
checks the center, both endpoints, two strictly interior points and two
strictly exterior points for every constructed finite set. These finite
checks validate the code against the derivation; the algebra above supplies
the general parity argument. They establish no stochastic uncertainty model
or actual financial measurement process.
