"""Freeze the checked insurer disclosure unit and refresh direct continuation."""
import datetime,hashlib,json,platform,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'source-checks.json').read_text())
assert c['passed']==75 and not c['failed']
tick=chr(96);plan=b['plan'];next_plan='docs/plans/accounting-munich-transition-integration-20261012.md'
old="""Inspect the retained Munich Re 2023 annual report's transition methods,
measurement assumptions and disclosed opening balances. Preserve historical
rule/issuer distinctions, actual-input unknowns and corpus exposure. Plan:
"""+tick+plan+tick+'.'
new="""Integrate the checked Munich Re transition disclosure, rounded equity bridge
and separate issued/held margins in Version 2.50. Preserve the dated method
populations, issuer-specific inputs and actual-group unknowns. Plan:
"""+tick+next_plan+tick+'.'
note="""## Latest Munich Re transition disclosure inquiry

The retained 2023 report supplies transition-method populations, a rounded
opening-equity bridge and separate issued/held opening margins. All 75
source/arithmetic checks pass across sixteen selected pages and 23 exact
excerpts; seven renders were inspected. The net margin of -EUR22,320m is
consistent with the rounded -EUR22.3bn bridge component. The rounded endpoint
difference is preserved, not called a source conflict. Actual groups,
valuation inputs, operative authority and independent interpretation remain
open. Added author-annotation exposure is recorded. Version 2.49 stays current
pending 2.50 integration; readiness remains not_ready.
Result: """+tick+'data/accounting-master/munich-transition-disclosures-20261012/result.md'+tick+'.\n\n'
def once(s,a,z):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)
prepared=[]
for r in b['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
    anchor='## Latest transition dependency source inquiry\n\n';s=once(s,anchor,note+anchor)
    if p.name!='accounting-continuation-requirements-20261007.md':s=once(s,old,new)
    else:s=once(s,'Next internal unit: '+tick+plan+tick+'.','Next internal unit: '+tick+next_plan+tick+'.')
    if p.name=='accounting-master-current.md':
        for a,z in [
            ('Version 2.49 integrated; next inspect Munich Re transition disclosures','Munich Re transition disclosure inquiry complete; next integrate Version 2.50'),
            ('next inspect Munich Re 2023 transition methods and measurement disclosures.','the Munich Re 2023 disclosure inquiry is complete; next integrate the supported case in Version 2.50.'),
            ('1. Follow the direct next plan: inspect Munich Re 2023 transition methods,\n   measurement assumptions and disclosed opening balances.',
             '1. Follow the direct next plan: integrate the checked Munich Re transition\n   methods, rounded bridge and scoped margin evidence in Version 2.50.')]:
            s=once(s,a,z)
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=[plan,next_plan]
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans]
inputs={b['source_record']['local_path']:b['source_record']['sha256'],
        'data/financial-report-benchmark/source-evidence.json':b['source_evidence_sha256']}
for p in ['data/accounting-master/transition-dependencies-integration-20261012/run-manifest.json',
          'data/accounting-master/transition-dependencies-integration-20261012/completion.json']:inputs[p]=sha(ROOT/p)
now=datetime.datetime.now(datetime.timezone.utc)
commands=[['python3',str((OUT/'read_pages.py').relative_to(ROOT)),*map(str,ns)] for ns in
          [[185,186],[187,188],[1,3],[157,158],[166,167],[211,212],[213,256],[257,258]]]
commands += [['python3',str((OUT/n).relative_to(ROOT))] for n in ['check_sources.py','closeout.py']]
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
 'plans':plans,'plan_addendum':str((OUT/'arithmetic-plan.md').relative_to(ROOT)),
 'result':str((OUT/'result.md').relative_to(ROOT)),'commands':commands,
 'source_discovery':'Searched retained extracted text for transition-method and measurement anchors; no network request.',
 'environment':{'python':sys.executable,'version':platform.python_version(),'pdf':'PyMuPDF','arithmetic':'decimal.Decimal'},
 'cpu_gpu':'CPU PDF/file processing; no ML import or GPU probe',
 'data_version':{'id':b['source_record']['document_id'],'sha256':b['source_record']['sha256'],'source_url':b['source_record']['source_url']},
 'random_seeds':'N/A: deterministic source/disclosed-arithmetic checks',
 'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),'checks':c['wall_seconds']},
 'selected_pages':[r['pdf_page'] for r in json.loads((OUT/'selected-pages.json').read_text())],
 'inspected_render_pages':[157,167,185,186,187,213,257],
 'input_hashes':inputs,'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'annotation_exposure':'Additional author annotation of Munich Re provisional P12 test family; no clean heldout claim.',
 'readiness':'not_ready','next_plan':next_plan}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded insurer disclosure review complete; independent interpretation pending',
 'source_checks':c['passed'],'failed':0,'source_pages':16,'source_anchors':23,'inspected_renders':7,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready','next_plan':next_plan})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'readiness':'not_ready'}))
