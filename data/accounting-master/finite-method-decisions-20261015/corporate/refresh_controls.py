from pathlib import Path
import hashlib,json,subprocess,shutil,re,platform
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
files=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md',
 'docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pdf=ROOT/'docs/design/proposal/manuscript-corporate-residuals-20261015/accounting-product-proposal.pdf'
newhash='2f827b851470e38a3242bb70a0a106a8ff8c3e9140c1cfa66a71effbc4d97f59'
assert sha(pdf)==newhash
assert all(json.loads((OUT/n).read_text())['passed'] for n in ['independent-checks.json','uncertain-tax-cases.json','manuscript-checks.json'])
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
archive=OUT/'controls-before-r04';assert not archive.exists()
summary=("R03-E's finite corporate repair is integrated in Version 3.00: twelve operating/restoration histories and three tax branches; "
 "559 exact arithmetic/source checks and 111 preservation/build checks pass; eight rendered pages inspected. "
 "Restoration, assurance, mixed contracts, WIP/joint products, deferred supplier terms and uncertain tax have conditional methods. "
 "Result: data/accounting-master/finite-method-decisions-20261015/corporate/result.md. "
 "Required remaining design is explicit in corporate/residual-disposition.md and ../residual-followup.md; R03/P17 remain open.")
nexttext=("Next: execute R04 under docs/plans/accounting-consequential-literature-20261015.md; then ready R05 future validation protocols "
 "and R06 reuse locks, while resolving the named R03 design residuals before R07/R08. Runtime execution remains held.")
updates={}
for n in files:
 s=(ROOT/n).read_text().replace('manuscript-group-bindings-20261015/accounting-product-proposal.pdf','manuscript-corporate-residuals-20261015/accounting-product-proposal.pdf')
 s=s.replace('393f4cf191a44ac8e671248a6c10562674d5c5a03a3a42e4f60c30b8c10e70e8',newhash)
 for a,b in [('Version **2.99**, 294','Version **3.00**, 298'),('Version 2.99, 294','Version 3.00, 298'),('current Version 2.99 candidate','current Version 3.00 candidate'),('through 2.99','through 3.00'),('2.73–2.99','2.73–3.00')]:s=s.replace(a,b)
 s=re.sub(r'Next: execute R03-E[^\n]*',nexttext,s)
 s=s.replace('## Group bindings and next work — 15 October 2026','## Corporate methods and next work — 15 October 2026\n\n'+summary+'\n\n'+nexttext+'\n\n## Group bindings — 15 October 2026',1)
 assert summary in s;updates[n]=s
n='data/accounting-master/finite-method-decisions-20261015/decisions.md'
s=(ROOT/n).read_text();s=s.replace('Active; no blanket private-facts disposition','Finite audit delivered3.00;559 checks; corporate/result.md. Required design remains in residual-followup.md');updates[n]=s
n='data/accounting-master/p17-completion-20261014/P17-04/operation-matrix.md'
s=(ROOT/n).read_text().replace('Refreshed through Version 2.93','Refreshed through Version 3.00')
s+='\nVersion3.00 delivers restoration, historical AU assurance, mixed modifications, WIP/joint products, supplier financing and uncertain-tax finite methods. The controlling detailed disposition is ../../finite-method-decisions-20261015/corporate/residual-disposition.md; required remaining methods stay open. Next R04 reconciles consequential claims before the named R03 follow-up repairs.\n';updates[n]=s
for n,s in updates.items():
 p=archive/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,p);(ROOT/n).write_text(s)
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
(OUT/'control-refresh.json').write_text(json.dumps({'before':{n:sha(archive/n) for n in updates},'after':{n:sha(ROOT/n) for n in updates},'next':nexttext,'index_preserved':True},indent=2)+'\n')
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'environment':{'python':platform.python_version(),'CPU':'exact documentary fractions; no frameworks','GPU':'N/A; no GPU operation'},
 'random_seeds':'N/A; no simulation','data_version':'source-manifest.json and protected2.99 predecessor',
 'plan':'docs/plans/accounting-corporate-residual-decisions-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),
 'candidate_pdf':str(pdf.relative_to(ROOT)),'candidate_pdf_sha256':newhash,
 'commands':['python3 data/accounting-master/finite-method-decisions-20261015/corporate/'+x+'.py' for x in ['build_cases','verify_cases','check_uncertain_tax','prepare_manuscript','repair_presentation','finish_equations','verify_manuscript','refresh_controls']],
 'document_command':'python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-corporate-residuals-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/corporate --timeout 240 --force',
 'render_command':'python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-corporate-residuals-20261015 --evidence data/accounting-master/finite-method-decisions-20261015/corporate/accepted-final --pages 1,111,116-121 --dpi 110',
 'build_executions':7,'wall_time':{'final_build_seconds':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'interactive_total':'not measured'},
 'output_artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(OUT.glob('*')) if p.is_file() and p.name!='run-manifest.json'],
 'index_preserved':True,'no_commit':True}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'version':'3.00','controls':len(files),'index_preserved':True,'next':'R04'}))
