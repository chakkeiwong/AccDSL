from pathlib import Path
import hashlib,json,shutil,difflib
from datetime import datetime,timezone
D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'docs/design/proposal/manuscript-debt-reading-v553-20261027'
T=R/'docs/design/proposal/manuscript-release-v553r1-20261027'
C=R/'docs/design/proposal/manuscript-release-prep-v552r2-20261027'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
assert (R/'docs/AccDSL-latest.tex').resolve().parent==B
assert not T.exists()
m=json.loads((B/'package-manifest.json').read_text());rows=[]
for row in m['files']:
 p=B/row['path'];assert sha(p)==row['sha256'];rows.append({'path':row['path'],'sha256':sha(p)})
T.mkdir()
for row in m['files']:
 p=B/row['path']
 if p.suffix=='.pdf':continue
 q=T/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
 p=T/name;p.write_text(once(p.read_text(),'Version 5.53','Version 5.53-R1'))
p=T/'accounting-product-proposal.tex';p.write_text(once(p.read_text(),'\\tableofcontents','\\input{reading-guide}\n\\tableofcontents'))
p=T/'simulation/01-observations.tex';s=p.read_text();s=once(s,'If interest is the only cash payment, closing cash is','If the interest payment is the only cash movement, closing cash is');s=once(s,'Two histories can agree with retained reports, agree under one simulation, or agree for every permitted future decision. These are progressively stronger requirements.','First restrict attention to histories compatible with the same retained reports. Within that family, two histories may agree under one specified simulation or under every permitted future decision. Agreement for the full set of decisions is stronger than agreement for one selected query.');p.write_text(s)
p=T/'simulation/03-learning.tex';p.write_text(once(p.read_text(),'Four dates attached to one fact','Five dates attached to one fact'))
p=T/'simulation/04-scenarios.tex';s=p.read_text();a=s.index('A scenario can also specify a set');b=s.index('\\section{Conditioning and intervention}',a)
s=s[:a]+r'''A scenario can also specify a set $\mathcal S$ of paths and a collection
$\Pi$ of candidate policies. Let $\mathcal A\subseteq\mathcal H\times
\mathcal S\times\Pi$ contain the jointly admitted triples: a compatible
history, an allowed shock path and a policy whose information and execution
rules are specified for that history and path. The outcome family is
\begin{equation}
 \mathcal Y=\{F(h,s,\pi):(h,s,\pi)\in\mathcal A\}.
\end{equation}
The joint restriction matters. A lender's offer can depend on the company's
contract state; a commodity shock can affect both sales and collateral; a
policy may be admissible only for certain information states. Choosing each
component independently from its marginal set can violate those dependencies.
An admitted triple can still produce a refused funding request, distress or
an unresolved result when its declared execution rules allow those outcomes.
Admissibility does not mean that every attempted payment succeeds.

'''+s[b:];p.write_text(s)
cp='simulation/lit-09-approximation-4.tex';assert sha(B/cp)==sha(R/'docs/design/proposal/manuscript-release-prep-v552r1-20261027'/cp);shutil.copy2(C/cp,T/cp)
p=T/'references.bib';s=p.read_text();a=s.index('@misc{litcloseestimation,');b=s.index('\n}\n',a)+3;entry=s[a:b];entry=once(entry,'year={2022}','year={2021}');entry=once(entry,'eprint={2002.07261}','eprint={2002.07261v2}');entry=once(entry,'note={Technical anchors refer to the retained arXiv manuscript}','note={Technical anchors refer to arXiv:2002.07261v2, 17 May 2021. The DOI identifies the 2022 journal publication; technical equivalence between editions has not been established here}');p.write_text(s[:a]+entry+s[b:])
shutil.copy2(D/'reading-guide.tex',T/'reading-guide.tex')
p=T/'README.md';s=p.read_text().replace('5.53','5.53-R1');s+='\nThis protected successor incorporates the checked initial-pairing/common-loss\ncoupling repair, explicit joint scenario admissibility, opening cash and date\nclarifications, a reading guide and an inspected arXiv edition pin. Its own\npackage and relocation results are recorded under release-pursuit-20261027/\nopening-repair; predecessor verification is not silently inherited. It remains\nnot_ready and is for internal review only.\n';p.write_text(s)
changes=[];diff=[]
for row in rows:
 if row['path'].endswith('.pdf'):continue
 q=T/row['path']
 if sha(q)!=row['sha256']:
  changes.append({'path':row['path'],'before':row['sha256'],'after':sha(q)})
  diff.extend(difflib.unified_diff((B/row['path']).read_text().splitlines(True),q.read_text().splitlines(True),fromfile='5.53/'+row['path'],tofile='5.53-R1/'+row['path']))
(D/'source-delta.patch').write_text(''.join(diff))
(D/'baseline.json').write_text(json.dumps({'baseline':str(B.relative_to(R)),'candidate':str(T.relative_to(R)),'files':rows,'manifest_sha256':sha(B/'package-manifest.json'),'coupling_sha256':sha(C/cp),'changes':changes,'new_files':[{'path':'reading-guide.tex','sha256':sha(T/'reading-guide.tex')}],'timestamp':datetime.now(timezone.utc).isoformat()},indent=2)+'\n')
H={'fixed','floating'};S={'calm','stress'};P={'hold','refinance'}
product={(h,s,p) for h in H for s in S for p in P}
admitted={(h,s,p) for h,s,p in product if not (h=='floating' and s=='stress' and p=='refinance')}
assert len(product)==8 and len(admitted)==7
assert ('floating','stress','refinance') not in admitted
outcome={(h,s,p):('distress' if h=='floating' and s=='stress' and p=='hold' else 'settled') for h,s,p in admitted}
assert 'distress' in outcome.values()
(D/'domain-check.json').write_text(json.dumps({'passed':True,'unrestricted_triples':8,'admitted_triples':7,'inadmissible_triple_excluded':True,'admitted_distress_retained':True,'scope':'exact illustrative domain test; no company fact or general feasibility theorem'},indent=2)+'\n')
print(json.dumps({'candidate':str(T.relative_to(R)),'changed':[x['path'] for x in changes],'new':'reading-guide.tex','baseline_files':len(rows)}))
