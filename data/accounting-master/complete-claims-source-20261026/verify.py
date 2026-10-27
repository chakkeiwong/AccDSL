"""Deterministic full-result checks against the frozen typed successor."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, subprocess, sys, time
import complete_text as text
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TYPED = HERE.parent / 'complete-claims-opening-20261026'
PRIOR = HERE.parent / 'admitted-program-binding-20261026'
opening = text.opening
core = text.core
def read(p): return json.loads(p.read_text())
def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(n, value): (HERE / n).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
def equal(a, b): return core.canonical(a) == core.canonical(b)


def main():
    start = time.monotonic()
    assertions, comparisons, controls = [], [], []
    def ensure(ok, label):
        assertions.append(dict(check=label, passed=bool(ok)))
        assert ok, label
    for folder in ('examples', 'results', 'adverse'):
        (HERE / folder).mkdir(exist_ok=True)
    lockpath = HERE / 'source-lock.json'
    if not lockpath.exists():
        lock = {}
        for directory in (TYPED, HERE.parent / 'selected-company-source-20261026'):
            for name, digest in read(directory / 'source-lock.json').items():
                assert name not in lock or lock[name] == digest, name
                lock[name] = digest
            for p in directory.rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:
                    name = str(p.relative_to(ROOT))
                    assert name not in lock or lock[name] == sha(p), name
                    lock[name] = sha(p)
        dump('source-lock.json', lock)
    lock = read(lockpath)
    for name, digest in lock.items():
        assert sha(ROOT / name) == digest, name
    cases = read(TYPED / 'cases.json')
    empty_results = {r['case']: r['result'] for r in read(TYPED / 'controls.json')}
    for row in read(PRIOR / 'cases.json')[:4]:
        selection = read(PRIOR / f'selections/{row["company"]}.json')
        template = read(HERE.parent / f'declared-opening-admission-20261026/templates/{row["company"]}.json')
        contract = opening.make_contract(template, row['program']['state_invariant'])
        population = opening.population(row['input']['opening'], 'Retained empty synthetic complete population')
        cases.append(dict(row, case=row['case'] + ':empty', selection=selection, contract=contract,
                          completeness=population, result=empty_results[row['case'] + ':empty_baseline']))
    originals = {n: getattr(native, n) for n in ('validate', 'control', 'claim_type', 'event_types', 'make_request', 'run', 'protected')}
    builder = operating.build
    def disabled(*args, **kwargs):
        raise AssertionError('native callback on complete claims source path')
    try:
        for name in originals:
            setattr(native, name, disabled)
        operating.build = disabled
        for index, row in enumerate(cases):
            before = opening.a.order_digest(row)
            source, resources = text.render(row['selection'], row['contract'], row['completeness'], row['program'])
            lowered = text.lower(source, resources, row['selection'])
            label = row['case']
            for key in ('selection', 'contract', 'input', 'completeness', 'program'):
                ensure(equal(lowered[key], row[key]), label + ':complete_' + key)
            ensure(opening.a.order_digest(lowered['input']) == opening.a.order_digest(row['input']), label + ':input_order')
            ensure(not lowered['executed'] and not lowered['opening_admitted'] and not lowered['source_admission'], label + ':lower_only')
            actual = text.execute_source(source, resources, row['selection'])
            expected = row['result']
            original_order = opening.a.order_digest(row['program'])
            lowered_order = opening.a.order_digest(lowered['program'])
            for result, order, kind in ((actual, lowered_order, 'lowered'), (expected, original_order, 'original')):
                ensure(result['program_order_sha256'] == order, label + ':' + kind + '_outer_order')
                ensure(result['delegated']['program_order_sha256'] == order, label + ':' + kind + '_delegated_order')
            compared = deepcopy(actual)
            compared['program_order_sha256'] = expected['program_order_sha256']
            compared['delegated']['program_order_sha256'] = expected['delegated']['program_order_sha256']
            ensure(equal(compared, expected), label + ':full_result_except_two_declared_order_paths')
            ensure(equal(actual['delegated']['execution'], expected['delegated']['execution']), label + ':exact_execution')
            ensure(opening.a.order_digest(row) == before, label + ':inputs_unchanged')
            filename = f'{index:02d}'
            (HERE / f'examples/{filename}.acc').write_text(source)
            dump(f'examples/{filename}.resources.json', resources)
            dump(f'examples/{filename}.selection.json', row['selection'])
            dump(f'results/{filename}.json', dict(case=label, actual=actual, expected=expected,
                 original_program_order=original_order, lowered_program_order=lowered_order,
                 exception_paths=['program_order_sha256', 'delegated.program_order_sha256'], full_remaining_result_equal=True))
            comparisons.append(dict(case=label, status=actual['status'], source=f'examples/{filename}.acc',
                source_sha256=sha(HERE / f'examples/{filename}.acc'), result=f'results/{filename}.json',
                result_sha256=sha(HERE / f'results/{filename}.json'),
                successful_commands=actual['delegated']['execution']['successful_commands'], full_remaining_result_equal=True))
        from source_controls import run_controls
        run_controls(cases[0], ensure, controls)
    finally:
        for name, value in originals.items():
            setattr(native, name, value)
        operating.build = builder
    dump('comparisons.json', comparisons)
    dump('controls.json', controls)
    for name, digest in lock.items():
        ensure(sha(ROOT / name) == digest, 'protected:' + name)
    summary = dict(passed=True, carried_programs=4, empty_programs=4,
                   carried_commands=sum(r['successful_commands'] for r in comparisons[:4]),
                   empty_commands=sum(r['successful_commands'] for r in comparisons[4:]),
                   controls=len(controls), assertions=len(assertions), protected_files=len(lock),
                   native_lifecycle_and_builder_disabled=True, actual_source_completeness=False,
                   accounting_admission=False, production_ready=False)
    dump('checks.json', summary)
    dump('assertions.json', assertions)
    git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
    dump('run-manifest.json', dict(git_commit=git.stdout.strip() if git.returncode == 0 else 'unavailable',
         command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/complete-claims-source-20261026/verify.py',
         environment=sys.version, cpu_gpu='CPU; GPU intentionally hidden', random_seeds='N/A deterministic',
         wall_seconds=time.monotonic()-start, data_version=sha(lockpath),
         plan_file='docs/plans/accounting-complete-claims-source-20261026.md',
         result_file='data/accounting-master/complete-claims-source-20261026/result.md',
         artifacts=['examples', 'results', 'adverse', 'comparisons.json', 'controls.json', 'checks.json', 'assertions.json'],
         implementation_sha256={n:sha(HERE/n) for n in ('complete_text.py', 'verify.py', 'source_controls.py', 'design.md')},
         timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__ == '__main__':
    main()
