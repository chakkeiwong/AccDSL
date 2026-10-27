"""Create the protected Version 3.48 notation repair once."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/readability-repair-20261022'
B = R / 'docs/design/proposal/manuscript-readability-20261022'
C = R / 'docs/design/proposal/manuscript-readability-20261022-theta'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not C.exists() and not (U / 'protection.json').exists()
assert sha(B / 'accounting-product-proposal.pdf') == 'b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db'
assert load(P / 'regression/completion.json')['status'] == 'author_diagnosis_complete_repairs_required'
protected = dict(load(P / 'protection.json')['protected'])
for completion in (P / 'completion.json', P / 'regression/completion.json'):
    for name, digest in load(completion)['bindings'].items():
        assert name not in protected or protected[name] == digest, name
        protected[name] = digest
    protected[str(completion.relative_to(R))] = sha(completion)
for name, digest in protected.items():
    assert sha(R / name) == digest, name

replacements = [
    dict(path='accounting-product-proposal.tex', id='version',
         old=r'Version 3.47 (proposal candidate) \quad 22 October 2026',
         new=r'Version 3.48 (proposal candidate) \quad 22 October 2026'),
    dict(path='chapters/05-mathematics.tex', id='R347-D01',
         old='$\\varepsilon_t$ future innovations. A behavioural policy $\\pi$ chooses\n$a_t$ using the permitted information $\\mathcal{F}_t$:',
         new='$\\varepsilon_t$ future innovations. Let $\\theta$ denote the declared\nbehavioural and event-generation parameters, with values specified by the chosen\nhistory, scenario and model assumptions. A behavioural policy $\\pi$ chooses\n$a_t$ using the permitted information $\\mathcal{F}_t$:')
]
sources = sorted(p for p in B.rglob('*') if p.is_file() and p.suffix in ('.tex', '.bib', '.lark'))
assert len(sources) == 144
prepared = []
for source in sources:
    name = str(source.relative_to(B))
    original = source.read_text()
    updated = original
    for change in replacements:
        if change['path'] == name:
            assert updated.count(change['old']) == 1, change['id']
            updated = updated.replace(change['old'], change['new'], 1)
    prepared.append((name, original, updated))
assert set(x['path'] for x in replacements) <= {x[0] for x in prepared}
controls = ['docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md',
            'docs/plans/accounting-mission-requirements.md', 'data/accounting-master/next-plan.md']
status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no', '-z'], cwd=R, text=True)
rows = [x for x in status.split('\0') if x]
assert len(rows) == 36 and all(x[:2] == ' M' for x in rows)
protection = dict(started_utc=datetime.now(timezone.utc).isoformat(),
    head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip(),
    branch=subprocess.check_output(['git', 'branch', '--show-current'], cwd=R, text=True).strip(),
    index_sha256=sha(R / '.git/index'), tracked_dirty={x[3:]: sha(R / x[3:]) for x in rows},
    controls=controls, protected=protected)
for name in controls:
    target = U / 'controls-before' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(R / name, target)
with (U / 'protection.json').open('x') as f:
    json.dump(protection, f, indent=2)
    f.write('\n')
C.mkdir()
files, diffs = [], []
for name, original, updated in prepared:
    dest = C / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(updated)
    files.append(dict(path=name, baseline_sha256=sha(B / name), candidate_sha256=sha(dest), changed=original != updated))
    if original != updated:
        diffs.extend(difflib.unified_diff(original.splitlines(True), updated.splitlines(True),
                                        fromfile='3.47/' + name, tofile='3.48/' + name))
with (U / 'source-lock.json').open('x') as f:
    json.dump(dict(baseline=str(B.relative_to(R)), candidate=str(C.relative_to(R)),
                   files=files, replacements=replacements), f, indent=2)
    f.write('\n')
with (U / 'source-delta.patch').open('x') as f:
    f.write(''.join(diffs))
print(json.dumps(dict(protected_files=len(protected), sources=len(files),
                      changed=[x['path'] for x in files if x['changed']], tracked_dirty_preserved=len(rows))))
