"""Prepare the seven bounded repairs without altering their baseline."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / 'docs/design/proposal/manuscript-readability-20261021'
C = R / 'docs/design/proposal/manuscript-readability-20261022'
P = R / 'data/accounting-master/readability-repair-20261021'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
assert not C.exists() and not (U / 'protection.json').exists()
assert sha(B / 'accounting-product-proposal.pdf') == '4a516701b3105ea778807f7143eb4d457f6d18cd439d8fc7172e1d9506cd1be5'
assert load(P / 'regression/completion.json')['status'] == 'author_diagnosis_complete_repairs_required'
protected = dict(load(P / 'protection.json')['protected'])
for completion in (P / 'completion.json', P / 'regression/completion.json'):
    protected.update(load(completion)['bindings'])
    protected[str(completion.relative_to(R))] = sha(completion)
for name, digest in protected.items():
    assert sha(R / name) == digest, name

replacements = [
    dict(path='accounting-product-proposal.tex', id='version',
         old=r'Version 3.46 (proposal candidate) \quad 21 October 2026',
         new=r'Version 3.47 (proposal candidate) \quad 22 October 2026'),
    dict(path='chapters/13-reference-company.tex', id='RR346-001',
         old='The earlier case annotation that described the reported\ncash balance as excluding restricted cash was wrong relative to this footnote.',
         new='Interpreting the reported cash balance as excluding the escrow\nis wrong relative to this footnote.'),
    dict(path='chapters/03-literature.tex', id='RR346-002',
         old="2024 thesis; the original collection's filename misleadingly suggests 2026.",
         new='2024 thesis.'),
    dict(path='chapters/03-literature.tex', id='RR346-003',
         old='Ahn, not the later Jensen--Snodgrass paper initially returned by a search.',
         new='Ahn (1986).'),
    dict(path='chapters/06-language.tex', id='RR346-004-reference',
         old='The proposed portable compilation sequence is specified separately in\nSection~\\ref{sec:portable-record}.',
         new='The proposed portable compilation sequence is specified separately in\nSection~\\ref{sec:portable-authoring}.'),
    dict(path='sections/portable-values.tex', id='RR346-004-target',
         old='\\section{The first company profile and its authoring boundary}\n',
         new='\\section{The first company profile and its authoring boundary}\n\\label{sec:portable-authoring}\n'),
    dict(path='sections/standards-methods.tex', id='RR346-005',
         old='AASB 112 compilation 7 is 29 September 2023. Their filenames are not date evidence.',
         new='AASB 112 compilation 7 is 29 September 2023.'),
    dict(path='sections/standards-methods.tex', id='RR346-006',
         old='\\citep{moflease2018,mofasbe21}. They replace the earlier secondary reproduction as support for the inspected wording.',
         new='\\citep{moflease2018,mofasbe21}.'),
    dict(path='sections/instrument-reduction.tex', id='RR346-007',
         old='Applying the earlier matched-\nportion method would instead remove purchase units and change the target.',
         new='Applying the matched purchase-portion method in the following\nSection~\\ref{sec:partial-hedge-discontinuation} would instead remove purchase\nunits and change the target.')
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
assert all(x[:2] == ' M' for x in rows)
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
                                        fromfile='3.46/' + name, tofile='3.47/' + name))
with (U / 'source-lock.json').open('x') as f:
    json.dump(dict(baseline=str(B.relative_to(R)), candidate=str(C.relative_to(R)),
                   files=files, replacements=replacements), f, indent=2)
    f.write('\n')
with (U / 'source-delta.patch').open('x') as f:
    f.write(''.join(diffs))
print(json.dumps(dict(protected_files=len(protected), sources=len(files),
                      changed=[x['path'] for x in files if x['changed']], tracked_dirty_preserved=len(rows))))
