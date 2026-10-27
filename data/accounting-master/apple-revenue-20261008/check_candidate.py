"""Bound source claims, the new narrative and preservation of earlier work."""
from datetime import datetime,timezone
import difflib,hashlib,json,re,time
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];START=time.monotonic()
OLD=ROOT/'docs/design/proposal/manuscript-adoption-20261008';NEW=ROOT/'docs/design/proposal/manuscript-revenue-20261008'
if (OUT/'completion.json').exists():raise SystemExit('Closed unit')
checks=[];inputs={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    inputs[str(p.relative_to(ROOT))]=sha(p);return json.loads(p.read_text())


def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))


def verify(name,hashes):
    bad=[n for n,h in hashes.items() if not (ROOT/n).is_file() or sha(ROOT/n)!=h];check(name,not bad,dict(count=len(hashes),mismatches=bad))


baseline=read(OUT/'baseline.json');verify('V2.6 unit and retained source inputs preserved',baseline['protected_hashes'])
reloc={r['historical_path']:r['preserved_path'] for r in baseline['pointer_relocations']}
verify('prior live pointer copies preserved',{r['preserved_path']:r['sha256'] for r in baseline['pointer_relocations']})
previous=read(ROOT/baseline['prior_manifest']);verify('all prior manifest references resolved',{reloc.get(n,n):h for n,h in previous['artifact_hashes'].items()})
oldfiles={p.relative_to(OLD) for p in OLD.rglob('*') if p.suffix in {'.tex','.bib','.lark'}};newfiles={p.relative_to(NEW) for p in NEW.rglob('*') if p.suffix in {'.tex','.bib','.lark'}}
check('source inventory unchanged',oldfiles==newfiles);before=[];after=[];changed=[];diff=[]
for n in sorted(oldfiles):
    a=(OLD/n).read_text();b=(NEW/n).read_text();inputs[str((NEW/n).relative_to(ROOT))]=sha(NEW/n)
    if a!=b:changed.append(str(n));diff.extend(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile=str(OLD/n),tofile=str(NEW/n)))
    if n.suffix=='.tex':before.append(a);after.append(b)
