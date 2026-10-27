# Positive carrying weights do not select a unique all-zero reversal

This is a local mathematical deduction about the existing proposed capped
allocator. It does not supply an interpretation of IAS 36 at zero carrying
amounts. The two retained source inquiries establish only their historical
wording and examples; neither gives this limiting argument.

Suppose m eligible non-goodwill assets have fixed restoration ceilings C_i>0.
Fix a desired final carrying total T with 0<T<=C=sum C_i. A positive starting
vector b satisfies 0<b_i<C_i and B=sum b_i<T. The requested reversal is T-B,
and each capacity is C_i-b_i. Keeping that relationship matters: perturbing
the starting balance while keeping the reversal unchanged changes the final
target. All quantities here are supplied hypothetical amounts. Admissibility
of the assets, ceilings, recovery and unit of account is not proved.

The existing method uses original carrying weights b_i on the remaining active
assets. It allocates the residual reversal pro rata, fixes any asset whose
proposed increase exceeds its capacity, removes it, and repeats. Write F for
the fixed assets and A for the active ones. Fixed assets end at C_i. The still
required increase is

    Q_A = T - sum_{i in F} C_i - sum_{i in A} b_i.

The pro-rata proposal for an active asset is b_i Q_A / sum_{j in A} b_j.
Adding its original balance gives

    b_i + b_i Q_A / sum_{j in A} b_j
      = b_i (T - sum_{j in F} C_j) / sum_{j in A} b_j
      = lambda_A b_i.

Thus a pass fixes precisely the assets with lambda_A b_i>C_i. After removing
such a group S, the new multiplier cannot decrease: their total ceiling is
strictly less than lambda_A sum_{i in S} b_i, so the residual final total per
remaining weight increases. Every previously fixed asset therefore also
satisfies lambda_final b_i>=C_i. If no proposed increase exceeds its capacity,
the remaining proportional split exactly supplies Q_A and terminates. Each
strict pass removes at least one asset. Feasibility T<=sum C_i prevents all
assets from being removed while a positive unsupplied reversal remains.

Consequently the final vector is

    F_i(b) = min(C_i, lambda b_i),       sum_i F_i(b) = T.             (1)

For T<C, the sum of these terms is continuous and strictly increasing in
lambda while any asset is unsaturated, starts at B<T when lambda=1, and reaches
C. There is exactly one multiplier achieving T. For T=C any sufficiently
large multiplier works, but the final vector is uniquely C_i. This proves the
characterization for the stated algorithm; it is not an invocation of an
uninspected optimization solver or a new allocation default.

Now let b approach the all-zero vector through the positive domain, retaining
the same C_i and T. Every F(b) lies in the closed bounded set

    A(C,T) = {x : 0<=x_i<=C_i for every i, and sum_i x_i=T}.          (2)

Every convergent subsequence therefore has its limit in A(C,T). This supplies
one inclusion for the set of possible limits, but does not yet show that the
ordinary positive-weight rule can approach every cap-compatible vector.

For the other inclusion first take 0<T<C and an arbitrary x in A(C,T). Define
z_i=T C_i/C. Then 0<z_i<C_i and sum z_i=T. For 0<epsilon<1 put

    y_i(epsilon) = (1-epsilon)x_i + epsilon z_i,
    b_i(epsilon) = epsilon y_i(epsilon).                            (3)

Every y_i is strictly between zero and C_i, sums to T, and tends to x_i.
Every b_i is positive, smaller than C_i, tends to zero and sums to epsilon T.
The requested reversal is (1-epsilon)T. Its proportional increase for asset i
is (1-epsilon)y_i, which does not exceed capacity C_i-epsilon y_i because
y_i<C_i. No cap clips this construction. Equivalently, (1) with
lambda=1/epsilon gives F_i(b(epsilon))=y_i(epsilon). Hence F(b(epsilon)) tends
to x. This argument includes target vectors x with zero components or binding
caps; the mixture z keeps every finite starting weight strictly positive.

For T=C, (2) contains only x_i=C_i. The path b_i=epsilon C_i approaches zero
and the allocator ends exactly at C_i. Combining both cases, the set of all
attainable limits is precisely A(C,T). This is a characterization of a set of
mathematical limits, not a probability distribution or the set of accounting-
admitted outcomes.

If m>=2 and 0<T<C, the interior vector z can be perturbed by adding a small
delta to one component and subtracting it from another. Choose positive delta
smaller than both components' distances to their two bounds. Both resulting
vectors are in A(C,T) and are distinct. By (3) both are attainable limits.
There is therefore no path-independent continuous extension of this allocator
at the all-zero carrying vector in that domain. Assigning zero, equal weights,
capacity weights or an arbitrary epsilon does not follow from continuity.

For example C_1=C_2=10 and T=6. Along b=epsilon(3,3), equation (1) gives
F(b)=(3,3) for every 0<epsilon<1. Along b=epsilon(1,5), it gives (1,5).
Both starting vectors approach (0,0), but the final vectors stay two units
apart in each component. Their reversal totals are both 6(1-epsilon).
Numerically smaller perturbations cannot eliminate this difference.

The singleton cases are distinct. If m=1, (2) contains only x_1=T. If T=C,
it contains only the ceiling vector. At T=0 the boundary constraints contain
only zero, but no positive b satisfies B<T, so this is not a positive-reversal
limit covered by (1). Assets with C_i=0 can be removed from the perturbed set
and retained at zero; they must not receive invented positive starting values.
T>C is outside the exact-total theorem and retains the existing explicit
capacity-shortfall treatment. Mixed zero/nonzero starting vectors, changing
ceilings, quantized rounding and different allocation procedures are not proved
by this argument.

This result rules out a particular proposed repair: obtaining a canonical
all-zero allocation solely by continuity of the existing positive-weight rule.
It does not rule out recovery, prove zero reversal, choose an alternative rule,
or establish IAS 36 authority even in a singleton case. Those conclusions
require the missing accounting premises or an applicable technical treatment.
