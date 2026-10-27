from pathlib import Path
import hashlib
import json
import shutil

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
BASE=ROOT/'docs/design/proposal/manuscript-rate-interval-propagation-20261017'
NEXT=ROOT/'docs/design/proposal/manuscript-participating-tax-allocation-20261017'
SELECTION=r'''
The official illustrative ordering example provides a useful comparison.
AASB~133 Example~9 orders options, bonds and preference shares by fixed
incremental earnings per share of 0, 1.5 and 4. Options and bonds reduce the
continuing-operations ratio to \(13{,}000{,}000/4{,}020{,}000=650/201\);
adding preferences would raise it to \(970/281\), so they are excluded
\citep[Example~9, pp.~28--30]{aasb133scope2021}. The earnings increments there
do not depend on another assumed conversion. Examples~7 and~12 explain
contingencies, actual conversion dates and the continuing-operations control
number, but do not add a rule for the shared threshold expense above.

Fixed standalone ranking followed by complete recalculation, and ranking by
the next marginal effect, both reject the first conversion in the 80-profit
example. With only two series, these calculations do not distinguish those
ranking policies in general. The inspected examples therefore do not settle
when changing increments should be reordered or a rejected issue reconsidered.
The unresolved selection is kept separate from the correct conditional world
amounts; lower combined EPS alone does not establish an admissible selection.
'''
BIB_ADDITION=r'''

@misc{ifric2017participatingtax,
  author = {{IFRS Interpretations Committee}},
  title = {{IAS 33: Tax Arising from Payments on Participating Equity Instruments}},
  year = {2017},
  url = {https://www.ifrs.org/content/dam/ifrs/supporting-implementation/agenda-decisions/2017/ias-33-tax-arising-from-payments-on-participating-equity-instruments-june-2017.pdf},
  note = {June 2017 agenda decision; complete decision inspected 17 October 2026. Basic earnings allocation and hypothetical-distribution tax consequence; no nonadditive diluted-selection rule}
}

@misc{ifric2017participatingtaxexample,
  author = {{IFRS Interpretations Committee}},
  title = {{Illustrative Example: Tax Arising from Payments on Participating Equity Instruments}},
  year = {2017},
  url = {https://www.ifrs.org/content/dam/ifrs/supporting-implementation/agenda-decisions/2017/ias-33-example.pdf},
  note = {Example accompanying the June 2017 IAS 33 agenda decision. All five pages inspected 17 October 2026, including the benefit-rights qualification and signed third-period reversal}
}
'''
NOTE_ADDITION='. Subsequent reading on 17 October 2026 inspected illustrative Examples 7, 9 and 12 for contingent conditions, additive ordering and period calculations'
TAX_INPUT='\n'+r'\input{sections/participating-tax-allocation}'+'\n'


def main():
    assert not NEXT.exists()
    files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'})
    assert len(files)==139
    records=[]
    for p in files:
        rel=p.relative_to(BASE)
        for dest in (OUT/'baseline-sources'/rel,NEXT/rel):
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        records.append(dict(path=str(rel),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (OUT/'baseline-source-lock.json').write_text(json.dumps(dict(baseline=str(BASE.relative_to(ROOT)),files=records),indent=2)+'\n')
    p=NEXT/'accounting-product-proposal.tex';s=p.read_text();assert s.count('Version 3.38 (proposal candidate)')==1
    p.write_text(s.replace('Version 3.38 (proposal candidate)','Version 3.39 (proposal candidate)'))
    p=NEXT/'sections/dependent-eps.tex';s=p.read_text();anchor='\nThere is a separate, explicit dependency for contingently issuable potential\n'
    assert s.count(anchor)==1;p.write_text(s.replace(anchor,'\n'+SELECTION+anchor))
    p=NEXT/'sections/awards-participation.tex';p.write_text(p.read_text()+TAX_INPUT)
    p=NEXT/'references.bib';s=p.read_text();anchor='no later amendment-chain claim}'
    assert s.count(anchor)==1
    p.write_text(s.replace(anchor,'no later amendment-chain claim'+NOTE_ADDITION+'}')+BIB_ADDITION)
    shutil.copy2(OUT/'participating-tax-allocation.tex',NEXT/'sections/participating-tax-allocation.tex')
    print(json.dumps(dict(version='3.39',protected_sources=len(files),new_sections=1)))


if __name__=='__main__':main()
