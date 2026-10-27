"""Source-preserving additive integration; builds do not imply research acceptance."""
from pathlib import Path
import re,json,hashlib,shutil
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
src=R/'docs/design/proposal/manuscript-opening-binding-20261026'
dst=R/'docs/design/proposal/manuscript-literature-methods-20261026'
if dst.exists():raise SystemExit('Refuse to overwrite existing successor')
files=[f for f in src.rglob('*') if f.is_file() and f.suffix in ['.tex','.bib','.lark','.json','.sty','.cls','.png','.jpg','.jpeg','.svg','.pdf'] and f.name not in ['accounting-product-proposal.pdf','simulation-foundations.pdf']]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
protected=[dict(path=str(f.relative_to(src)),sha256=sha(f)) for f in files]
for f in files:
 d=dst/f.relative_to(src);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,d)
s=(R/'docs/design/research/simulation-literature-closure-20261026/supplement.tex').read_text()
chunks={}
for m in re.finditer(r'\\(section|subsection)\{([^}]+)\}',s):
 end=re.search(r'\\(?:section|subsection)\{|\\begingroup',s[m.end():]);tail=m.end()+end.start() if end else len(s)
 chunks[m.group(2)]=s[m.end():tail].strip()
# Use unique keys so no predecessor citation or label is reinterpreted.
items=re.findall(r'\\bibitem\{([^}]+)\}\s*(.*?)(?=\\bibitem|\\end\{thebibliography\})',s,re.S)
keymap={k:'litclose'+k for k,_ in items}
def adapt(t):
 def cite(m):return m.group(1)+'{'+','.join(keymap[x] for x in m.group(2).split(','))+'}'
 t=re.sub(r'(\\cite(?:\[[^]]*\])?)\{([^}]+)\}',cite,t)
 t=t.replace('eq:finite-','sim:lit-finite-')
 t=t.replace('The present supplement reuses that work.','These arguments retain that exact finite scope.')
 t=t.replace('The observation-quotient work already present in AccDSL supplies exact finite\npath comparisons and deliberately rejected partitions for this restriction.\n','The finite reference implementation supplies exact path comparisons and\ndeliberately rejected partitions for this restriction.\n')
 # Reader-facing text must not require the separate supplement for a premise.
 t=t.replace('the earlier\n$2\\varepsilon+\\eta$ policy-regret bound','the common-policy\n$2\\varepsilon+\\eta$ regret bound derived in this chapter')
 return t
edits=[]
def add(chapter,before,name,blocks,intro=''):
 content='\n\n'+('\\section{'+name+'}\n' if name else '')+intro
 for heading,title in blocks:
  if title:content+='\n\\section{'+title+'}\n'
  content+=adapt(chunks[heading])+'\n'
 fragment=dst/'simulation'/('lit-'+chapter+'-'+str(len(edits)+1)+'.tex');fragment.write_text(content)
 f=dst/'simulation'/(chapter+'.tex');old=f.read_text();needle='\\section{'+before+'}'
 assert old.count(needle)==1,(chapter,before)
 include='\\input{simulation/'+fragment.stem+'}\n\n';f.write_text(old.replace(needle,include+needle))
 edits.append(dict(path=str(f.relative_to(dst)),before=before,fragment=str(fragment.relative_to(dst)),insertion=include))
add('03-learning','An informative and an uninformative disclosure','A finite filter that preserves contract identity',[('A finite filter that preserves contract identity',None)])
add('03-learning','A proposed information service','Recursive ambiguity and persistent contracts',[('A recursive worst case can describe a different company',None)])
# The finite quotient is already taught here; introduce only the genuinely new lift passage.
full=chunks['Exact sharing must preserve information as well as cash'];start=full.index('The distinction between a process')
chunks['Information-process lifts']=full[start:]
add('08-compression','Unweighted families require relational memory','A larger state can preserve the information structure',[('Information-process lifts',None)])
add('09-approximation','Error propagation through time',None,[('Thresholds require control near the boundary','A quantitative boundary argument'),('Close optimal values do not validate a transferred policy','A common-policy regret argument'),('Even sampling can accidentally reveal the future','When sampled paths disclose their own futures'),('A finite compression method that keeps discrete decisions','A finite coupling method for discrete decisions')])
add('11-numerics','Classical reference methods',None,[('What a causal generator does and does not preserve','Causal generators and feasible policy transfer'),('Learning a transition law needs more than matching an aggregate','Controlled transition laws and off-policy support')])
add('19-literature','What remains to be researched',None,[('What is disclosed is part of the observation model','Disclosure selection and the observation likelihood'),('A simple equilibrium of silence','When silence has an equilibrium interpretation'),('Mechanical shocks, conditioning and intervention','What changes under an intervention')])
add('25-interactions','Prioritizing interaction tests',None,[('A rate shock changes both market access and ownership','A complete rate, covenant and ownership path'),('Executing the distinction between promises and book amounts','Executing promises, carrying amounts and ownership')])
add('26-finite-finance','Reference-solver requirements',None,[("Checking lender prices against the issuer's actual choice",'Two creditors, policy consistency and financing refusal'),('Positive continuation value need not make renegotiation feasible','Why positive surplus can still end in liquidation')])
used=set()
for edit in edits:
 t=(dst/edit['fragment']).read_text()
 for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',t):used.update(group.split(','))
# Fully preserved bibliographic descriptions retain exact versions/source caveats.
with (dst/'references.bib').open('a') as f:
 for key,body in items:
  if keymap[key] not in used:continue
  body=' '.join(body.split());body=body.replace('\\emph{','\\textit{')
  f.write('\n@misc{'+keymap[key]+',\n author={{AccDSL retained source record}},\n title={{'+body+'}},\n year={2026},\n note={Version and inspected technical anchors are stated in the chapter; bibliographic source description retained verbatim from the research supplement}\n}\n')
# Temporary descriptive bibliography entries must be normalized before acceptance.
for name in ['accounting-product-proposal.tex','simulation-foundations.tex']:
 f=dst/name;t=f.read_text();t=t.replace('Version 5.9 (proposal candidate)','Version 5.10 (proposal candidate)').replace('Version 5.5 research companion','Version 5.10 research companion');f.write_text(t)
manifest=dict(baseline=str(src.relative_to(R)),successor=str(dst.relative_to(R)),baseline_pdf_sha256=sha(src/'accounting-product-proposal.pdf'),protected_sources=protected,edits=edits,new_bibliography_keys=sorted(used),scope='All predecessor source bytes recoverable by removing declared insertions and cover/bibliography additions; no production script edits.')
(B/'manuscript-integration.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(protected=len(files),chapter_insertions=len(edits),new_sources=len(used),successor=str(dst))))
