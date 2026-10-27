from pathlib import Path
import hashlib,json,subprocess
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text())
a=json.loads((OUT/'cases.json').read_text())
r=json.loads((OUT/'render-v2/render-manifest.json').read_text())
assert c['passed'] and a['passed'] and c['count']==119 and a['count']==73
pdf=ROOT/'docs/design/proposal/manuscript-group-restatement-20261015/accounting-product-proposal.pdf'
assert sha(pdf)==c['pdf_sha256']==r['pdf_sha256']
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert (OUT/'result.md').exists()
next_plan='docs/plans/accounting-corporate-cohorts-funding-20261015.md'
assert (ROOT/next_plan).exists()
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
next_line=f'Next: opening production cohorts, pension funding and restoration cash under {next_plan}; remaining methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.'
section='''## Group joins, restatement and exchangeability — 15 October 2026

R03-K is integrated in Version 3.09, 326 pages. Seven groups pass 73 exact checks; 119 preservation/build checks and six final pages were inspected. Result: data/accounting-master/group-restatement-exchangeability-20261015/result.md. Reporting-date balance elimination is distinguished from transaction control intervals; inflation, tax opening and dated exchangeability procedures remain conditional. Closed profiles and full readiness remain open.

'''+next_line+'\n\n'
before=OUT/'controls-before-corporate-cohorts'; before.mkdir(); records=[]
for rel in paths:
 p=ROOT/rel; s=p.read_text(); (before/p.name).write_bytes(p.read_bytes()); h=sha(p)
 s=s.replace('Version **3.08**, 322 pages','Version **3.09**, 326 pages')
 s=s.replace('docs/design/proposal/manuscript-insurance-treaty-changes-20261015/accounting-product-proposal.pdf',str(pdf.relative_to(ROOT)))
 s=s.replace('461ae8c011e7384379a2943b9c158877b47b417475a3a8652a288bd634c5fc96',c['pdf_sha256'])
 s='\n'.join(next_line if line.startswith('Next: group elimination') else line for line in s.split('\n'))
 i=s.index('\n## '); s=s[:i+1]+section+s[i+1:]; p.write_text(s)
 records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:
 f.write('\n## Progress 15 October 2026 through Version 3.09\n\nR03-K adds exact group joins, hyperinflation/tax/translation and dated exchangeability methods. See group-restatement-exchangeability-20261015/result.md. Actual facts and closed successor exchanges remain. '+next_line+'\n')
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,192,193,194,195,196],'render_manifest':'render-v2/render-manifest.json','review':'Scoped author inspection of final pages; control-date explanation and prose-number spacing repaired. Human comprehension pending.'},indent=2)+'\n')
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==idx
manifest={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-group-restatement-exchangeability-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':326,'commands':['check_cases.py','prepare_manuscript.py (once)','accounting_document_tools.py build','accounting_document_tools.py render (render-v2 final)','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only; no GPU detection or framework imports','data_version':'Retained EU2023/1803 and EU2024/2862; seven synthetic groups','random_seeds':'N/A: deterministic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':73,'manuscript':119},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready','next_plan':next_plan}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'version':'3.09','controls':6,'checks':manifest['checks'],'index_preserved':True,'next_plan':next_plan}))
