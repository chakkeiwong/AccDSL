"""Record Version 3.48 once; default invocation is read-only replay."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from check_candidate import check

U = Path(__file__).resolve().parent
R = U.parents[2]
P = R / 'data/accounting-master/readability-repair-20261022'
C = R / 'docs/design/proposal/manuscript-readability-20261022-theta'
PDF = C / 'accounting-product-proposal.pdf'
PLAN = R / 'docs/plans/accounting-readability-repair-20261022-theta.md'
EXPECTED = '6a2acd8e3e01e6127eb89112a168216ee12b3244b3e56c814f1d2d1c56b90f0e'
DELTA = ('Version 3.48 defines theta before its first policy/event display. Exact mathematics, '
         'citations and qualifications remain; six local rendered pages were inspected. '
         'Full 3.48 regression and independent/domain/human acceptance remain pending. Zero whole-row closures.')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(R))
bind = lambda p: dict(path=rel(p), sha256=sha(p))

def write(name, value):
    with (U / name).open('x') as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write('\n')

def preservation():
    old, new = load(P / 'assessment-successor.json'), load(U / 'assessment-successor.json')
    allowed = {'previous_candidate_version', 'candidate_version', 'candidate_pdf', 'candidate_pdf_sha256', 'delta_assessment', 'evidence_updates'}
    checks = []
    for a, b in zip(old['rows'], new['rows']):
        unchanged = {k: v for k, v in a.items() if k not in allowed} == {k: v for k, v in b.items() if k not in allowed}
        evidence = b.get('evidence_updates', [])[:len(a.get('evidence_updates', []))] == a.get('evidence_updates', [])
        checks.append(dict(name=a['id'], passed=unchanged and evidence and b['candidate_pdf_sha256'] == EXPECTED))
    checks += [dict(name='all53', passed=len(old['rows']) == len(new['rows']) == 53),
               dict(name='six-interactions', passed=old['interactions'] == new['interactions'] and len(new['interactions']) == 6)]
    a, b = load(P / 'operation-successor.json'), load(U / 'operation-successor.json')
    ops = [dict(name=x['id'], passed=x == y and y['full_requirement_closed'] is False) for x, y in zip(a['rows'], b['rows'])]
    assert len(ops) == len(b['rows']) == 46 and all(x['passed'] for x in checks + ops)
    assert new['readiness'] == 'not_ready' and new['candidate_pdf_sha256'] == EXPECTED
    return checks, ops

def record():
    outputs = ('completion.json', 'assessment-successor.json', 'operation-successor.json', 'rendered-review.json',
               'assessment-checks.json', 'operation-checks.json', 'run-manifest.json', 'integration-bindings.json')
    assert not any((U / n).exists() for n in outputs)
    for name in ('review.md', 'result.md', 'execution-audit.md'):
        assert (U / name).stat().st_size > 100
    rendered = load(U / 'render-manifest.json')
    assert rendered['pdf_sha256'] == EXPECTED
    assert [r['page'] for r in rendered['renders']] == [1, 2, 87, 88, 89, 90]
    for row in rendered['renders']:
        assert sha(R / row['path']) == row['sha256']
    write('rendered-review.json', dict(candidate_version='3.48', pdf=bind(PDF),
        inspected_pages=[1, 2, 87, 88, 89, 90], visitation_order=[88, 89, 1, 87, 90, 2],
        provenance='Actual 110 dpi image inspections in this continuation; local review only',
        renders=rendered['renders'], review=bind(U / 'review.md'), full_regression='pending',
        independent_reader='pending', human_acceptance='pending'))
    evidence = [bind(U / n) for n in ('result.md', 'review.md', 'execution-audit.md', 'candidate-checks.json',
                                     'build-manifest.json', 'rendered-review.json', 'page-delta.json')]
    evidence += [bind(P / 'regression/completion.json'), bind(P / 'regression/document-synthesis.md')]
    new = deepcopy(load(P / 'assessment-successor.json'))
    new.update(date='2026-10-22', candidate_version='3.48', candidate_pdf=rel(PDF), candidate_pdf_sha256=EXPECTED,
        predecessor=rel(P / 'assessment-successor.json'), predecessor_sha256=sha(P / 'assessment-successor.json'),
        assessment_scope=DELTA, author_review_status='local_repair_complete_full_3.48_regression_pending')
    new['historical_3.47_author_diagnosis'] = bind(P / 'regression/completion.json')
    new['prior_additive_supplements'] = [*new.get('prior_additive_supplements', []),
                                       *[bind(p) for p in sorted(P.glob('*-supplement.json'))]]
    affected = {'MC11', 'MC12', 'MC18', 'MC32', 'MC33', 'MC34', 'MC35', 'G2', 'G6', 'G10', 'G15', 'G16'}
    for row in new['rows']:
        row.update(previous_candidate_version='3.47', candidate_version='3.48', candidate_pdf=rel(PDF), candidate_pdf_sha256=EXPECTED,
            delta_assessment=DELTA if row['id'] in affected else 'Inherited substantive assessment; local notation repair supplies no new method acceptance.')
        if row['id'] in affected:
            row.setdefault('evidence_updates', []).extend(deepcopy(evidence))
    write('assessment-successor.json', new)
    ops = deepcopy(load(P / 'operation-successor.json'))
    ops.update(candidate_version='3.48', candidate_pdf=rel(PDF), candidate_pdf_sha256=EXPECTED,
        recorded_utc=datetime.now(timezone.utc).isoformat(), current_increment=DELTA,
        predecessor=rel(P / 'operation-successor.json'), predecessor_sha256=sha(P / 'operation-successor.json'))
    write('operation-successor.json', ops)
    checks, opchecks = preservation()
    write('assessment-checks.json', dict(checks=len(checks), failures=0, detail=checks))
    write('operation-checks.json', dict(checks=len(opchecks), failures=0, detail=opchecks))
    protection, build = load(U / 'protection.json'), load(U / 'build-manifest.json')
    write('run-manifest.json', dict(git_commit=protection['head'], branch=protection['branch'],
        environment=sys.executable, python=platform.python_version(), cpu_gpu='CPU only; GPU devices intentionally hidden',
        data_version='Protected 3.47 and bounded prose-only 3.48; no financial data changed',
        seeds='N/A deterministic document repair', wall_seconds_build=build['wall_seconds'],
        started_utc=protection['started_utc'], recorded_utc=datetime.now(timezone.utc).isoformat(),
        commands=['prepare.py', 'build_candidate.py', 'check_candidate.py', 'render_local.py', 'verify.py --record', 'verify.py'],
        command_scope='Python: env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B; exact build command bound below',
        build=bind(U / 'build-manifest.json'), plan=bind(PLAN), result=bind(U / 'result.md'), output=rel(U)))
    write('integration-bindings.json', dict(pdf=bind(PDF), assessment=bind(U / 'assessment-successor.json'),
        operations=bind(U / 'operation-successor.json'), evidence=evidence, status='not_ready', whole_rows_closed=0,
        scope='Frozen local repair; subsequent regression and live controls remain separate'))
    files = [p for p in U.rglob('*') if p.is_file() and not any(x in p.relative_to(U).parts for x in ('__pycache__', 'regression', 'controls-after'))]
    files += [p for p in C.rglob('*') if p.is_file()] + [PLAN]
    write('completion.json', dict(bindings={rel(p): sha(p) for p in sorted(set(files))},
        policy='Local repair evidence immutable; future regression and control refreshes are additive.'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    assert check() == load(U / 'candidate-checks.json') and sha(PDF) == EXPECTED
    if args.record:
        record()
    checks, ops = preservation()
    for name, digest in load(U / 'completion.json')['bindings'].items():
        assert sha(R / name) == digest, name
    assert load(U / 'assessment-checks.json')['detail'] == checks
    assert load(U / 'operation-checks.json')['detail'] == ops
    print(json.dumps(dict(status='recorded and verified' if args.record else 'read-only replay passed',
        version='3.48', pages=401, assessment_checks=len(checks), operations=len(ops),
        protected_files=len(load(U / 'protection.json')['protected']),
        completion_bindings=len(load(U / 'completion.json')['bindings']), whole_rows_closed=0, readiness='not_ready')))

if __name__ == '__main__':
    main()
