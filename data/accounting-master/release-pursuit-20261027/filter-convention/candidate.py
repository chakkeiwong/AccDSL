"""Stage and check a bounded document successor without mutating its parents."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time

D = Path(__file__).resolve().parent
R = D.parents[3]
B = R / 'docs/design/proposal/manuscript-selected-history-v554-20261027'
T = R / 'docs/design/proposal/manuscript-filter-v554r1-20261027'
NAMES = ['accounting-product-proposal', 'simulation-foundations']
CHANGED = {'README.md', 'accounting-product-proposal.tex',
           'simulation-foundations.tex', 'simulation/09-approximation.tex'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def prepare():
    assert not T.exists() and not (D / 'candidate-baseline.json').exists()
    assert (R / 'docs/AccDSL-latest.pdf').resolve() == B / (NAMES[0]+'.pdf')
    assert read(D / 'exact-check.json')['passed']
    assert sha(B / 'simulation/09-approximation.tex') == read(D / 'source-identity.json')['baseline_sha256']
    manifest = read(B / 'package-manifest.json')
    assert len(manifest['files']) == 411
    T.mkdir()
    for row in manifest['files']:
        source = B / row['path']
        assert sha(source) == row['sha256'] and source.stat().st_size == row['bytes']
        if source.suffix != '.pdf':
            dest = T / row['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(source.read_bytes())
    (T / 'simulation/09-approximation.tex').write_bytes((D / '09-approximation.tex').read_bytes())
    for name in NAMES:
        p = T / (name+'.tex')
        text = p.read_text()
        assert text.count('Version 5.54 ') == 1
        p.write_text(text.replace('Version 5.54 ', 'Version 5.54-R1 ', 1))
    p = T / 'README.md'
    text = p.read_text().replace('# AccDSL 5.54 selected-history candidate', '# AccDSL 5.54-R1 particle-weight clarification')
    text = text.replace('This is a protected successor to 5.53-R1.', 'This is a protected successor to 5.54.')
    text += '''
Version 5.54-R1 distinguishes sequential importance weights from weights after
ancestor resampling. It preserves the earlier weight equation, derives the
ancestor-proposal ratio and illustrates double counting with two persistent
contract types. Exact arithmetic and source reading are recorded under
data/accounting-master/release-pursuit-20261027/filter-convention/.
This is a manuscript clarification, not a new filtering implementation or a
claim of exact finite-sample inference. All source/history additions and prior
coupling/opening corrections remain. The successor needs its own source,
rendered-page, package and relocation evidence; broad acceptance stays open.
'''
    p.write_text(text)
    dump(D / 'candidate-baseline.json', {'baseline': str(B.relative_to(R)),
         'candidate': str(T.relative_to(R)), 'manifest_sha256': sha(B / 'package-manifest.json'),
         'files': manifest['files'], 'allowed_changes': sorted(CHANGED),
         'timestamp_utc': datetime.now(timezone.utc).isoformat()})
    print(json.dumps({'prepared': True, 'candidate': str(T), 'files': len(manifest['files'])}))


def build(name, relocated=False):
    assert name in NAMES
    folder = D / ('relocation-01' if relocated else 'build-02')
    folder.mkdir(exist_ok=True)
    target = Path(read(D / 'relocation-01/location.json')['target']) if relocated else T
    log = folder / (name+'.stdout')
    result = folder / (name+'-build.json')
    assert not log.exists() and not result.exists()
    cache = target / '.tex-cache'
    cache.mkdir(exist_ok=True)
    env = dict(os.environ, TEXMFVAR=str(cache), TEXMFCACHE=str(cache), CUDA_VISIBLE_DEVICES='-1')
    cmd = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode',
           '-halt-on-error', '-no-shell-escape', name+'.tex']
    start = time.monotonic()
    with log.open('w') as f:
        p = subprocess.run(cmd, cwd=target, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=240)
    report = {'command': cmd, 'cwd': str(target), 'exit_code': p.returncode,
        'wall_seconds': time.monotonic()-start, 'python': sys.version, 'platform': platform.platform(),
        'environment': {k: env[k] for k in ['TEXMFVAR','TEXMFCACHE','CUDA_VISIBLE_DEVICES']},
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': 'unavailable; unusable marker', 'seed': 'N/A deterministic document build',
        'plan': str((D / 'plan.md').relative_to(R))}
    dump(result, report)
    print(json.dumps({'name': name, 'relocated': relocated, 'exit_code': p.returncode,
                      'wall_seconds': report['wall_seconds']}))
    raise SystemExit(p.returncode)


def verify():
    import fitz
    assert not (D / 'candidate-verification-02.json').exists()
    base = read(D / 'candidate-baseline.json')
    checks, changed, delta = [], [], []
    def ck(name, passed, detail=None):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    for row in base['files']:
        a, b = B / row['path'], T / row['path']
        ck('baseline:'+row['path'], sha(a) == row['sha256'])
        if a.suffix != '.pdf' and sha(b) != row['sha256']:
            changed.append(row['path'])
            delta.extend(difflib.unified_diff(a.read_text().splitlines(True), b.read_text().splitlines(True),
                fromfile='5.54/'+row['path'], tofile='5.54-R1/'+row['path']))
    ck('exact_change_set', set(changed) == CHANGED, changed)
    section = (T / 'simulation/09-approximation.tex').read_text()
    ck('exact_reviewed_chapter', section == (D / '09-approximation.tex').read_text())
    old = (B / 'simulation/09-approximation.tex').read_text()
    pattern = r'\\begin\{(equation\*?|align\*?|gather\*?)\}.*?\\end\{\1\}'
    old_eq = [m.group() for m in re.finditer(pattern, old, re.S)]
    new_eq = [m.group() for m in re.finditer(pattern, section, re.S)]
    ck('all_original_displays_retained', not (Counter(old_eq)-Counter(new_eq)))
    ck('one_derived_display_added', len(new_eq) == len(old_eq)+1)
    citation = r'\\cite[a-zA-Z]*\*?(?:\[[^]]*\])*\{([^}]+)\}'
    ck('all_original_citations_retained', not (Counter(re.findall(citation,old))-Counter(re.findall(citation,section))))
    ck('all_exact_checks_pass', read(D / 'exact-check.json')['passed'])
    volumes, rendered = [], []
    out = D / 'rendered-02'
    out.mkdir(exist_ok=True)
    for name in NAMES:
        ck('successful_build:'+name, read(D / 'build-02' / (name+'-build.json'))['exit_code'] == 0)
        doc = fitz.open(T / (name+'.pdf'))
        log = (T / (name+'.log')).read_text(errors='replace')
        ck('resolved_clean_log:'+name, not re.search(r'undefined|Overfull|multiply defined',log,re.I))
        ck('version:'+name, '5.54-R1' in doc[0].get_text())
        toc = doc.get_toc()
        start = next(x[2] for x in toc if x[1].startswith('9 '))
        stop = next(x[2] for x in toc if x[1].startswith('10 '))
        pages = {1, start, stop}
        if name == NAMES[0]:
            pages.update(range(start,stop))
        else:
            pages.update(i+1 for i,p in enumerate(doc) if 'ancestor' in p.get_text() and start<=i+1<stop)
        for n in sorted(pages):
            p = out / f'{name}-{n:04}.png'
            doc[n-1].get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(p)
            rendered.append({'volume':name,'page':n,'path':str(p.relative_to(R)),
                             'pdf_sha256':sha(T/(name+'.pdf')),'review':'not_yet_viewed'})
        clipping = []
        for i,page in enumerate(doc):
            for w in page.get_text('words'):
                if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:
                    clipping.append({'page':i+1,'word':w[4]})
        ck('page_rectangle_bounds:'+name, not clipping, clipping[:10])
        volumes.append({'name':name,'pages':len(doc),'sha256':sha(T/(name+'.pdf')),
                        'chapter9_physical_pages':list(range(start,stop))})
    dump(D / 'candidate-verification-02.json', {'passed':all(x['passed'] for x in checks),
         'checks':checks,'volumes':volumes,'changed_files':changed,
         'scope':'Source integrity, preservation and build/layout diagnostics; author and independent acceptance separate.'})
    dump(D / 'rendered-pages-02.json', rendered)
    (D / 'candidate-source-delta-02.patch').write_text(''.join(delta))
    print(json.dumps({'passed':all(x['passed'] for x in checks),'checks':len(checks),
          'failures':[x for x in checks if not x['passed']], 'volumes':volumes,
          'rendered':[(x['volume'],x['page']) for x in rendered]}))
    raise SystemExit(0 if all(x['passed'] for x in checks) else 1)


def package():
    assert not (D / 'package-record.json').exists()
    assert read(D / 'candidate-verification-02.json')['passed']
    review = read(D / 'rendered-review.json')
    for row in review['pages']:
        assert sha(T / (row['volume']+'.pdf')) == row['pdf_sha256']
    manifest = read(B / 'package-manifest.json')
    manifest.update(candidate='5.54-R1;not_ready', manifest_self_hash=
        'Stored outside this package in release-pursuit-20261027/filter-convention/package-record.json')
    for row in manifest['files']:
        p = T / row['path']
        assert p.is_file() and not p.is_symlink()
        row.update(sha256=sha(p),bytes=p.stat().st_size)
    dump(T / 'package-manifest.json', manifest)
    p = subprocess.run(['python3','-I','-B','verify_package.py'],cwd=T,capture_output=True,text=True,timeout=30)
    assert p.returncode == 0, p.stdout+p.stderr
    dump(D / 'package-record.json', {'candidate':'5.54-R1;not_ready',
        'manifest_sha256':sha(T/'package-manifest.json'), 'predecessor_manifest_sha256':sha(B/'package-manifest.json'),
        'files':len(manifest['files']), 'verification':json.loads(p.stdout),
        'source_verification_sha256':sha(D/'candidate-verification-02.json'),
        'rendered_review_sha256':sha(D/'rendered-review.json'),
        'full_evidence_closure':False, 'rights':'Existing internal-only dispositions retained'})
    print(json.dumps({'passed':True,'files':len(manifest['files'])}))


def relocate_prepare():
    out = D / 'relocation-01'
    out.mkdir(exist_ok=False)
    target = Path(tempfile.mkdtemp(prefix='accdsl-v554r1-relocation-',dir='/tmp'))
    manifest = read(T / 'package-manifest.json')
    assert sha(T / 'package-manifest.json') == read(D / 'package-record.json')['manifest_sha256']
    for row in manifest['files']:
        p, q = T / row['path'], target / row['path']
        assert sha(p) == row['sha256']
        q.parent.mkdir(parents=True,exist_ok=True)
        q.write_bytes(p.read_bytes())
    (target/'package-manifest.json').write_bytes((T/'package-manifest.json').read_bytes())
    dump(out/'location.json', {'target':str(target),'manifest_sha256':sha(T/'package-manifest.json')})
    print(json.dumps({'prepared':True,'target':str(target)}))


def relocate_verify():
    import fitz
    out = D / 'relocation-01'
    assert not (out/'result.json').exists()
    target = Path(read(out/'location.json')['target'])
    reports = []
    for name in NAMES:
        assert read(out/(name+'-build.json'))['exit_code'] == 0
        a,b = fitz.open(T/(name+'.pdf')),fitz.open(target/(name+'.pdf'))
        assert len(a)==len(b)
        assert all(' '.join(x.get_text().split())==' '.join(y.get_text().split()) for x,y in zip(a,b))
        log = (target/(name+'.log')).read_text(errors='replace')
        assert not re.search(r'undefined|Overfull|multiply defined',log,re.I)
        inputs = set()
        for line in (target/(name+'.fls')).read_text().splitlines():
            if line.startswith('INPUT '):
                p=Path(line[6:]);inputs.add(str((target/p).resolve() if not p.is_absolute() else p.resolve()))
        assert not [p for p in inputs if p.startswith(str(R)+'/')]
        external = sorted(p for p in inputs if not p.startswith(str(target)+'/'))
        dump(out/(name+'-external-inputs.json'),external)
        reports.append({'name':name,'pages':len(a),'all_page_text_equal':True,
                        'source_sha256':sha(T/(name+'.pdf')),'relocated_sha256':sha(target/(name+'.pdf')),
                        'external_environment_files':len(external),'hidden_original_worktree_inputs':[]})
    dump(out/'result.json',{'passed':True,'documents':reports,
        'scope':'Document package in existing environment; no full executable closure or independent installation claim.'})
    print(json.dumps({'passed':True,'documents':reports}))


if __name__ == '__main__':
    action = sys.argv[1]
    if action in ['build','relocate-build']:
        build(sys.argv[2], action=='relocate-build')
    else:
        {'prepare':prepare,'verify':verify,'package':package,
         'relocate-prepare':relocate_prepare,'relocate-verify':relocate_verify}[action]()
