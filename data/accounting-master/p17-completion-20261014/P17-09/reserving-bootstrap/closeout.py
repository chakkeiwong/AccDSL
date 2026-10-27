from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[5];O=Path(__file__).resolve().parent;N=chr(10)
A=R/'data/accounting-master/p17-completion-20261014/control-refresh-13'
cs=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
assert not A.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={}
for n in cs:
 p=R/n;q=A/'before'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);before[n]=sha(p)
summary='P17-09 reserving uncertainty is delivered in Version2.85:46 exact and85 preservation/build checks pass; seven rendered pages inspected. Two-stage prediction, process-law identity, shared-fit dependence, sparse-data refusal and one-year re-estimation are specified. All six literature ledgers retain their historical records. Result: data/accounting-master/p17-completion-20261014/P17-09/reserving-bootstrap/result.md. P17/E07/E08 remain open.'
next_text='Next: audit the retained Steinmetz/Jentsch arXiv2303.05913v1 (10 March2023; published2024 record) for bootstrap consistency. Refresh the exact target, assumptions, comparator, theorem/proof dependencies and available author code before importing any validity or failure conclusion. No stochastic campaign starts.'
for n in cs:
 p=R/n;s=p.read_text()
 for a,b in [('12979f23fbac7ea69d3b2fe55917e8fd6a1a4e3d15243c4e455effc3c9a87943','fa2d2a38f0c9ea2d420f7b346ff8f5496d0d9680b6aa8d89322ef05db82a5638'),('manuscript-query-resolution-20261014/accounting-product-proposal.pdf','manuscript-reserving-bootstrap-20261014/accounting-product-proposal.pdf'),('Version **2.84**','Version **2.85**'),('**Version 2.84,','**Version 2.85,'),('Version 2.84, 251','Version 2.85, 254'),('current Version 2.84 candidate','current Version 2.85 candidate'),('progress — Version 2.84','progress — Version 2.85'),('251 pages','254 pages'),('2.73–2.84','2.73–2.85'),('through 2.84','through 2.85')]:s=s.replace(a,b)
 if n.endswith('accounting-master-current.md'):
  a=s.index('**P17-09:');b=s.index(N+'[P17-01]',a);s=s[:a]+'**P17-09: bootstrap-consistency follow-up.**'+N+N+summary+N+N+next_text+N+s[b:];s=s.replace('Five pages of 2.84 received','Seven pages of 2.85 received')
 elif n.endswith('accounting-master-checkpoint.md'):
  s=s.replace('## Latest completed work'+N+N,'## Latest completed work'+N+N+summary+N+N,1);a=s.index('Refresh and skeptically audit P17-09');b=s.index(N+'## Preserve',a);s=s[:a]+next_text+N+s[b:]
 elif n.endswith('accounting-continuation-requirements-20261007.md'):
  s=s.replace('P17-08’s [query-resolution cases]',summary+N+N+'P17-08’s [query-resolution cases]',1)
  s=s.replace('The immediate work is the P17-09 consequential literature/claim audit,','The immediate work is the P17-09 bootstrap-consistency audit,')
  s=s.replace('The immediate action is'+N+"P17-10's state-only exchange; P17-04's remaining operation repairs stay queued.",'The state-only exchange is also delivered. '+next_text)
 elif n.endswith('accounting-p17-completion-20261014.md'):
  a=s.index('Next refresh and audit P17-09');b=s.index(N+N,a);s=s[:a]+summary+N+N+next_text+s[b:]
  s=s.replace('P17-01 is the immediate ready action.','P17-01 is delivered; the P17-09 consistency audit is the immediate ready action.')
  s=s.replace('| Version 2.72 and current assessment | Checked baseline for this plan |','| Version2.85 and full2.72 assessment | Current candidate and frozen full assessment |')
 elif n.endswith('accounting-p18-completion-20261014.md'):
  s=s.replace('integration follows the refreshed P17-09 consequential-source audit.','integration follows the refreshed P17-09 consistency audit.'+N+N+summary)
 else:
  a=s.index('1. Refresh');b=s.index('2. Give',a);s=s[:a]+'1. '+next_text+N+'   '+summary.replace('data/accounting-master/','')+N+s[b:]
  s=s.replace('query resolution in 2.84.','query resolution in 2.84; reserving uncertainty in 2.85.')
 p.write_text(s)
index=(R/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=R);assert index
(A/'refresh-manifest.json').write_text(json.dumps({'before':before,'after':{n:sha(R/n) for n in cs},'index_preserved':index,'next':next_text},indent=2)+N)
(A/'execution-note.md').write_text('# Control refresh13'+N+N+summary+N+N+next_text+N)
print(json.dumps({'version':'2.85','controls':6,'index_preserved':index}))

