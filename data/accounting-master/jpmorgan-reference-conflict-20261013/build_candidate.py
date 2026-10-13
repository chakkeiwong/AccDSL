"""Create the separate Version 2.53 manuscript from a protected baseline."""
import datetime
import difflib
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / 'docs/design/proposal/manuscript-intragroup-fx-20261013'
CAND = ROOT / 'docs/design/proposal/manuscript-reference-conflict-20261013'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(name, data):
    (UNIT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def expected_text(rel):
    text = (BASE / rel).read_text()
    if rel == 'accounting-product-proposal.tex':
        assert text.count('Version 2.52 (proposal candidate)') == 1
        return text.replace('Version 2.52 (proposal candidate)', 'Version 2.53 (proposal candidate)')
    if rel != 'sections/source-admission.tex':
        return text
    marker = '\\section{Three meanings of disclosure coverage}'
    assert text.count(marker) == 1
    text = text.replace(marker, (UNIT / 'reference-addition.tex').read_text() + marker)
    text = text.replace('The source preparation retains six located Apple policy passages:',
                        'The initial source preparation retains six located Apple policy passages:')
    old = '''The Apple annual/interim preparation inventories 125 quantities, 13 annual notes,
10 interim notes, 70 exhibit references and seven further package obligations.
All 23 notes retain unresolved semantic content; none is recorded as fully
formalised. Downloading their pages answers a useful but narrower question
than constructing a complete company model.'''
    new = '''The initial Apple annual/interim preparation inventories 125 quantities,
13 annual notes, 10 interim notes, 70 exhibit references and seven further
package obligations. In that starting assessment, all 23 notes retain
unresolved semantic content; none is recorded as fully formalised. The later
worked readings now trace representative revenue, commitment, asset, tax and
funding consequences, while retaining missing facts and wider package
obligations. Downloading a note, reviewing its material passages and using it
in a complete company model remain different achievements.'''
    assert old in text
    text = text.replace(old, new)
    old_end = '''The investigated real sources have not yet supplied a qualifying unresolved
same-context contradiction. Known revisions, different reporting bases and
synthetic conflicts remain useful cases of their own kinds. A genuine conflict
case must first match entity, perimeter, concept, dimensions, unit, basis,
period, versions and precision, and investigate extraction and supersession.
The absence of a qualifying example in a bounded search is not evidence that
the corpus contains no conflicts.'''
    new_end = '''The financial-amount comparisons investigated so far have not supplied a
qualifying unresolved same-context measurement contradiction. The reference
conflict in Section~\\ref{sec:reference-conflict} establishes the narrower
source-navigation finding. Known revisions, different reporting bases and
synthetic conflicts remain useful cases of their own kinds. A financial
conflict case must first match entity, perimeter, concept, dimensions, unit,
basis, period, versions and precision, and investigate extraction and
supersession. The absence of a qualifying measurement conflict in a bounded
search is not evidence that the corpus contains no conflicts.'''
    assert old_end in text
    return text.replace(old_end, new_end)

def main():
    assert not CAND.exists() and not (UNIT / 'completion.json').exists()
    evidence = json.loads((UNIT / 'source-checks.json').read_text())
    assert not evidence['failed']
    baseline = json.loads((UNIT / 'baseline.json').read_text())
    assert sha(BASE / 'accounting-product-proposal.pdf') == baseline['baseline_pdf_sha256']
    source_hashes = {str(p.relative_to(BASE)): sha(p) for p in sorted(BASE.rglob('*'))
                     if p.is_file() and p.suffix in {'.tex', '.bib', '.lark'}}
    changes = []
    for rel in source_hashes:
        original = (BASE / rel).read_text()
        current = expected_text(rel)
        p = CAND / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(current)
        if current != original:
            changes.append(rel)
            patch = ''.join(difflib.unified_diff(original.splitlines(True), current.splitlines(True), fromfile=str(BASE / rel), tofile=str(p)))
            (UNIT / (Path(rel).stem + '.diff')).write_text(patch)
    save('candidate.json', {'baseline': str(BASE.relative_to(ROOT)), 'candidate': str(CAND.relative_to(ROOT)),
                           'baseline_pdf_sha256': baseline['baseline_pdf_sha256'], 'source_hashes': source_hashes,
                           'changed_files': changes, 'readiness': 'not_ready', 'human_review': 'pending'})
    cmd = ['latexmk', '-g', '-lualatex', '-interaction=nonstopmode', '-halt-on-error', 'accounting-product-proposal.tex']
    overrides = {'TEXMFVAR': '/tmp/accdsl-texmfvar', 'TEXMFCACHE': '/tmp/accdsl-texmfvar', 'CUDA_VISIBLE_DEVICES': '-1'}
    env = os.environ.copy()
    env.update(overrides)
    started = time.monotonic()
    with (UNIT / 'build-stdout.log').open('w') as log:
        result = subprocess.run(cmd, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT)
    record = {'command': cmd, 'cwd': str(CAND.relative_to(ROOT)), 'environment_overrides': overrides,
              'exit_code': result.returncode, 'wall_seconds': time.monotonic() - started,
              'completed_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save('build-run.json', record)
    print(json.dumps(record))
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
