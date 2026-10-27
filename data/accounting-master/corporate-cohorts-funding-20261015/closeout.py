from pathlib import Path
import hashlib,json,subprocess
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text())
a=json.loads((OUT/'cases.json').read_text())
r=json.loads((OUT/'render-v3/render-manifest.json').read_text())
assert c['passed'] and a['passed'] and c['count']==121 and a['count']==58
pdf=ROOT/'docs/design/proposal/manuscript-corporate-cohorts-20261015/accounting-product-proposal.pdf'
assert sha(pdf)==c['pdf_sha256']==r['pdf_sha256']
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
assert (OUT/'result.md').exists()
next_plan='docs/plans/accounting-financing-modifications-net-hedges-20261015.md'
assert (ROOT/next_plan).exists()
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
next_line=f'Next: amendment dates, award modifications and group/net hedges under {next_plan}; remaining methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.'
section='''## Opening production, pension funding and restoration cash — 15 October 2026

R03-L is integrated in Version 3.10, 329 pages. Six groups pass 58 exact checks; 121 preservation/build checks and five final pages were inspected. Result: data/accounting-master/corporate-cohorts-funding-20261015/result.md. FIFO/average opening work, abnormal loss and pension availability/funding are explicit. The restoration cash classification remains a provisional interpretation with its competing consequence retained. Closed profiles and full readiness remain open.

'''+next_line+'\n\n'
before=OUT/'controls-before-financing-modifications'; before.mkdir(); records=[]
for rel in paths:
 p=ROOT/rel; s=p.read_text(); (before/p.name).write_bytes(p.read_bytes()); h=sha(p)
 s=s.replace('Version **3.09**, 326 pages','Version **3.10**, 329 pages')
 s=s.replace('**Version 3.00, 298 pages.**','**Version 3.10, 329 pages.**').replace('Versions 2.73–3.00 add scoped','Versions 2.73–3.10 add scoped').replace('Integrations delivered through 3.00','Integrations delivered through 3.10')
 s=s.replace('docs/design/proposal/manuscript-group-restatement-20261015/accounting-product-proposal.pdf',str(pdf.relative_to(ROOT)))
 s=s.replace('c4eba8f000c9489a3cbdf798b05cd7997626923a59be21cbdf81b95cf6616d61',c['pdf_sha256'])
 s='\n'.join(next_line if line.startswith('Next: opening production cohorts') else line for line in s.split('\n'))
 i=s.index('\n## '); s=s[:i+1]+section+s[i+1:]; p.write_text(s)
 records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:
 f.write('\n## Progress 15 October 2026 through Version 3.10\n\nR03-L adds opening production cohorts, normal/abnormal losses, pension funding and conditional restoration cash methods. See corporate-cohorts-funding-20261015/result.md. Actual facts and closed successor exchanges remain. '+next_line+'\n')
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,124,125,126,127],'render_manifest':'render-v3/render-manifest.json','review':'Scoped author inspection of final pages; subsection hierarchy and prose-number spacing repaired. Human comprehension pending.'},indent=2)+'\n')
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==idx
manifest={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-corporate-cohorts-funding-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':329,'commands':['check_cases.py','prepare_manuscript.py (once)','accounting_document_tools.py build','accounting_document_tools.py render (render-v3 final)','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only; no GPU detection or framework imports','data_version':'Retained EU2023/1803 and dated nonbinding staff papers; six synthetic groups','random_seeds':'N/A: deterministic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':58,'manuscript':121},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready','next_plan':next_plan}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'version':'3.10','controls':6,'checks':manifest['checks'],'index_preserved':True,'next_plan':next_plan}))
