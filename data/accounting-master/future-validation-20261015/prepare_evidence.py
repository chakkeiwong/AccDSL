"""Freeze the documentary baseline and append the inspected scoring source once."""
from pathlib import Path
import json, hashlib, shutil, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
assert not (OUT/'baseline.json').exists()
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert sha(OLD/'accounting-product-proposal.pdf')=='2f827b851470e38a3242bb70a0a106a8ff8c3e9140c1cfa66a71effbc4d97f59'
sources=sorted(p for p in OLD.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark'])
baseline={'candidate':str(OLD.relative_to(ROOT)),'pdf_sha256':sha(OLD/'accounting-product-proposal.pdf'),'source_files':[{'path':str(p.relative_to(OLD)),'sha256':sha(p)} for p in sources],'index_sha256':hashlib.sha256(index).hexdigest()}
write(OUT/'baseline.json',baseline)
(OUT/'sources').mkdir()
shutil.copy2('/tmp/accdsl-gneiting2007.txt',OUT/'sources/gneiting2007.txt')
shutil.copy2('/tmp/accdsl-gneiting2007-crossref.json',OUT/'sources/crossref.json')
m=json.loads((OUT/'sources/crossref.json').read_text())['message']
assert m['DOI'].lower()=='10.1198/016214506000001437'
assert not m.get('update-to') and not m.get('updated-by'), 'Inspect returned notice before using source'
pdf=ROOT/'docs/papers/Strictly Proper Scoring Rules, Prediction, and Estimation Gneiting (2007).pdf'
source={'id':'gneiting2007proper','title':'Strictly Proper Scoring Rules, Prediction, and Estimation','authors':['Tilmann Gneiting','Adrian E. Raftery'],'year':2007,'doi':m['DOI'],'classification':'DIRECT_METHOD','local_path':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'text_path':str((OUT/'sources/gneiting2007.txt').relative_to(ROOT)),'retrieval_url':'https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf','retrieval_date':'2026-10-15','full_text_status':'Retained published article; selected technical, proof, evaluation and appendix passages inspected','inspected_technical_anchors':['4.2 equations20–21, sign orientation and first moment','4.3 equation22; exponent and moment restrictions; exponent2 limitation','4.4 improper predictive model-choice criterion','5.1 Theorem4 proof and examples8–9; external negative-definite-kernel theorem not independently proved','6.1–6.3 quantile/interval construction equation43 and heteroscedastic counterexample','8.1–8.3 weather comparison and evaluation limits','Appendix statistical-depth distinction; no supporting scoring proof imported'],'claims_allowed':['Negative CRPS representation and deterministic absolute-error limit under finite first moment','Energy-score definition and stated proper/strict-propriety conditions attributed to source','Coverage and width alone may favor an inappropriate conditional interval'],'claims_forbidden':['Corporate predictive validity','A confidence-interval method for the nine-issuer panel','Empirical superiority or default selection','Independent verification of every external theorem in the source'],'correction_check':{'source':'Crossref exact DOI 2026-10-15','relation':m.get('relation'),'update_to':m.get('update-to'),'updated_by':m.get('updated-by'),'limit':'No adverse notice returned in these metadata fields; not comprehensive correction clearance'},'official_code_status':'No original-author implementation used; formulas audited directly. Complete official-code search remains not checked.','reading_record':str((OUT/'source-reading.md').relative_to(ROOT))}
write(OUT/'source-support.json',source)
names=['source-support','citation-venue','backward-snowball','forward-snowball','claim-support','omissions']
before=OUT/'six-ledgers-before';before.mkdir()
added={n:[] for n in names}
added['source-support']=[source]
added['citation-venue']=[{'id':source['id'],'date':'2026-10-15','source':'Crossref exact DOI','raw_path':str((OUT/'sources/crossref.json').relative_to(ROOT)),'cited_by_count':m.get('is-referenced-by-count','not available'),'venue':m.get('container-title'),'volume':m.get('volume'),'pages':m.get('page'),'venue_ranking':'not available','limit':'Dated visibility metadata; no validity or comprehensive notice-clearance inference'}]
added['backward-snowball']=[{'seed':source['id'],'date':'2026-10-15','candidates':[{'work':'Matheson and Winkler (1976)','class':'FOUNDATIONAL','action':'Primary CRPS predecessor; not separately inspected, do not attribute a new proof to it'},{'work':'Székely (2003); Berg, Christensen and Ressel (1984)','class':'FOUNDATIONAL','action':'External kernel/strictness dependencies; inspect before an independent proof-certification claim'},{'work':'Dawid and Sebastiani (1999)','class':'COMPETITOR','action':'Moment-based score alternative; retained source says not strictly proper for unrestricted distributions; original not inspected'},{'work':'Gneiting, Balabdaoui and Raftery calibration/sharpness follow-up','class':'DIRECT_METHOD','action':'Relevant calibration design lead; inspect before adopting additional claims'}],'scope':'Relevant method/evaluation references, not an exhaustive bibliography census'}]
added['forward-snowball']=[{'seed':source['id'],'date':'2026-10-15','source':'Exact DOI metadata only','status':'OPEN','result':'No citing-work list was inspected; citation count is not forward screening','next_action':'Inspect calibration/dependence-sensitive and finite-ensemble scoring follow-ups before confirmatory protocol admission'}]
added['claim-support']=[{'id':'r05-crps','class':'SOURCE_RESULT','source':source['id'],'anchor':'4.2 equations20–21','claim':'Negative CRPS equals E|X-y| minus half E|X-Xprime| with independent copies and finite first moment','limit':'No transfer to unweighted sets or unresolved mass'},{'id':'r05-energy','class':'SOURCE_RESULT','source':source['id'],'anchor':'4.3 equation22; 5.1 Theorem4/examples8–9','claim':'Exponent1 energy score evaluates a joint distribution with finite first moments','limit':'No guarantee of finite-panel detection power or independent reproof of cited external theorem'},{'id':'r05-forecast-origin','class':'PROJECT_DEDUCTION','source':'Dated interval ordering','anchor':'future-validation method Information available at the forecast date','claim':'An annual period beginning before an origin includes a nowcast component','limit':'Reporting-period targets remain admissible when honestly labelled'},{'id':'r05-score-arithmetic','class':'PROJECT_DERIVATION','source':'Finite two-point law','anchor':'future-validation E3','claim':'Equal mass on5/7 scores0.5 at5 or6; point6 scores1 or0','limit':'Exact illustration, no empirical ranking'}]
added['omissions']=[{'id':'r05-score-followup-scope','status':'OPEN_SCOPED_SURVEY','title':'Scoring inference, finite ensembles and dependence-sensitive diagnostics','reason':'The inspected scoring definitions do not specify a valid nine-issuer uncertainty procedure or all multivariate power properties','next_action':'Inspect exact inference/finite-ensemble methods when a target and sampling design are selected; no execution admission now','acceptable_for_current_claims':'Definitions/conditions and exact examples only'}]
records=[]
for n in names:
    p=ROOT/'docs/design/research'/f'{n}.json';d=json.loads(p.read_text());shutil.copy2(p,before/p.name)
    assert not any(x.get('id')=='gneiting2007proper' for x in d['records'])
    count=len(d['records']);d['records'].extend(added[n]);write(p,d)
    records.append({'name':n,'before':count,'added':len(added[n]),'after':len(d['records']),'sha256':sha(p)})
write(OUT/'ledger-additions.json',{'records':records,'date':'2026-10-15'})
print(json.dumps({'baseline_sources':len(sources),'source':source['id'],'notice_relations':m.get('relation'),'ledger_additions':{n:len(added[n]) for n in names}}))
