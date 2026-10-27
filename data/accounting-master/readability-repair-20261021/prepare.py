"""Prepare a protected prose-only successor once. No runtime implementation."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'docs/design/proposal/manuscript-reserve-risk-20261020'
C = R / 'docs/design/proposal/manuscript-readability-20261021'
P = R / 'data/accounting-master/reserve-risk-integration-20261020'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not C.exists() and not (U / 'protection.json').exists()
assert sha(B / 'accounting-product-proposal.pdf') == '92b1ab24970cb301ba96d409edcadd3679fc778917c81e82b1c82da592e3dd0d'
assert load(P / 'regression/completion.json')['status'] == 'author_diagnosis_complete_repairs_required'
protected = dict(load(P / 'protection.json')['protected'])
protected.update(load(P / 'completion.json')['bindings'])
protected.update(load(P / 'regression/completion.json')['bindings'])
protected[str((P / 'regression/completion.json').relative_to(R))] = sha(P / 'regression/completion.json')
for name, digest in protected.items():
    assert sha(R / name) == digest, name
controls = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
    'docs/plans/accounting-mission-requirements.md', 'data/accounting-master/next-plan.md']
status = subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'],cwd=R,text=True)
rows = [x for x in status.split(chr(0)) if x]
assert all(x[:2] == ' M' for x in rows)
dirty = {x[3:]:sha(R / x[3:]) for x in rows}
protection = {'started_utc':datetime.now(timezone.utc).isoformat(),
    'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),
    'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),
    'index_sha256':sha(R / '.git/index'), 'tracked_dirty':dirty, 'controls':controls, 'protected':protected}
for name in controls:
    target = U / 'controls-before' / name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(R / name,target)
with (U / 'protection.json').open('x') as f:
    json.dump(protection,f,indent=2);f.write(chr(10))
replacements = [
    {'path':'accounting-product-proposal.tex','id':'version',
     'old':r'Version 3.45 (proposal candidate) quad 20 October 2026',
     'new':r'Version 3.46 (proposal candidate) quad 21 October 2026'},
    {'path':'sections/corporate-residuals.tex','id':'RR-001',
     'old':'The prior tax dossier already specifies tax bases, gross DTA/DTL, recoverability, rate changes and lease interaction; the error/estimate bridge retains equity origins. Uncertain tax treatment was genuinely deferred.',
     'new':'Uncertainty about whether a tax authority will accept a treatment affects both current tax and the tax bases used for deferred tax. The calculation must retain gross DTA/DTL, recoverability, rate changes, lease interactions and the original profit, OCI or equity allocation. It also needs a measurement decision about the uncertain treatment.'},
    {'path':'sections/corporate-methods.tex','id':'RR-002',
     'old':'The official lease compilation is dated December 2023 despite the older filename.',
     'new':'The official lease compilation is dated December 2023.'},
    {'path':'chapters/12-research.tex','id':'RR-003-library',
     'old':'The companion library contains 32 verified paper PDFs: 25 retrieved from'+chr(10)+'external sources and seven preserved copies from the original collection.',
     'new':'The initial research catalogue records 32 verified paper PDFs: 25 retrieved'+chr(10)+'from external sources and seven preserved copies from the original collection.'+chr(10)+'Later source inquiries retain additional papers and their technical reading'+chr(10)+'in separate versioned records, including the reserve-risk and bootstrap'+chr(10)+'studies used in Chapter~12. The initial count therefore describes that'+chr(10)+'catalogue, not the full expanded library.'},
    {'path':'chapters/12-research.tex','id':'RR-003-query',
     'old':'Every one of the 179 unique candidates in the acquired forward-query files'+chr(10)+'has an individual title/metadata relevance decision.',
     'new':'Each of the 179 unique candidates in the initial acquired forward-query'+chr(10)+'files has an individual title/metadata relevance decision. Later searches'+chr(10)+'retain their own bounded populations and relevance decisions.'}
]
C.mkdir()
files = []
diffs = []
for source in sorted(B.rglob('*')):
    if not source.is_file() or source.suffix not in ('.tex','.bib','.lark'):
        continue
    name = str(source.relative_to(B))
    dest = C / name
    dest.parent.mkdir(parents=True,exist_ok=True)
    original = source.read_text()
    updated = original
    for change in replacements:
        if change['path'] == name:
            assert updated.count(change['old']) == 1,change['id']
            updated = updated.replace(change['old'],change['new'],1)
    dest.write_text(updated)
    files.append({'path':name,'baseline_sha256':sha(source),'candidate_sha256':sha(dest),'changed':original!=updated})
    if original != updated:
        diffs.extend(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),fromfile='3.45/'+name,tofile='3.46/'+name))
with (U / 'source-lock.json').open('x') as f:
    json.dump({'baseline':str(B.relative_to(R)),'candidate':str(C.relative_to(R)),
        'files':files,'replacements':replacements},f,indent=2,ensure_ascii=False);f.write(chr(10))
with (U / 'source-delta.patch').open('x') as f:
    f.write(''.join(diffs))
print(json.dumps({'protected_files':len(protected),'sources':len(files),'changed':[x['path'] for x in files if x['changed']],
    'candidate':str(C.relative_to(R)),'tracked_dirty_preserved':len(dirty)}))
