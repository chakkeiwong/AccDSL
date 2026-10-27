"""Protect evidence and copy inspected review tooling, without reading credit."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

U = Path(__file__).resolve().parent
R = U.parents[3]
P = R / 'data/accounting-master/r03-eps-additivity-boundary-20261022'
T = R / 'data/accounting-master/readability-repair-20261022/regression'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))

assert not (U / 'protection.json').exists() and not (U / 'structure-ledger.json').exists()
protected = dict(load(P / 'protection.json')['protected'])
for name, digest in load(P / 'completion.json')['bindings'].items():
    assert name not in protected or protected[name] == digest, name
    protected[name] = digest
protected[rel(P / 'completion.json')] = sha(P / 'completion.json')
for name, digest in protected.items():
    assert sha(R / name) == digest, name
rows = [x for x in subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=no','-z'], cwd=R, text=True).split('\0') if x]
assert len(rows) == 36 and all(x[:2] == ' M' for x in rows)
controls = load(P / 'protection.json')['controls']
protection = dict(started_utc=datetime.now(timezone.utc).isoformat(),
    head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=R, text=True).strip(),
    branch=subprocess.check_output(['git','branch','--show-current'], cwd=R, text=True).strip(),
    index_sha256=sha(R / '.git/index'), tracked_dirty={x[3:]:sha(R / x[3:]) for x in rows},
    controls=controls, protected=protected)
for name in controls:
    target = U / 'controls-before' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(R / name, target)
replacements = [
    ('manuscript-readability-20261022"', 'manuscript-readability-20261022-theta"'),
    ('b8003bfde4755e171f057588679b6b7a3cedf95685342e6ca438408e34bdd8db', '6a2acd8e3e01e6127eb89112a168216ee12b3244b3e56c814f1d2d1c56b90f0e'),
    ('AccDSL Version 3.47', 'AccDSL Version 3.48')]
source = (T / 'reading_inventory.py').read_text()
for old, new in replacements:
    assert source.count(old) == 1, old
    source = source.replace(old, new, 1)
assert not (U / 'reading_inventory.py').exists()
(U / 'reading_inventory.py').write_text(source)
for name in ('author_segment.py','record_synthesis.py'):
    assert not (U / name).exists()
    shutil.copy2(T / name, U / name)
with (U / 'protection.json').open('x') as f:
    json.dump(protection, f, indent=2)
    f.write('\n')
with (U / 'tooling-manifest.json').open('x') as f:
    json.dump(dict(scope='Tools only; no reading credit copied', replacements=replacements,
        files=[dict(name=n, baseline_sha256=sha(T/n), current_sha256=sha(U/n))
               for n in ('reading_inventory.py','author_segment.py','record_synthesis.py')]), f, indent=2)
    f.write('\n')
with (U / 'synthesis-ledger.json').open('x') as f:
    json.dump(dict(status='in_progress', candidate_pdf='docs/design/proposal/manuscript-readability-20261022-theta/accounting-product-proposal.pdf',
        pdf_sha256=replacements[1][1], chapter_regressions=[], cumulative_prefixes=[], document_synthesis=None,
        independent_reader='pending', human_acceptance='pending'), f, indent=2)
    f.write('\n')
with (U / 'run-manifest.json').open('x') as f:
    json.dump(dict(started_utc=protection['started_utc'], git_commit=protection['head'], environment=sys.executable,
        cpu_gpu='CPU only; GPU devices intentionally hidden', seeds='N/A deterministic document review',
        data_version='Exact frozen Version 3.48, 401 pages', wall_time='Open review; not one continuous timed run',
        plan='docs/plans/accounting-readability-regression-20261022-theta.md', result=rel(U/'document-synthesis.md'),
        command_prefix=['env','CUDA_VISIBLE_DEVICES=-1',sys.executable,'-B'],
        executed_setup=rel(U/'setup.py'), recording_policy='Actual ordered images precede each authored segment; no inherited reading credit'), f, indent=2)
    f.write('\n')
print(json.dumps(dict(protected_files=len(protected), tools_copied=3, judgments_copied=0)))
