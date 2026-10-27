# W05/W06 dated funding and counterparty cash

26 October 2026. MC13/14/17/20/24/25/28/33/34; W05/W06/W16.

Question: does a financing offer accepted by the exact decision reference
produce a jointly feasible date0 cash settlement across the company, old
owner, new holder and investment seller? Compare every complete book,
journal, cash flow, claim/share record and report with independently authored
expected states. Sum counterparty transfers by identity and date; an aggregate
cash total alone cannot establish that each payer can settle.

Use the checked debt-risky/conversion-safe continuation, quote17000/441,
investment60 and owner contribution9460/441. The date is2027-01-01. The
company opens with project asset40, senior liability40 and zero cash/equity;
40 old shares survive. The old owner has cash20 or22 and matching opening
equity. The new holder has cash40 and matching equity. The seller has project
asset60 and matching equity. Those counterparties and their available funds
are new explicit synthetic premises, not evidence about any real party.

The company receives the two financing legs and pays60 to the seller. It
records project asset100, senior40, convertible carrying equal to the supplied
proceeds, owner capital equal to the contribution, new claim face80 and no
new shares yet. The owner records a cost-basis investment equal to its
contribution; the new holder records an investment equal to its payment; the
seller exchanges project60 for cash60. This is a supplied accounting fixture,
not a claim about convertible recognition or fair-value measurement.

Audit: do not use the older maturity-only bond runtime or count a policy quote
as executed funding. Use existing generic typed journal/book methods for the
four books and a bounded joint proposal that returns no accepted bundle
unless all legs and every party's liquidity pass. This is atomic in-memory
proposal validation only, not durable multi-book transaction infrastructure.
Keep rejected diagnostic proposals separate from accepted state.

Primary criterion: exact full-book/journal/report equality on two account
charts, unchanged inputs on refusal, matched payer/payee cash legs, and
claim/carrying/share distinctions. Controls include cash20 refusal, stale
policy or quote, unfunded new holder, wrong date, missing/duplicated transfer,
one-sided cash, wrong face, invented shares and corrupted accepted state.
Rejecting a candidate is expected; comparator or dependency mismatch invalidates
the attempt and triggers repair. Counts/runtime are explanatory.

Defaults: all amounts and dates come from the checked finite case except the
explicit counterparty cash and cost-basis accounting fixtures above. Their
earliest diagnostics are individual cash sufficiency, reciprocal legs and
complete statements. No price is promoted to a reporting standard. Later
measurement and fiscal carry into the2028 conversion opening remain separate;
the work must not silently fill that interval with a no-change assumption.

Budget: three numbered one-shot attempts, five CPU minutes total. Preserve
all successes/failures, source locks and manifests under
data/accounting-master/dated-funding-bundle-20261026/. Use standard-library
Python with CUDA_VISIBLE_DEVICES=-1 and PYTHONDONTWRITEBYTECODE=1. No agents,
commits, installs, GPU, outreach, fees or publication. Governing Version5.19
remains provisional; all broad packages remain open, S6 held and E3 deferred.
