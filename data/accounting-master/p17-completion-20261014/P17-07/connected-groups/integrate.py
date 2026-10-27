"""Integrate a section and repair one stale inherited claim."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[5]; OUT=Path(__file__).resolve().parent
NEW=ROOT/'docs/design/proposal/manuscript-insurance-connected-groups-20261014'
p=NEW/'sections/insurance-methods.tex';s=p.read_text()
anchor=r'\hypertarget{paa-reinsurance-and-valuation-methods}{%'
assert s.count(anchor)==1
s=s.replace(anchor,'\\input{sections/insurance-connected-groups}\n\n'+anchor)
p.write_text(s)
p=NEW/'sections/bank-methods.tex';s=p.read_text()
old='No binding capital-policy numbers have been inspected for a target bank here. Use the Basel/national source and actual bank facts before real admission.'
new='Selected dated US national capital rules are inspected in the surrounding bank inquiry. A connected accounting-to-capital reconciliation for the same bank still requires its applicable perimeter, eligibility, deductions and exposure facts; the illustrative inputs above do not supply those facts.'
assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
(OUT/'content-dispositions.json').write_text(json.dumps({'new_section':'sections/insurance-connected-groups.tex','modified':['accounting-product-proposal.tex','sections/insurance-methods.tex','sections/bank-methods.tex'],'bank_repair':{'removed':old,'replacement':new,'reason':'Blanket absence statement became stale after selected OCC/Fed inquiries; actual connected prudential case still open'},'no_equation_or_source_removed':True},indent=2)+'\n')
src=ROOT/'data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/verify_candidate.py'
v=src.read_text().replace('2.82 supplement','2.83 supplement').replace('{"accounting-product-proposal.tex","sections/bank-methods.tex","references.bib"}','{"accounting-product-proposal.tex","sections/insurance-methods.tex","sections/bank-methods.tex"}').replace('{"sections/bank-commitment-draw.tex"}','{"sections/insurance-connected-groups.tex"}')
(OUT/'verify_candidate.py').write_text(v)
txt=ROOT/'docs/design/research/standards/aasb17.txt';pages=txt.read_text().split('\f')
selected=[1,8,9,10,11,12,13,14,15,16,17,19,20,21,44,45,52,53,54]
(OUT/'selected-source-pages.txt').write_text('\n\n'.join('PHYSICAL PAGE '+str(i)+'\n'+pages[i-1] for i in selected))
p=OUT/'source-manifest.json';m=json.loads(p.read_text());m['physical_pages_retained']=selected;p.write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'integrated':True,'modified':3,'new_sections':1,'stale_bank_claim_repaired':True}))
