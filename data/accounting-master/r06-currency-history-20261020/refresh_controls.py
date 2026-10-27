"""Advance four live controls without rewriting completed source evidence."""
from pathlib import Path
R = Path(__file__).resolve().parents[3]
old = """Next: audit the independent historical-currency duty left by the completed
seven-unit inquiry. Inspect authoritative maintenance-agency sources and exact
fact periods; current code membership alone cannot establish past validity.
Keep all873 currency-bearing results partial until date-supported evidence
exists. Preserve the56-fragment structural result and source/projection
distinction. Full XHTML/DTR/schema validity,installed correspondence and build
identities remain."""
new = """The R06 currency-source inquiry is complete at
data/accounting-master/r06-currency-history-20261020/: eight official sources,
13 anchors,48 bindings and989 checks bind873 facts,143 contexts and ten period
forms. Two EUR facts reach30August2016. Current lists lack inception fields;
the historical EUR withdrawal is territory-specific. Amendment94 distinguishes
1997 code issuance from1999 adoption;158 removesUSS,notUSD;160 changes country
names. The index reaches179 while the page names180. All873 historical results
remain partial; no currency invalidity,full validation or whole-row closure.
Four rendered pages and complete five-page text reads support the source account.

Next: recover the Calculations1.1 normative schema from the exact publication
URL whose earlier trusted request timed out. Preserve that failed receipt and
the explicitly non-normative appendix copy; compare actual declarations and
imports if recovery succeeds. No old/new calculation adoption or rounding
policy is selected by source recovery. Historical currency intervals,full
XHTML/DTR/schema validity,installed correspondence and build identities remain."""
names = ['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
         'docs/plans/accounting-mission-requirements.md','data/accounting-master/next-plan.md']
texts = {name:(R/name).read_text() for name in names}
assert all(value.count(old)==1 for value in texts.values())
for name,value in texts.items():
    (R/name).write_text(value.replace(old,new))
print('Updated four live controls; 873 historical results remain partial.')
