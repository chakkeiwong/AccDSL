"""Lock the successor package and reproduce its documents and new companions."""
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time

D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027'
T=R/'docs/design/proposal/manuscript-sector-v555-20261027'
read=lambda p:json.loads(p.read_text())
digest=lambda p:sha256(p.read_bytes()).hexdigest()
def dump(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2);f.write(chr(10))

def lock():
    assert read(D/'verification-02.json')['passed']
    assert not (T/'package-manifest.json').exists()
    base=read(D/'baseline.json')
    manifest=read(B/'package-manifest.json')
    manifest.update(candidate='5.55;not_ready',manifest_self_hash=str((D/'package-record.json').relative_to(R)))
    names=sorted({r['path'] for r in base['files']}|set(base['added_files']))
    manifest['files']=[dict(path=name,sha256=digest(T/name),bytes=(T/name).stat().st_size) for name in names]
    dump(T/'package-manifest.json',manifest)
    result=subprocess.run([sys.executable,'-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True,check=True)
    dump(D/'package-record.json',dict(passed=True,files=len(names),manifest_sha256=digest(T/'package-manifest.json'),
        verification=json.loads(result.stdout),baseline_manifest_sha256=digest(B/'package-manifest.json')))
    print(result.stdout.strip())

def stage():
    record=read(D/'package-record.json')
    assert digest(T/'package-manifest.json')==record['manifest_sha256']
    target=Path(tempfile.mkdtemp(prefix='accdsl-sector-v555-',dir='/tmp'))
    for row in read(T/'package-manifest.json')['files']:
        source=T/row['path'];assert digest(source)==row['sha256']
        dest=target/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
    (target/'package-manifest.json').write_bytes((T/'package-manifest.json').read_bytes())
    folder=D/'relocation-01';folder.mkdir(exist_ok=False)
    dump(folder/'location.json',dict(target=str(target),manifest_sha256=record['manifest_sha256']))
    print(json.dumps(dict(target=str(target),files=record['files'])))

def reproduce(key):
    assert key in ['insurance-paa-dated-book','bank-interfaces']
    target=Path(read(D/'relocation-01/location.json')['target'])
    folder=target/'companions'/key
    meta=read(folder/'component.json')
    extracted=target/(key+'-extracted')
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='-1',PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONPATH',None)
    command=[sys.executable,'-I','-B',str(folder/'unpack.py'),'--destination',str(extracted)]
    started=time.monotonic()
    result=subprocess.run(command,cwd='/tmp',env=env,capture_output=True,text=True,check=True,timeout=60)
    extraction=json.loads(result.stdout)
    command2=[sys.executable,'-B',str(extracted/meta['driver'])]
    if meta['root_argument']:command2+=['--root',str(extracted)]
    command2+=['--output',str(extracted/'output-01')]
    log=D/'relocation-01'/(key+'.stdout')
    with log.open('x') as f:
        run=subprocess.run(command2,cwd='/tmp',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
    out=extracted/'output-01'
    success=run.returncode==0
    comparisons=[]
    if success:
        if key=='insurance-paa-dated-book':
            previous=R/'data/accounting-master/insurance-paa-dated-book-20261027/attempt-01'
            for name in ['cases.json','controls.json','verification.json']:
                equal=read(out/name)==read(previous/name);comparisons.append(dict(file=name,exact_match=equal));success &= equal
        else:
            previous=R/'data/accounting-master/bank-interface-consolidation-20261027/attempt-01'
            for name in ['bank.json','bank-v2.json','bank-assessment.json','exact-time.json','checks.json']:
                equal=read(out/name)==read(previous/name);comparisons.append(dict(file=name,exact_match=equal));success &= equal
    dest=D/'relocation-01'/(key+'-results');dest.mkdir(exist_ok=False)
    for name in (['verification.json','run-manifest.json'] if key=='insurance-paa-dated-book' else ['checks.json','run-manifest.json']):
        if (out/name).exists():(dest/name).write_bytes((out/name).read_bytes())
    report=dict(passed=bool(success),extraction=extraction,command=command2,extraction_command=command,
        exit_code=run.returncode,wall_seconds=time.monotonic()-started,comparisons=comparisons,
        environment={k:env[k] for k in ['CUDA_VISIBLE_DEVICES','PYTHONDONTWRITEBYTECODE']},
        archive_sha256=meta['archive_sha256'],output=str(out),timestamp_utc=datetime.now(timezone.utc).isoformat())
    dump(D/'relocation-01'/(key+'-reproduction.json'),report)
    print(json.dumps(dict(component=key,passed=bool(success),full_comparisons=comparisons)))
    raise SystemExit(0 if success else 1)

def finish():
    import fitz
    target=Path(read(D/'relocation-01/location.json')['target'])
    report=dict(documents=[],components=[],passed=True)
    normalize=lambda value:' '.join(value.split())
    for name in ['accounting-product-proposal','simulation-foundations']:
        build=read(D/'relocation-01'/(name+'-build.json'));assert build['exit_code']==0
        a=fitz.open(T/(name+'.pdf'));b=fitz.open(target/(name+'.pdf'))
        log=(target/(name+'.log')).read_text(errors='replace')
        warnings=bool(re.search(r'undefined|Overfull|multiply defined',log,re.I))
        mismatches=[] if len(a)==len(b) else ['page_count']
        mismatches += [i+1 for i in range(min(len(a),len(b))) if normalize(a[i].get_text())!=normalize(b[i].get_text())]
        report['documents'].append(dict(name=name,pages=len(a),normalized_page_mismatches=mismatches,
            unresolved_or_overfull=warnings,
            original_pdf_sha256=digest(T/(name+'.pdf')),copied_pdf_sha256=digest(target/(name+'.pdf'))))
        report['passed'] &= not mismatches and not warnings
    for key in ['insurance-paa-dated-book','bank-interfaces']:
        result=read(D/'relocation-01'/(key+'-reproduction.json'))
        report['components'].append(dict(component=key,passed=result['passed'],comparisons=result['comparisons']))
        report['passed'] &= result['passed']
    # Copied rebuilds may change PDF metadata; all non-generated package inputs must remain exact.
    for row in read(T/'package-manifest.json')['files']:
        if Path(row['path']).suffix!='.pdf':assert digest(target/row['path'])==row['sha256']
    for row in read(D/'baseline.json')['files']:assert digest(B/row['path'])==row['sha256']
    report.update(baseline_preserved=True,all_copied_nonpdf_inputs_preserved=True,full_release_closure=False)
    dump(D/'relocation-01/result.json',report)
    print(json.dumps(report))

if __name__=='__main__':
    action=sys.argv[1]
    if action=='lock':lock()
    elif action=='stage':stage()
    elif action=='reproduce':reproduce(sys.argv[2])
    elif action=='finish':finish()
