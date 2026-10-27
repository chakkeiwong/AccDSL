# Retained units and declared numeric compatibility

All seven unit structures and all 1,127 fact/type/unit joins pass the scoped
checks. The 963 numeric facts have units, including both nil facts; the 164
nonnumeric facts have none. Monetary, shares, pure and per-share source shapes
match their declared types. Complete monetary-unit validity remains unverified
because the required historical currency-code evidence was not inspected.

| Source unit | Exact measure structure | Fact occurrences | Scoped result |
| --- | --- | --- | --- |
| usd | ISO4217-namespace USD | 838 | Monetary shape/namespace pass; historical code validity pending |
| eur | ISO4217-namespace EUR | 5 | Monetary shape/namespace pass; historical code validity pending |
| shares | xbrli:shares | 54 | Declared shares shape matches |
| usdPerShare | ISO4217-namespace USD divided by xbrli:shares | 30 | DTR per-share shape matches; historical code validity pending |
| number | xbrli:pure | 33 | 32 percent facts and one pure fact use the expected unit |
| vendor | Issuer-namespace Vendor | 2 | General integer numeric presence/structure matches |
| subsidiary | Issuer-namespace Subsidiary | 1 | General integer numeric presence/structure matches |

The seven definitions retain numerator and denominator separately, expand each
QName with its element's namespace scope, and preserve product multiplicity.
No measure occurs on both sides of the actual ratio. The reserved instance
namespace is used only for pure and shares. Issuer-defined Vendor and
Subsidiary are retained as distinct measure names; this does not establish a
count ontology, equivalence to pure, or financial aggregation permission.

XBRL requires currency designations that were valid during the fact's context
period, as well as the prescribed namespace and single-measure shape.
Consequently 843 monetary and 30 per-share facts have the explicit result
partial_currency_history_unverified. The fixture with an arbitrary local name
in the currency namespace also remains partial. It demonstrates why this
structural check cannot certify a currency designation. No fabricated registry
entry or current-to-historical extrapolation is used.

The DTR perShare type has a decimal base but adds a monetary-amount-per-share
interpretation. It is therefore checked as a ratio, not misclassified as a
single monetary measure. Both retained DTR percent annotations preserve the
XBRL rule that a reported ratio is not multiplied by100. In the exact authored
example, stored0.25 represents the ratio1/4 and may be presented as25%; storing
25 instead changes the numeric value by100. No actual issuer value was changed
or rendered.

The source schema and its square-feet example allow repeated measures in a
product, despite the opening prose's single-simple-measure wording. A fixture
therefore distinguishes feet squared from feet; converting either product to
a set would be wrong for this representation. A ratio with the same measure
on both sides is rejected under the explicit simplest-form rule. The checker
does not silently cancel source measures to produce a different accepted
representation. Measure identity uses namespace/local name, not prefix spelling.

## Evidence and decision

Eight source spans and nineteen input bindings support the finite account.
All1,207 counted assertions and23 fixtures pass, including1,127 rejected
unit-presence mutations. Each actual unit source slice, declaration/type path,
QName and source/portable side is checked. The two nil numeric facts retain
their units. Numeric status follows the inspected declared type, so seven
numeric-looking strings/years among the unitless facts remain nonnumeric.

| Decision | Primary criterion | Veto status | Main uncertainty | Next justified action | Not concluded |
| --- | --- | --- | --- | --- | --- |
| Accept finite unit/type correspondence | Seven exact structures and1,127 joins | Presence, shape, QName and reserved-name checks pass | Full processor and registry behavior unobserved | Preserve source and candidate values with separate unit interpretations | Full XBRL validity |
| Keep873 currency-bearing results partial | Currency namespace/shape checked | Historical designation requirement unverified | Currency-code validity throughout each context period | Obtain authoritative historical designation evidence under a separate plan | Monetary validity or conversion permission |
| Preserve measure multiplicity and reported ratios | Source examples/rules and exact fixtures support distinctions | Set-deduplication,cancellation and100x shortcuts distinguished | Actual display and accounting meaning unevaluated | Require separate source/presentation/financial mappings | Validity from arithmetic alone |
| Continue program | No protected-state change or global veto | Missing installed acceptance blocks promotion only | Other source/method and independent/domain/human gaps remain | Check numeric precision metadata as a separate source interpretation | Whole-row closure or completedR06 |

The claimed target is finite source measure structure, declared unit presence
and selected type/unit compatibility. The computed quantities match that
bounded target. Complete monetary validity is a different, uncomputed target;
the result explicitly withholds it. Full UTR or filing-specific unit rules,
financial units, conversion rates and rights applicability also remain open.

Commands used standard-library CPU Python, with GPU devices intentionally hidden:

    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-unit-measures-20261020/build_records.py
    CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/r06-unit-measures-20261020/verify.py --check

The manifest records lifecycle commands,commit,environment,elapsed wall time
and output bindings. No new acquisition, upstream execution, installation,
stochastic comparison, ranking or default-policy change occurred.

Post-run challenge: the strongest broader objection is that the declared
currency code was not valid for the context, or that additional registry/
filing rules constrain the generic numeric measures. These possibilities
remain untested and prevent complete validity. A different effective type
chain, source unit or installed parser would require a new source-specific
comparison. No local failure invalidated the data or research direction.

Version3.44 remains396 pages and not_ready. The separate R08 supplement
preserves53 obligations,six interactions and46 operations with zero whole-row
closures. No continuation veto fired.
