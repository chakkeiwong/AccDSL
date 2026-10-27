"""Prepare, build and inspect the bounded 5.55 document successor."""
from collections import Counter
from datetime import datetime,timezone
import difflib
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

D=Path(__file__).resolve().parent;R=D.parents[3]
B=R/'docs/design/proposal/manuscript-financing-v554r2p2-20261027'
T=R/'docs/design/proposal/manuscript-sector-v555-20261027'
NAMES=['accounting-product-proposal','simulation-foundations']
CHANGED={'README.md','DEPENDENCIES.md','PACKAGE-REVISION.json',
         'accounting-product-proposal.tex','simulation-foundations.tex',
         'chapters/16-insurance.tex','sections/company-family-language.tex','sections/exact-bank-profile.tex'}
INSERTS={
    'chapters/16-insurance.tex':('\\input{sections/insurance-paa-dated-case}\n\n',
                               'Longer-duration business adds a fulfilment-cash-flow vector,'),
    'sections/company-family-language.tex':('\\input{sections/insurance-paa-dated-interface}\n\n',
                                             '\\paragraph{Map an exact insurer schedule into a proposed book.}'),
    'sections/exact-bank-profile.tex':('\n\\input{sections/bank-interface-boundaries}\n',None)}
digest=lambda p:sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def dump(path,value):
    with path.open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write(chr(10))

