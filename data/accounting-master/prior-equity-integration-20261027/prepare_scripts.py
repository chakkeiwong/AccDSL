"""Generate a new integration writer without modifying any frozen predecessor."""
from pathlib import Path
H=Path(__file__).resolve().parent
p=H/'integrate.py';assert not p.exists()
s=(H.parent/'upstream-carry-integration-20261027/integrate.py').read_text()
def replace(old,new):
    global s
    assert old in s,old
    s=s.replace(old,new)
replace("S=R/'docs/design/proposal/manuscript-intragroup-upstream-v534-20261027'", "S=R/'docs/design/proposal/manuscript-upstream-carry-v535-20261027'")
replace("T=R/'docs/design/proposal/manuscript-upstream-carry-v535-20261027'", "T=R/'docs/design/proposal/manuscript-prior-equity-v536-20261027'")
replace('611d83759a0e4d5ba757753613e957aa7364e48cf516ec91fc5b2ee0a52df34d','bff99bcae8c29268fd29497c4b5cbb2de5d1bd528bd4b4c20fbb3ac783e69fb8')
replace('5f0352b476ee76236157975f2cc04634ab43408ee7f2184f22771b536464b0dc','9c3ecdc06aa94a5772688e0ad57dfe1d86bfb70f356c579885ae30b55ef4f56d')
replace('upstream-carry.tex','prior-equity.tex')
replace("'simulation/26-finite-finance.tex']","'simulation/26-finite-finance.tex','references.bib']")
replace("assert t.count('Version 5.34')==1;return t.replace('Version 5.34','Version 5.35')", "assert t.count('Version 5.35')==1;return t.replace('Version 5.35','Version 5.36')")
replace('input{simulation/upstream-carry}','input{simulation/prior-equity}')
replace("if n=='references.bib':return t", "if n=='references.bib':\n        assert 'aasb128prior2025' not in t;return t+(H/'bibliography-addition.bib').read_text()")
replace("startswith('5.34;')","startswith('5.35;')")
replace("['acquisition-intragroup-upstream-carry-20261027']", "['acquisition-prior-interest-20261027','acquisition-prior-interest-scope-20261027','acquisition-prior-worksheet-20261027']")
replace("[('acquisition-intragroup-upstream-carry-20261027','attempt-01')]", "[(x,'attempt-01') for x in ['acquisition-prior-interest-20261027','acquisition-prior-interest-scope-20261027','acquisition-prior-worksheet-20261027']]")
replace("['prior-equity.tex','reader-plan.md']", "['prior-equity.tex','reader-plan.md','bibliography-addition.bib']")
replace('accounting-upstream-carry-integration-20261027.md','accounting-prior-equity-integration-20261027.md')
replace("'Version 5.35' in texts[0]", "'Version 5.36' in texts[0]")
replace("title='Acquiring control changes the measurement and the period';ending='distinguished before the same consolidation logic can be applied.'", "title='An investment already held before control';ending='That distinction determines the next extension of the financing example.'")
replace('At the first upstream year end, suppose the parent still holds the whole lot.','An investor may already own shares when it obtains control of a business.')
replace("['subsidiary','retained','inventory','tax','NCI','accounts']", "['significant influence','joint control','noncash','remeasurement','FVOCI','NCI','120']")
assert 'Version 5.34' not in s
p.write_text(s)
print('Created integrate.py only; no preparation or build rerun.')
