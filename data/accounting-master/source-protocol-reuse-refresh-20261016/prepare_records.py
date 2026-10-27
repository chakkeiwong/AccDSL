"""Static source/target preparation; never imports acquired package code."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess,sys,time,tomllib
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
    p=OUT/n
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2)+'\n')
def main():
    start=time.monotonic();checks=[]
    def check(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise ValueError(n)
    selection=ROOT/'data/accounting-master/selected-reuse-20261015/source-selection.json'
    selected=json.loads(selection.read_text());pins=[selection]
    for row in selected['source_pins']:
        p=ROOT/row['path'];check('prior-source/'+row['path'],sha(p)==row['sha256']);pins.append(p)
    ap=ROOT/'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/arelle/pyproject.toml'
    a=tomllib.loads(ap.read_text());check('arelle-declared-requirements',a['project']['dependencies']==selected['selected_native']['base_constraints'])
    pr=(OUT/'pdfplumber-requirements.txt.txt').read_text().splitlines()
    check('pdfplumber-requirements',pr==['pdfminer.six==20260107','Pillow>=12.2.0','pypdfium2>=5.9.0'])
    setup=(OUT/'pdfplumber-setup.py.txt').read_text()
    check('requirements-used','install_requires=base_reqs' in setup and 'with _open("requirements.txt")' in setup)
    check('source-version','version_info = (0, 11, 10)' in (OUT/'pdfplumber-pdfplumber-_version.py.txt').read_text())
    nodes=[dict(id='arelle-source',identity=selected['selected_native']['commit'],python=a['project']['requires-python']),
           dict(id='pdfplumber-source',identity=selected['pdf_baseline']['commit'],version='0.11.10',python_declared='>=3.8',minimum_from_pinned_dependency='>=3.10')]
    edges=[]
    for r in a['project']['dependencies']:edges.append(dict(owner='arelle-source',requirement=r,role='base',closure='unresolved selected version'))
    for r in a['build-system']['requires']:edges.append(dict(owner='arelle-source',requirement=r,role='build',closure='unresolved selected version'))
    for r in pr:edges.append(dict(owner='pdfplumber-source',requirement=r,role='base',closure='exact metadata below' if r.startswith('pdfminer') else 'unresolved selected version'))
    records=[]
    for file,version,role in [('pdfminer-release.json','20260107','exact required release'),('pillow-minimum.json','12.2.0','lower-bound metadata witness only'),('pypdfium-minimum.json','5.9.0','lower-bound metadata witness only')]:
        d=json.loads((OUT/file).read_text());i=d['info'];check('metadata/'+file,i['version']==version)
        record=dict(name=i['name'],version=version,role=role,python=i['requires_python'],requirements=i['requires_dist'],license_expression=i.get('license_expression'),license_description=i.get('license'),source=file,sha256=sha(OUT/file))
        records.append(record)
        if role=='exact required release':
            check('pdfminer-base',i['requires_dist'][:2]==['charset-normalizer>=2.0.0','cryptography>=36.0.0'])
            for r in i['requires_dist']:edges.append(dict(owner='pdfminer.six==20260107',requirement=r,role='not-selected-extra' if '; extra' in r else 'base',closure='unresolved selected version'))
    graph=dict(schema='StaticDependencyFrontier/1',nodes=nodes,edges=edges,metadata=records,selected_extras=[],
        shared_pillow_intersection='>=12.2.0,<13',declared_python_minimum='>=3.10',
        environment_lock=None,installations=False,compatibility='not checked',native_closure='unresolved',
        boundary='Inspected declarations and exact pdfminer metadata only; witnesses are not selected runtime versions.')
    write('dependency-frontier.json',graph)
    chain=[];p=ROOT/'data/accounting-master/sector-company-composition-20261016/assessment-successor.json'
    while True:
        d=json.loads(p.read_text());chain.append(dict(version=d['candidate_version'],path=str(p.relative_to(ROOT)),sha256=sha(p),scope=d.get('assessment_scope','baseline')));pins.append(p)
        if d['candidate_version']=='3.14':break
        prev=ROOT/d['predecessor'];check('assessment-parent/'+d['candidate_version'],sha(prev)==d['predecessor_sha256']);p=prev
    check('chain-inventory',len(chain)==22 and chain[0]['version']=='3.36')
    write('candidate-chain.json',dict(rows=list(reversed(chain)),scope='21 successor assessments plus3.14;3.17 incorporates3.16'))
    # Source notes are evidence for local claim boundaries, not automatic theorem support.
    source_notes=[]
    for row in chain[:-1]:
        folder=(ROOT/row['path']).parent
        candidates=[folder/'source-reading.md',folder/'ordered-eps/source-reading.md',folder/'audit.md']
        for p in candidates:
            if p.exists():source_notes.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)));pins.append(p)
    write('claim-source-index.json',dict(notes=source_notes,dispositions='claim-successor.md',fresh_reading='source-dispositions.md'))
    ledger=dict(source_support=[dict(source='EU2023/1803-original',new_reading=['IFRIC19.1–3,5–10','IAS8.10–12','IAS36.118–125'],scope='historical source only'),dict(source='pinned pdfplumber and exact package metadata',record='dependency-frontier.json',scope='static declarations only')],
        claim_support=[dict(record='claim-successor.md',scope='post3.14 finite accounting/local-derivation additions'),dict(record='protocol-successor.md',scope='future target mapping; no empirical result')],
        citation_venue=[dict(status='no fresh citation counts or collection-wide notice checks; retained metadata dates unchanged')],
        backward_snowball=[dict(lead='IFRIC19.3(c) original-terms exclusion',disposition='inspected; not affirmative early-conversion measurement'),dict(lead='IAS8.10–12 policy hierarchy',disposition='inspected; no unique zero-CGU allocation')],
        forward_snowball=[dict(status='no usable new result from two explicit source searches; no claim of coverage or source absence')],
        omissions=[dict(source=s,status='SOURCE_BLOCKED',action='distinct authenticated full-text lead required') for s in ('McCarthy REA','Imielinski/Lipski','Tamer','Caiani')])
    write('six-ledger-supplement.json',ledger)
    for name in ('source-dispositions.md','claim-successor.md','protocol-successor.md','reuse-successor.md'):
        check('substantive-note/'+name,(OUT/name).stat().st_size>1000)
    pins += [ROOT/'docs/plans/accounting-source-protocol-reuse-refresh-20261016.md',ROOT/'data/accounting-master/future-validation-20261015/protocol-ledger.md',ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt']
    write('input-lock.json',dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(set(pins))]))
    write('checks.json',dict(checks=len(checks),failures=0,detail=checks,scope='preservation and declared-metadata identity; not scientific or legal certification'))
    write('run-manifest.json',dict(recorded_utc=datetime.now(timezone.utc).isoformat(),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/source-protocol-reuse-refresh-20261016/prepare_records.py',environment=sys.executable+'; stdlib only; no package imports',gpu_status='intentionally hidden; no framework/device calls',random_seeds='N/A deterministic',data_version='source pins and exact release metadata',wall_seconds=round(time.monotonic()-start,3),plan='docs/plans/accounting-source-protocol-reuse-refresh-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),outputs=['dependency-frontier.json','candidate-chain.json','claim-source-index.json','six-ledger-supplement.json','input-lock.json','checks.json']))
    print(json.dumps(dict(checks=len(checks),failures=0,dependency_edges=len(edges),assessments=len(chain),source_notes=len(source_notes))))
if __name__=='__main__':main()
