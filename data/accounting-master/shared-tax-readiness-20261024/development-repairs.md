# Focused development repairs

The first evaluator smoke check failed with fields:dimensional_type. The new
adapter had supplied v1 rational declarations to the v3 evaluator. The existing
v2/v3 contract requires explicit dimensions and scale. The adapter now represents
money in currency:USD at unit scale and rates as dimensionless rationals. The
frozen evaluator and original methods were not changed. An arbitrary 100% rate
cap was also removed; the finite information check only excludes negative rates.

The first focused suite ran ten methods and found one wrong test expectation:
it expected fully terminated right B to disappear from closing memory. The
native lease kernel retains B with zero ROU and liability. The test now checks
those exact balances and still requires B's tax declarations. This repairs the
test's assumption, not the original state. The assessor collects opening and
all completed states and never selects rights by positive closing balance.
Neither failure provides evidence against the original native tax controls.
