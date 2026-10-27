"""Read-only verification by default; --record seals this new increment once."""
from pathlib import Path
from hashlib import sha256, sha1
from datetime import datetime, timezone
import base64
import importlib.util
import json
import platform
import sys
import time
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
PRIOR = 'data/accounting-master/annual-inventory-persistence-coverage-20261025'
NEXT = 'docs/plans/accounting-company-functions-20261025.md'
PAPER = 'docs/papers/A Simultaneous Equation Approach to Financial Planning Using Cash Flow Components Gentry (1990).pdf'
SYNTHESIS = 'docs/design/research/simulator-equations-and-events-20261025.md'

def sha(path): return sha256(path.read_bytes()).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
def dump(path, value): path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    started = datetime.now(timezone.utc).isoformat()
    clock = time.monotonic()
    record = sys.argv[1:] == ['--record']
    assert sys.argv[1:] in ([], ['--record'])
    if record:
        assert not (HERE/'manifest.json').exists(), 'already recorded'
        assert not (HERE/'source-lock.json').exists(), 'lock already exists'
    checks = []
    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
    previous = json.loads((ROOT/PRIOR/'source-lock.json').read_text())
    previous[str(Path(PRIOR)/'inventory.json')] = sha(ROOT/PRIOR/'inventory.json')
    for name, expected in previous.items():
        check('protected:' + name, sha(ROOT/name) == expected)
    pdf = HERE/'gentry-hoque1990.pdf'
    meta = json.loads((HERE/'gentry-hoque1990-metadata.json').read_text())
    entry = next(x for x in meta['files'] if x['name'] == 'simultaneousequa1694gent.pdf')
    check('paper_sha1_metadata', sha1(pdf.read_bytes()).hexdigest() == entry['sha1'])
    check('paper_size_metadata', pdf.stat().st_size == int(entry['size']))
    check('paper_sha256', sha(pdf) == 'e2d52c3cb4c55dcaccc6648b52654b75f52d2a7b5174f3532b4faa12dbeabe8e')
    with fitz.open(pdf) as doc: check('paper_46_pages', len(doc) == 46)
    if record and not (ROOT/PAPER).exists(): (ROOT/PAPER).write_bytes(pdf.read_bytes())
    check('paper_library_copy', sha(ROOT/PAPER) == sha(pdf))
    pairs = [('actus-installation-blob.json','actus-installation.md'),
             ('actus-core-concepts-blob.json','actus-core-concepts.md'),
             ('service-dockerfile-blob.json','service-dockerfile.txt'),
             ('service-readme-blob.json','service-readme.txt')]
    for blob, decoded in pairs:
        obj = json.loads((HERE/blob).read_text())
        raw = base64.b64decode(obj['content'])
        check('git_blob:' + blob, sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == obj['sha'])
        check('decoded:' + decoded, raw == (HERE/decoded).read_bytes())
    spec = importlib.util.spec_from_file_location('source_arithmetic', HERE/'check_arithmetic.py')
    arithmetic = importlib.util.module_from_spec(spec); spec.loader.exec_module(arithmetic)
    checks.extend(arithmetic.check())
    baseline = json.loads((ROOT/PRIOR/'inventory.json').read_text())
    targeted = {'MC13','MC14','MC17','MC23','MC29','MC30','MC31','MC34','MC35'}
    inventory = {'schema':'accdsl.coverage.references.v1','date':'2026-10-25',
                 'candidate':'3.99','readiness':'not_ready','whole_rows_closed':0,
                 'baseline':{'path':PRIOR+'/inventory.json','sha256':sha(ROOT/PRIOR/'inventory.json')},
                 'next_plan':NEXT,'scope':'Source review only; exact predecessor rows retained by immutable reference.'}
    for group, count in [('obligations',53),('interactions',6),('operations',46)]:
        rows = baseline[group]
        check('coverage_count:' + group, len(rows) == count)
        check('coverage_unique_ids:' + group, len({r['id'] for r in rows}) == count)
        inventory[group] = []
        for row in rows:
            ref = {'path':PRIOR+'/inventory.json','collection':group,'id':row['id'],
                   'sha256':sha256(canonical(row)).hexdigest()}
            updated = group == 'obligations' and row['id'] in targeted
            inventory[group].append({'id':row['id'],'prior_ref':ref,
              'assessment':'source_review_scoped_advance' if updated else 'prior_scope_retained_not_reaudited',
              'evidence':[REL+'/technical-reading.md',REL+'/source-findings.md',SYNTHESIS] if updated else [],
              'full_requirement_closed':False,'acceptance':'not_promoted'})
    if record: dump(HERE/'inventory.json', inventory)
    saved = json.loads((HERE/'inventory.json').read_text())
    check('coverage_exact_reconstruction', saved == inventory)
    for group in ['obligations','interactions','operations']:
        for ref, row in zip(saved[group], baseline[group]):
            check('coverage_row:' + group + ':' + row['id'], ref['prior_ref']['sha256'] == sha256(canonical(row)).hexdigest() and ref['id'] == row['id'])
    check('current_candidate_preserved', sha(ROOT/'docs/design/proposal/manuscript-inventory-persistence-20261025/accounting-product-proposal.pdf') == '6cb611a97dd3d1479c8a010bd65e3de724950a67c9e0284de1ce24ee939f6a06')
    check('next_plan_exists', (ROOT/NEXT).is_file())
    if record:
        lock = dict(previous)
        for p in HERE.iterdir():
            if p.is_file() and p.name not in ['manifest.json','source-lock.json','checks.json','control-refresh.json','finish.py']:
                lock[p.relative_to(ROOT).as_posix()] = sha(p)
        for name in [PAPER,SYNTHESIS,NEXT]: lock[name] = sha(ROOT/name)
        dump(HERE/'source-lock.json', lock)
    lock = json.loads((HERE/'source-lock.json').read_text())
    for name, expected in lock.items(): check('sealed:' + name, sha(ROOT/name) == expected)
    result = {'passed':all(c['passed'] for c in checks),'checks':checks,'protected_files':len(lock),
              'coverage_counts':[53,6,46],'whole_rows_closed':0,'updated_obligations':len(targeted)}
    assert result['passed'], [c['name'] for c in checks if not c['passed']]
    if record:
        dump(HERE/'checks.json',result)
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':time.monotonic()-clock,
             'git_commit_recorded':'03fea070f089821f4759e49a4466a3399b7fc078',
             'command':'python3 -B '+REL+'/verify.py --record','environment':platform.python_version(),
             'cpu_gpu':'CPU-only deterministic file and rational checks; no GPU framework imported',
             'random_seeds':'N/A: deterministic','data_version':'retained source bytes bound in source-lock.json',
             'plan':'docs/plans/accounting-simulator-survey-source-recovery-20261025.md',
             'result':REL+'/result.md','source_lock_sha256':sha(HERE/'source-lock.json'),
             'retrieval_log_limit':'Earlier exact command flags and durations not all retained; no invented provenance',
             'scope':'Narrow source/transcription and preservation checks, not scientific-model replication'})
    else: check('recorded_checks_match', result == json.loads((HERE/'checks.json').read_text()))
    assert all(c['passed'] for c in checks)
    print(json.dumps({'passed':True,'checks':len(result['checks']),'protected_files':len(lock),'coverage':[53,6,46],'whole_rows_closed':0}))

if __name__ == '__main__': main()
