from pathlib import Path
import json,hashlib,shutil,re
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
b=json.loads((H/'baseline.json').read_text());S=R/b['source'];T=R/'docs/design/proposal/manuscript-release-prep-v551r1-20261027'
if T.exists():raise SystemExit('Refusing to overwrite candidate')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[p for p in S.rglob('*') if p.is_file() and p.suffix in ['.tex','.bib','.lark','.json','.md','.png','.jpg','.pdf','.svg'] and p.name not in ['accounting-product-proposal.pdf','simulation-foundations.pdf']]
for p in files:
 q=T/p.relative_to(S);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
changes=[]
def edit(rel,old,new,count=1):
 p=T/rel;t=p.read_text();assert t.count(old)==count,(rel,old,t.count(old));t=t.replace(old,new);p.write_text(t);changes.append({'file':rel,'old':old,'new':new})
edit('accounting-product-proposal.tex','Version 5.51 (proposal candidate)','Version 5.51-R1 (release-preparation candidate)')
edit('simulation-foundations.tex','Version 5.51 research companion; provisional candidate','Version 5.51-R1 research companion; provisional candidate')
# Use the same floating fraction in both treatments; no financial target changes.
slash=chr(92)
p=T/'chapters/01-purpose.tex';text=p.read_text();old='fixed-rate fraction $'+slash+'alpha'+slash+'in[0,1]$, future interest is';new='floating-rate fraction $'+slash+'alpha'+slash+'in[0,1]$, using the convention of\nChapter~'+slash+'ref{sim:observations}, future interest is';edit('chapters/01-purpose.tex',old,new)
edit('chapters/01-purpose.tex',' I('+slash+'alpha)=100[0.05'+slash+'alpha+0.07(1-'+slash+'alpha)]=7-2'+slash+'alpha.',' I('+slash+'alpha)=100[0.05(1-'+slash+'alpha)+0.07'+slash+'alpha]=5+2'+slash+'alpha.')
edit('simulation/family-policies.tex','General observation languages, longer horizons, empirical actor access, saved partial frontiers and durable recovery require further work.','General observation languages, longer horizons, empirical actor access and durable recovery require further work. The saved partial-frontier extension for the temporal profile is developed in Section~'+slash+'ref{sim:release-temporal-frontier}.')
p=T/'simulation/temporal-frontier.tex';lines=p.read_text().splitlines();idx=next(i for i,l in enumerate(lines) if l.startswith(slash+'section{'));lines.insert(idx+1,slash+'label{sim:release-temporal-frontier}');p.write_text(chr(10).join(lines)+chr(10));changes.append({'file':'simulation/temporal-frontier.tex','change':'Add stable cross-reference label only.'})
edit('simulation/observation-binding.tex','The remaining computational difficulty is how to continue an unfinished temporal search while retaining its unexamined possibilities.','For this observation-binding profile, the remaining computational difficulty is how to continue an unfinished temporal search while retaining its unexamined possibilities. Section~'+slash+'ref{sim:release-temporal-frontier} develops that extension for the selected temporal domain.')
# Keep reference files byte-exact; explicit reference root replaces silent dependency guessing.
refmap=[]
for name in ['core-contract.md','core-ir.schema.json','core0-lowering-profile-v1.md','context-chronology-profile-v1.md','reconstruction-profile-v1.md','review-persistence-profile-v1.md']:
 p=R/'docs/design/spec'/name;q=T/'spec'/name;shutil.copy2(p,q);refmap.append({'reference':'spec/'+name,'source':str(p.relative_to(R)),'sha256':sha(p),'scope':'historical normative reference; no implicit promotion to current portable profiles'})
(T/'reference-map.json').write_text(json.dumps(refmap,indent=2)+chr(10))
preserved=[{'file':str(p.relative_to(S)),'before':sha(p),'after':sha(T/p.relative_to(S)),'unchanged':sha(p)==sha(T/p.relative_to(S))} for p in files]
manifest={'baseline':b['candidate'],'candidate':'5.51-R1 release-preparation; not_ready','source':str(S.relative_to(R)),'target':str(T.relative_to(R)),'original_files':preserved,'intentional_changes':changes,'added_reference_files':refmap,'claims':'Notation variable change, profile navigation and package references only. No new accounting or general algorithmic result.'}
(H/'manuscript-source-comparison.json').write_text(json.dumps(manifest,indent=2)+chr(10));print(json.dumps({'target':str(T),'copied':len(files),'changed':[(x['file']) for x in preserved if not x['unchanged']],'added_references':len(refmap)},indent=2))
