# Accuracy metadata and conditional rounding sets

All1,127 retained facts satisfy the scoped accuracy-attribute rules. The961
non-nil numeric facts each have decimals and no precision. The two nil numeric
facts and164 nonnumeric facts have neither. Sixteen numeric facts assert
decimals=INF;945 have finite decimals. Every finite reported rational lies on
its indicated decimal grid, so no actual inverse construction was withheld.
These results preserve the source accuracy assertions; they do not validate
the underlying reported amounts.

For each finite decimals value d, the separate step is q=10^(-d). The reported
rational v is unchanged; q is not a multiplier applied to v. Under the explicitly
conditional nearest-rounding map with ties to even, write v=kq. The exact
preimage includes both endpoints v±q/2 when k is even and excludes both when
k is odd. The derivation and implementation distinguish this set from an
assumption-free financial observation constraint.

There are514 even-grid and431 odd-grid values among the945 finite records.
These are descriptive counts. Every conditional set is checked at seven
points—center, both endpoints, two interior and two exterior—using exact
rational rounding and a separate Decimal ROUND_HALF_EVEN implementation.
All6,615 actual-value comparisons pass;63 further fixture comparisons cover
zero,negative values,fractional steps and large decimal-place steps.

The corrected XBRL definition of “correct to n decimal places” invokes nearest
rounding with ties to even. Its illustrative GE/LT columns and examples with
extra lexical digits do not justify identifying every reported fact with an
output of this particular map. Two authored off-grid examples,10.009 with
decimals2 and-205 with decimals-2, therefore retain their original values and
withhold an observation-set interpretation. Mathematically the stated map has
no preimage for either unmodified value; choosing a different representative
would be a different policy. No such policy was needed for the actual945
finite records.

INF is recorded as the source's assertion that the represented value is exact.
It is not proof that accounting recognition, measurement or economic reality
is exact. Nil stays nil and receives no numeric interval. Precision lexical/
presence fixtures cover0,-0,INF and invalid forms, but no precision-to-decimals
inference is implemented because no actual precision attribute occurs.

## Evidence and decision

Eight technical/schema spans and eleven input bindings preserve the source,
type classification and rational comparator. The one-time check reports1,210
counted assertions,17 metadata fixtures,13 rounding fixtures and1,127 rejected
accuracy-attribute mutations, in addition to the6,678 exact rounding comparison
points. Actual source spans,attributes and frozen rational candidates are
checked separately in the construction/replay guards.

| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept metadata account |1,127 exact records satisfy presence/type/nil rules | Both-attribute,missing,prohibited and lexical controls distinguish failures | Full XBRL processor behavior unobserved | Preserve raw attributes and candidate values | Whole-filing validity |
| Accept conditional inverse derivation |945 grid-aligned values;exact endpoint checks pass | No actual off-grid value;authored off-grid inverses withheld | Actual issuer measurement/rounding process not established | Keep conditional map separate from financial admission | Exact feasible financial-history sets |
| Reject generic half-open ties-even inverse | Parity determines both endpoints | Positive/negative/zero fixtures pass | Other declared tie rules have different preimages | Require explicit rounding convention before admission | That all half-open illustrative intervals are wrong |
| Continue program | No source or protected-state veto | Missing installed/human evidence blocks its dependent claims only | Full dimensional/calculation/source-currency and independent acceptance gaps remain | Reconcile residual native-validation duties and choose next distinct check | Whole-row closure or program completion |

The claimed target is source metadata consistency and an exact inverse under a
stated mathematical rounding map. Those are the quantities computed and
supported. An actual issuer observation process and an admitted financial
constraint are different targets and remain unevaluated. No confidence
interval, stochastic uncertainty distribution,V-Equals or calculation-link
validity follows from these sets.

The current manuscript already ties interval endpoints to a declared rounding
convention and allows a conservative closed enclosure when that convention is
unknown. This inquiry finds no confirmed contradiction requiring a rebuild.

Executed in standard-library CPU Python,with GPU devices intentionally hidden:

    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-numeric-accuracy-20261020/build_records.py
    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-numeric-accuracy-20261020/verify.py --check

The manifest records git commit,lifecycle commands,environment,elapsed wall
time and output bindings. No new acquisition,upstream runtime,installation,
empirical comparison,ranking or default-policy change occurred.

Post-run challenge: the strongest alternative is that the source accuracy
assertion or the actual reporting process differs from the conditional
nearest/ties-even map. That would change financial interpretation without
changing the preserved metadata. A changed source rational,decimals token or
declared type would require a new local record. The source's illustrative
accuracy tables remain a reason to keep this mathematical map conditional.

Version3.44 remains396 pages and not_ready,with53 obligations,six interactions
and46 operations. The additiveR08 supplement closes zero whole rows. No result
invalidated the harness,data,target or research direction; no continuation
veto fired.