(OUT/'manuscript-delta.diff').write_text(''.join(diff))
check('only intended sources changed',set(changed)=={'accounting-product-proposal.tex','chapters/13-reference-company.tex','chapters/02-history.tex'})
a='\n'.join(before);b='\n'.join(after)
pattern=r'\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}'
displays=lambda t:[m.group() for m in re.finditer(pattern,t,re.S)]
old_displays=displays(a);new_displays=displays(b);added=[s for s in new_displays if '\\label{eq:apple-deferred-movement}' in s]
check('all prior displays preserved with one new reconciliation',len(added)==1 and [s for s in new_displays if s not in added]==old_displays,dict(before=len(old_displays),after=len(new_displays)))
old_ch=(OLD/'chapters/13-reference-company.tex').read_text();new_ch=(NEW/'chapters/13-reference-company.tex').read_text()
check('earlier synthetic and Apple cases verbatim',new_ch.startswith(old_ch))
addition=new_ch[len(old_ch):]
check('material source qualifications and authored limits retained',all(s in addition for s in ['stand-alone selling','returns','commission','Greater China','unquantified','not reconstructed','not a verified issuer rounding rule','cash collections','No probability']))
old_hist=(OLD/'chapters/02-history.tex').read_text();new_hist=(NEW/'chapters/02-history.tex').read_text()
check('history chapter unchanged after opening bridge',old_hist.split('\\section{',1)[1]==new_hist.split('\\section{',1)[1])
keys=lambda t:re.findall(r'@\w+\s*\{\s*([^,\s]+)',t)
old_bib=(OLD/'references.bib').read_text();new_bib=(NEW/'references.bib').read_text()
check('bibliography preserved exactly',old_bib==new_bib,len(keys(new_bib)))
cites=lambda t:{k.strip() for g in re.findall(r'\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}',t) for k in g.split(',')}
check('old citations retained and all citations resolve',cites(a)<=cites(b)<=set(keys(new_bib)))
labels=re.findall(r'\\label\{([^}]+)\}',b);refs=re.findall(r'\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}',b)
check('unique labels and complete cross references',len(labels)==len(set(labels)) and set(refs)<=set(labels))
pdf=NEW/'accounting-product-proposal.pdf';doc=fitz.open(pdf);text=' '.join(' '.join(p.get_text().split()) for p in doc);text=re.sub(r'(?<=\d),\s+(?=\d)',',',text)
check('material candidate text rendered',all(s in text for s in ['Version 2.7','124,300','8,461','4.1','3.95','4.25','120.6','119.6','8.448','124.7']))
log=(NEW/'accounting-product-proposal.log').read_text();warnings=[l for l in log.splitlines() if any(s in l for s in ['Warning','Overfull','Underfull','! '])]
check('clean final LuaLaTeX log','LuaHBTeX' in log and not warnings,warnings)
check('clean bibliography log',not re.search(r'Warning--|error message|I couldn.t open',(NEW/'accounting-product-proposal.blg').read_text()))
e=read(OUT/'evidence-checks.json');check('document/source arithmetic checks current',e['failed']==0 and all(c['passed'] for c in e['checks']) and e['checker_sha256']==sha(OUT/'prepare_evidence.py'))
verify('source check inputs current',e['inputs']);verify('source claim and calculation outputs bound',e['output_hashes'])
ledger=read(OUT/'source-claim-supplement.json');check('bounded note coverage remains distinct from package closure',len(ledger['units'])==17 and ledger['coverage']['whole_apple_package']=='open' and ledger['coverage']['outstanding_exhibit_targets']==40)
build=read(OUT/'build-receipt.json');check('build binds PDF and log',build['exit_code']==0 and build['pdf_sha256']==sha(pdf) and build['log_sha256']==sha(OUT/'build.log'))
render=read(OUT/'render-manifest.json');review=read(OUT/'render-review.json')
check('render binds final PDF',render['pdf_sha256_before']==render['pdf_sha256_after']==sha(pdf))
verify('render image hashes',{r['path']:r['sha256'] for r in render['rendered_pages'].values()})
check('author inspection binds actual render',review['render_manifest_sha256']==sha(OUT/'render-manifest.json') and review['author_review_sha256']==sha(OUT/'author-review.md') and review['page_numbers']==render['page_numbers'])
check('independent and human acceptance remain pending',review['independent_reader']==review['human_acceptance']=='pending')
source_render=read(OUT/'source-render-receipt.json')
check('derived HTML renders bound to retained excerpts',all(sha(Path(r['source_html']))==r['sha256'] and sha(Path(r['pdf']))==r['pdf_sha256'] and r['text_preserved_after_namespace_unwrap'] for r in source_render['records']))
history=read(ROOT/'data/accounting-master/direct-p19-20261007/recovery-entry-v1.json');counts={}
for key in ['protected_hashes','upstream_reference_hashes','controller_hashes']:verify('historical '+key,history[key]);counts[key]=len(history[key])
c=read(ROOT/'data/accounting-master/continuation-20261007/baseline-manifest.json');rel={r['historical_path']:r['preserved_path'] for r in c['relocations']};verify('P19 hashes resolve historically',{rel.get(n,n):h for n,h in c['p19_historical_artifact_hashes'].items()})
readiness=read(ROOT/'data/accounting-master/deliverables/P19/readiness.json');check('full proposal negative status preserved',readiness['status']=='not_ready' and not readiness['ready'] and set(readiness['remaining_blockers'])=={'P15-'+s for s in ['E01','E05','E07','E08','E14']})
report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),checker_sha256=sha(Path(__file__)),inputs=inputs,pdf=dict(path=str(pdf.relative_to(ROOT)),sha256=sha(pdf),pages=len(doc)),changed_sources=changed,baseline_displays=len(old_displays),candidate_displays=len(new_displays),bibliography_keys=len(keys(new_bib)),preservation_counts=counts,checks=checks,passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks),wall_seconds=time.monotonic()-START)
(OUT/'candidate-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['passed','failed','baseline_displays','candidate_displays','bibliography_keys']}))
if report['failed']:print(json.dumps([c for c in checks if not c['passed']]));raise SystemExit(1)
