# Repair after the first exact run

Attempt01 passed136 financial, origin, reversal, cadence and refusal checks.
Endpoint inspection found a distinct context defect: all event contexts had to
match, but a consistently wrong opening price currency or risk label could
pass. Add the unit identity price_unit=currency/quantity_unit and enforce this
finite common-price-risk/source-version profile. Preserve attempt01 and rerun
the unchanged authored financial targets with three additional adverse cases.
No numerical, fiscal, valuation or eligibility premise is changed.