def prepare():
    assert not T.exists()
    assert (R/'docs/AccDSL-latest.pdf').resolve()==B/(NAMES[0]+'.pdf')
    manifest=read(B/'package-manifest.json')
    for row in manifest['files']:assert digest(B/row['path'])==row['sha256'],row['path']
    T.mkdir()
    for row in manifest['files']:
        if Path(row['path']).suffix=='.pdf':continue
        target=T/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(B/row['path'],target)
    for name in NAMES:
        p=T/(name+'.tex');s=p.read_text();assert s.count('Version 5.54-R2 ')==1
        p.write_text(s.replace('Version 5.54-R2 ','Version 5.55 ',1))
    for path,(addition,anchor) in INSERTS.items():
        p=T/path;s=p.read_text()
        if anchor is None:s+=addition
        else:assert s.count(anchor)==1;s=s.replace(anchor,addition+anchor,1)
        p.write_text(s)
    added=[]
    for name in ['insurance-paa-dated-case.tex','insurance-paa-dated-interface.tex','bank-interface-boundaries.tex']:
        dest=T/'sections'/name;shutil.copyfile(D/name,dest);added.append(str(dest.relative_to(T)))
    components=[
        dict(id='insurance-paa-dated-book',unit='insurance-paa-dated-book-20261027',
             archive='paa-dated-book-bundle.tar.gz',driver='verify.py',root_argument=False,
             notes=['contract.md','source-note.md','result.md','README.md','preservation.json','acceptance-supplement.json','complete-record-checks.json']),
        dict(id='bank-interfaces',unit='bank-interface-consolidation-20261027',
             archive='bank-interface-bundle.tar.gz',driver='replay.py',root_argument=True,
             notes=['compatibility-map.md','execution-audit.md','result.md','README.md','preservation.json','acceptance-supplement.json'])]
    for component in components:
        source=R/'data/accounting-master'/component['unit'];dest=T/'companions'/component['id'];dest.mkdir()
        assert read(source/'preservation.json')['passed']
        for name in [component['archive'],*component['notes']]:shutil.copyfile(source/name,dest/name)
        shutil.copyfile(D/'unpack.py',dest/'unpack.py')
        entries={}
        with tarfile.open(dest/component['archive'],'r:gz') as archive:
            for member in archive.getmembers():
                assert member.isfile() and not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
                raw=archive.extractfile(member).read()
                assert member.name not in entries
                entries[member.name]=dict(sha256=sha256(raw).hexdigest(),bytes=len(raw))
        meta=dict(archive=component['archive'],archive_sha256=digest(dest/component['archive']),entries=entries,
                  driver='data/accounting-master/'+component['unit']+'/'+component['driver'],
                  root_argument=component['root_argument'],rights='internal only')
        dump(dest/'component.json',meta)
        (dest/'RUN.md').write_text(
            '# Reproduce this internal component\n\n'
            'From this directory, use an absolute new destination:\n\n'
            '    python3 -I -B unpack.py --destination /tmp/accdsl-new-'+component['id']+'\n\n'
            'Run the printed next_command. It writes output-01 inside the copy.\n'
            'Use the recorded Python3.11/jsonschema4.26.0 environment; no installation\n'
            'is performed. The driver hides GPU devices and leaves original inputs\n'
            'unchanged. See README.md and result.md for comparison scope and limits.\n'
            'The source materials remain internal; reproduction is not redistribution\n'
            'clearance, independent domain acceptance or full runtime closure.\n')
        added += [str(p.relative_to(T)) for p in dest.iterdir()]
    (T/'README.md').write_text(
        '# AccDSL 5.55 — sector interfaces\n\n'
        'This protected successor preserves the5.54-R2 package revision2 and adds\n'
        'the dated premium-allocation book/report connection and explicit bank\n'
        'profile boundaries. The candidate remains not_ready; independent reader,\n'
        'domain, implementation and whole-document acceptance remain open.\n\n'
        'Run python3 -I -B verify_package.py here to check declared package bytes.\n'
        'Build the two TeX roots with LuaLaTeX through latexmk in the retained\n'
        'TeX Live2026 environment, using a private writable TEXMFVAR/TEXMFCACHE.\n'
        'No dependency installation or publication is implied.\n\n'
        'Six companions now accompany the specification:\n\n'
        '| Component | Scope | Instructions |\n| --- | --- | --- |\n'
        '| Historical Core0 | Historical language/reference fixtures | companions/historical-core0/README.md |\n'
        '| Selected term program | Bounded term execution | companions/selected-term/README.md |\n'
        '| Refinancing domain | Conditional cash identities and counterexamples | companions/refinancing-domain/README.md |\n'
        '| Source/history/opening/report |37 retained exchanges | companions/source-history-replay/README.md |\n'
        '| Dated PAA book | Seven conditional cases and21 controls | companions/insurance-paa-dated-book/RUN.md |\n'
        '| Bank interfaces | Separate AU/US and exact-time profiles | companions/bank-interfaces/RUN.md |\n\n'
        'Each component retains its own assumptions and comparison contract.\n'
        'Use a fresh output directory; never run archived one-shot writers.\n'
        'The bank replay excludes historical Git/index preservation and checks\n'
        'declared copied inputs instead; this distinction is explicit in its notes.\n'
        'All materials are for internal preparation. Original source rights,\n'
        'current applicability, clean installation and other runtimes remain separate.\n'
        'Evidence paths beginning data/, docs/ or scripts/ refer to the AccDSL\n'
        'repository layout reconstructed by the relevant archive, where included.\n'
        'DEPENDENCIES.md and PACKAGE-REVISION.json preserve version and access limits.\n')
    p=T/'DEPENDENCIES.md'
    p.write_text(p.read_text()+'\n## Sector interfaces in5.55\n\n'
        'The dated PAA and bank companion archives are included by exact identity.\n'
        'Their RUN.md files provide checked extraction and execution steps for a\n'
        'new directory. They retain historical sources for internal preparation;\n'
        'their inclusion does not establish redistribution rights. Neither archive\n'
        'supplies an actual source/accounting admission or a production service.\n'
        'All prior companions and source qualifications remain preserved.\n')
    (T/'PACKAGE-REVISION.json').write_text(json.dumps(dict(manuscript_edition='5.55',package_revision=1,
        release_status='not_ready',predecessor_package=str(B.relative_to(R)),
        predecessor_manifest_sha256=digest(B/'package-manifest.json'),
        prior_revision_record=read(B/'PACKAGE-REVISION.json'),
        added_components=[x['id'] for x in components],
        integration_plan='docs/plans/accounting-sector-interface-integration-20261027.md'),indent=2)+chr(10))
    dump(D/'baseline.json',dict(baseline=str(B.relative_to(R)),candidate=str(T.relative_to(R)),files=manifest['files'],
        manifest_sha256=digest(B/'package-manifest.json'),allowed_changes=sorted(CHANGED),added_files=sorted(added),
        timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(dict(prepared=True,added=len(added))))

def build(name,copy=False):
    assert name in NAMES
    folder=D/('relocation-01' if copy else ('build-03' if name==NAMES[0] else 'build-01'));folder.mkdir(exist_ok=True)
    target=Path(read(folder/'location.json')['target']) if copy else T
    log=folder/(name+'.stdout');record=folder/(name+'-build.json')
    assert not log.exists() and not record.exists()
    cache=target/'.tex-cache';cache.mkdir(exist_ok=True)
    env=dict(os.environ,TEXMFVAR=str(cache),TEXMFCACHE=str(cache),CUDA_VISIBLE_DEVICES='-1')
    command=['latexmk','-g','-lualatex','-interaction=nonstopmode','-halt-on-error','-no-shell-escape',name+'.tex']
    start=time.monotonic()
    with log.open('x') as f:result=subprocess.run(command,cwd=target,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
    dump(record,dict(command=command,cwd=str(target),exit_code=result.returncode,wall_seconds=time.monotonic()-start,
        environment={k:env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},
        timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable; unusable marker',
        plan='docs/plans/accounting-sector-interface-integration-20261027.md'))
    print(json.dumps(dict(document=name,copied=copy,exit_code=result.returncode,wall_seconds=time.monotonic()-start)))
    raise SystemExit(result.returncode)

def verify():
    import fitz
    base=read(D/'baseline.json');checks=[];changed=[];delta=[]
    def ck(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for row in base['files']:
        a,b=B/row['path'],T/row['path']
        ck('baseline:'+row['path'],digest(a)==row['sha256'])
        if a.suffix!='.pdf' and digest(b)!=row['sha256']:
            changed.append(row['path'])
            delta.extend(difflib.unified_diff(a.read_text().splitlines(True),b.read_text().splitlines(True),
                fromfile='5.54-R2/'+row['path'],tofile='5.55/'+row['path']))
    ck('exact_change_set',set(changed)==CHANGED,changed)
    for path,(addition,_) in INSERTS.items():
        text=(T/path).read_text()
        prior=(B/path).read_text()
        if path=='sections/company-family-language.tex':
            prior=prior.replace('A separate retained insurer calculation supplies the missing posting example.',
                'A different retained insurer calculation illustrates a loss-component posting sequence.')
            prior=prior.replace('This is a different synthetic case from the resolved\nassessment above.',
                'This is a different synthetic case from both the resolved\nassessment and the premium-allocation example above.')
        ck('all_prior_text_preserved_except_explicit_transition:'+path,text.count(addition)==1 and text.replace(addition,'',1)==prior)
    for name in ['insurance-paa-dated-case.tex','insurance-paa-dated-interface.tex','bank-interface-boundaries.tex']:
        ck('exact_authored_addition:'+name,(T/'sections'/name).read_bytes()==(D/name).read_bytes())
    volumes=[];rendered=[];folder=D/'rendered-02';folder.mkdir(exist_ok=False)
    for name in NAMES:
        ck('successful_build:'+name,read(D/('build-03' if name==NAMES[0] else 'build-01')/(name+'-build.json'))['exit_code']==0)
        log=(T/(name+'.log')).read_text(errors='replace')
        ck('no_undefined_or_overfull:'+name,not re.search(r'undefined|Overfull|multiply defined',log,re.I))
        doc=fitz.open(T/(name+'.pdf'));ck('cover_version:'+name,'5.55' in doc[0].get_text())
        pages={1}
        if name==NAMES[0]:
            needles=['Put the cohort on an explicit calendar','Carry the premium-allocation groups',
                     'Keep accounting profiles and capital assessments','InsurancePAADatedBook/1',
                     'companions/bank-interfaces/']
            for i,page in enumerate(doc):
                text=page.get_text()
                if any(needle in text for needle in needles):
                    pages.update(range(max(1,i),min(len(doc),i+3)+1))
        for page in sorted(pages):
            dest=folder/(name+f'-{page:04}.png')
            doc[page-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(dest)
            rendered.append(dict(document=name,page=page,image=str(dest.relative_to(R)),sha256=digest(dest)))
        volumes.append(dict(document=name,pages=len(doc),pdf_sha256=digest(T/(name+'.pdf'))))
    ck('unchanged_simulation_chapters',all((T/p.relative_to(B)).read_bytes()==p.read_bytes() for p in (B/'simulation').glob('*.tex')))
    (D/'source-delta-02.patch').write_text(''.join(delta))
    dump(D/'rendered-pages-02.json',rendered)
    report=dict(passed=all(x['passed'] for x in checks),checks=checks,volumes=volumes,changed=changed)
    dump(D/'verification-02.json',report)
    print(json.dumps(dict(passed=report['passed'],checks=len(checks),volumes=volumes,rendered=len(rendered),
                          failed=[r for r in checks if not r['passed']])))

if __name__=='__main__':
    action=sys.argv[1]
    if action=='prepare':prepare()
    elif action=='build':build(sys.argv[2],len(sys.argv)>3 and sys.argv[3]=='copy')
    elif action=='verify':verify()
