"""P12 finite conformance benchmark; preparation never imports evaluated engines."""
from __future__ import annotations
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = 'docs/design/fixtures/p12-benchmark-inputs-v1.json'
PLAN = 'docs/plans/accounting-p12-benchmark-plan.md'
OUTPUT = ROOT / 'data/accounting-master/deliverables/P12'
CHANGED = [PLAN, FIXTURE, 'scripts/accounting_benchmark_v1.py',
           'scripts/check_accounting_p12.py', 'tests/test_accounting_p12.py',
           'data/accounting-master/deliverables/P12/benchmark.json',
           'data/accounting-master/deliverables/P12/result.md',
           'data/accounting-master/deliverables/P12/progress.md']


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def utc():
    return datetime.now(timezone.utc).isoformat()


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def independent_enumeration(cell):
    """No Z3 or evaluated solver; one exact result per Cartesian assignment."""
    rows = []
    for values in product(*cell['domains']):
        amount = sum((Fraction(w) * v for w, v in zip(cell['weights'], values)), Fraction())
        rows.append({'assignments': dict(zip(cell['variables'], values)),
                     'feasible': amount <= Fraction(cell['threshold']), 'output': str(amount)})
    return rows


def validate_fixture(fixture, root=ROOT):
    import jsonschema
    schema = read(root / 'data/financial-report-benchmark/annotation-record.schema.json')
    cases, cells, refs = (fixture[k] for k in ('chronology', 'workloads', 'source_references'))
    p = fixture['protocol']
    require((len(cases), len(cells), len(refs)) == (12, 5, 4), 'fixed inventory changed')
    require((p['chronology_denominator'], p['valid_denominator'], p['invalid_denominator'],
             p['workload_denominator'], p['repetitions'], p['scheduled_workload_runs'],
             p['source_reference_count'], p['source_evaluation_denominator']) ==
            (12, 3, 9, 5, 3, 15, 4, 0), 'fixed denominators changed')
    for rows in (cases, cells, refs):
        require(len({r['id'] for r in rows}) == len(rows), 'duplicate reference ID')
    require(Counter(c['kind'] for c in cases) == {'valid': 3, 'invalid': 9}, 'case classes')
    for c in cases:
        if c['kind'] == 'valid':
            expected = c['expected']
            require(Fraction(expected['amount']) == Fraction(c['total']['amount']) -
                    Fraction(c['earlier']['amount']), 'independent subtraction mismatch')
            require(expected['period'] == {'start': c['earlier']['period']['end'],
                                          'end': c['total']['period']['end']}, 'half-open period mismatch')
            require(expected['status'] == 'ok', 'valid answer missing')
        else:
            require(c['expected']['status'] == 'rejected' and c['expected']['code'], 'rejection missing')
    for c in cells:
        require(len(c['variables']) == len(c['domains']) == len(c['weights']), 'workload arity')
        require(len(set(c['variables'])) == len(c['variables']), 'duplicate variable')
        require(all(d == [0, 1] for d in c['domains']), 'binary domains required')
        require(set(c['budget']) == {'max_slots', 'max_formula_nodes', 'max_integer_assignments',
                                    'max_cells', 'elapsed_ms', 'solver_timeout_ms', 'solver_rlimit'}, 'incomplete budget')
        require(all(type(v) is int and v >= 0 for v in c['budget'].values()), 'invalid budget')
        independent_enumeration(c)
    for ref in refs:
        jsonschema.validate(ref['annotation'], schema)
        require(ref['ambiguity_preserved'] and ref['admissibility']['forbidden'], 'ambiguity rule missing')
        require(not ref['evaluation_ready'], 'source extraction has no evaluated system')
        require(file_hash(root / ref['original_path']) == ref['annotation']['original_sha256'], 'original source changed')
        require(bool(ref['supports']), 'missing source support')
        for support in ref['supports']:
            path = root / support['path']
            require(file_hash(path) == support['sha256'], 'source/extraction hash changed')
            text = path.read_text()
            require(support['end'] > support['start'] and text[support['start']:support['end']] == support['quote'], 'source locator/quote mismatch')
            if support['pdf_physical_page'] is not None:
                require(text[:support['start']].count('\f') + 1 == support['pdf_physical_page'], 'PDF physical page mismatch')
    unresolved = next(r for r in refs if r['id'] == 'S4-debt-swap-allocation')
    require(all(r['value_exact'] is None for r in unresolved['annotation']['readings']), 'invented unresolved allocation')


def exposure_register(root=ROOT):
    base = root / 'data/financial-report-benchmark'
    panel = read(base / 'target-panel-v2.json')
    protocol = read(base / 'benchmark-protocol-v1.json')
    integrity = read(base / 'integrity-manifest.json')
    groups = defaultdict(list)
    for path, entry in integrity['files'].items():
        if 'original' in entry['roles']:
            groups[entry['sha256']].append(path)
    families = []
    for issuer in panel['issuers']:
        name = issuer['issuer_id']; role = protocol['provisional_issuer_family_roles'][name]
        families.append({'issuer': name, 'industry': issuer['industry'], 'proposed_role': role,
                         'substantive_development_exposure': role == 'development',
                         'source_acquisition_qa_exposure': True,
                         'current_p12_annotation_exposure': name == 'apple',
                         'evaluated_model_training_exposure': 'unknown; no LLM evaluated',
                         'clean_heldout': False,
                         'grouping': 'all years, languages, mirrors, amendments and revisions stay in issuer family'})
    return {'families': families, 'window': panel['coverage_window'], 'issuer_count': 9,
            'verified_report_slots': integrity['verified_slots'],
            'retained_original_paths': sum(len(g) for g in groups.values()),
            'unique_original_hashes': len(groups),
            'exact_duplicate_groups': [{'sha256': h, 'paths': p} for h, p in sorted(groups.items()) if len(p) > 1],
            'duplicate_audit_scope': 'all original-path hashes in frozen integrity manifest; only task-used original bytes reverified here',
            'semantic_duplicate_coverage': 'incomplete',
            'known_relationships': ['Annual and interim balance sheets repeat comparative dates and tables.',
                                    'Current and prior-year columns are dependent, not new issuer observations.',
                                    'Language versions, mirrors and retained revisions belong to the same family.'],
            'dependence': 'nine purposive issuer families, eight years each; issuer/time and cross-report table dependence',
            'test_concentration': 'JPMorgan, Ping An and Munich Re: all three proposed test families are banking/insurance',
            'split_status': 'candidate roles only, exposed through acquisition/QA; no clean unseen-model claim'}


def preparation(root=ROOT, revision=1):
    fixture = read(root / FIXTURE)
    validate_fixture(fixture, root)
    references = {'chronology': fixture['chronology'], 'source_records': fixture['source_references'],
                  'workloads': [{**c, 'independent_oracle': independent_enumeration(c)} for c in fixture['workloads']]}
    paths = {FIXTURE, PLAN, 'scripts/accounting_benchmark_v1.py', 'scripts/check_accounting_p12.py',
             'tests/test_accounting_p12.py', 'scripts/context_chronology_v1.py', 'scripts/rational_solver_v1.py',
             'data/financial-report-benchmark/annotation-record.schema.json',
             'data/financial-report-benchmark/target-panel-v2.json',
             'data/financial-report-benchmark/benchmark-protocol-v1.json',
             'data/financial-report-benchmark/integrity-manifest.json',
             'data/financial-report-benchmark/release-manifest.json'}
    for r in fixture['source_references']:
        paths.add(r['original_path'])
        paths.update(s['path'] for s in r['supports'])
    prepared = {'created_at': utc(), 'gate': 'passed', 'protocol': fixture['protocol'],
                'revision': revision, 'harness_version': 'p12.harness.v2',
                'references': references, 'reference_sha256': digest(references),
                'exposure': exposure_register(root),
                'input_hashes': {p: file_hash(root / p) for p in sorted(paths)},
                'difficult_cases': ['instant versus cumulative', 'negative exact rational flow',
                                   'calendar boundaries', 'context/concept mismatch', 'revision identity and exception scope',
                                   'derivative notional versus debt allocation', 'incomplete finite search',
                                   'unsupported nonlinear product', 'cross-report and longitudinal dependence'],
                'source_readiness': {'provisional_records': 4, 'evaluated_source_tasks': 0,
                                     'debt_allocation': 'unresolved', 'professional_adjudication': 'not performed'}}
    return {'schema_version': 'accdsl.p12.benchmark.v1', 'status': 'prepared_not_evaluated',
            'preparation': prepared, 'preparation_sha256': digest(prepared), 'runs': []}


def repair_preparation(previous, archive, root=ROOT):
    """Retain the exact reviewed evidence before freezing repaired harness hashes."""
    p = previous['preparation']
    require(previous['preparation_sha256'] == digest(p), 'previous preparation hash mismatch')
    require(p['reference_sha256'] == digest(p['references']), 'previous reference hash mismatch')
    require(read_archive_document(archive) == previous, 'archive does not match previous benchmark')
    for name, source in archive['source_snapshots'].items():
        require(hashlib.sha256(source.encode()).hexdigest() == p['input_hashes'][name],
                'previous source snapshot mismatch: ' + name)
    document = preparation(root, revision=p.get('revision', 1) + 1)
    require(document['preparation']['reference_sha256'] == p['reference_sha256'],
            'repair must not change reference answers')
    document['prior_evidence'] = {'disposition': 'superseded: harness defects identified by result review',
                                'archive': deepcopy(archive), 'archive_sha256': digest(archive)}
    document['repair'] = {'findings': ['malformed responses escaped scheduled failure recording',
                                      'unsupported coverage allowed false zero unresolved branches'],
                          'reference_answers_changed': False,
                          'previous_preparation_sha256': previous['preparation_sha256']}
    return document


def read_archive_document(archive):
    for field in ('benchmark', 'result'):
        require(hashlib.sha256(archive[field + '_text'].encode()).hexdigest() == archive[field + '_sha256'],
                'archive text hash mismatch: ' + field)
    return json.loads(archive['benchmark_text'])


def verify_preparation(document, root=ROOT):
    p = document['preparation']
    require(document['preparation_sha256'] == digest(p), 'preparation hash mismatch')
    require(p['reference_sha256'] == digest(p['references']), 'reference hash mismatch')
    if 'prior_evidence' in document:
        saved = document['prior_evidence']
        require(saved['archive_sha256'] == digest(saved['archive']), 'prior evidence hash mismatch')
        read_archive_document(saved['archive'])
    for path, expected in p['input_hashes'].items():
        require(file_hash(root / path) == expected, 'frozen input changed: ' + path)
    validate_fixture(read(root / FIXTURE), root)


def evaluate_chronology(cases):
    from context_chronology_v1 import subtract_cumulative, P06Error
    answers = []
    for c in cases:
        try:
            answer = subtract_cumulative(c['total'], c['earlier'], revision_compatibility=c.get('revision_compatibility'))
            answer['amount'] = str(answer['amount'])
            answer['status'] = 'ok'
        except P06Error as exc:
            answer = {'status': 'rejected', 'code': exc.code}
        except Exception as exc:
            answer = {'status': 'crash', 'error': type(exc).__name__, 'detail': str(exc)}
        answers.append({'id': c['id'], 'answer': answer})
    return answers


def score_chronology(cases, answers):
    buckets = defaultdict(list); errors = []
    known = {c['id'] for c in cases}
    if not isinstance(answers, list):
        answers = []; errors.append('malformed answer batch')
    for answer in answers:
        if not isinstance(answer, dict) or not isinstance(answer.get('id'), str):
            errors.append('malformed answer envelope'); continue
        if answer['id'] not in known:
            errors.append('extra answer: ' + answer['id'])
        buckets[answer['id']].append(answer.get('answer'))
    outcomes = []
    for case in cases:
        found = buckets[case['id']]
        equal = len(found) == 1 and found[0] == case['expected']
        fields = [] if equal else (['missing' if not found else 'duplicate'] if len(found) != 1 else ['whole answer differs'])
        outcomes.append({'id': case['id'], 'kind': case['kind'], 'passed': equal, 'diagnostics': fields})
    return {'denominator': len(cases), 'passed': sum(c['passed'] for c in outcomes),
            'by_kind': {k: {'denominator': sum(c['kind'] == k for c in cases),
                            'passed': sum(c['passed'] and c['kind'] == k for c in outcomes)} for k in ('valid', 'invalid')},
            'protocol_errors': errors, 'all_passed': all(c['passed'] for c in outcomes) and not errors,
            'cases': outcomes}


def admit_source_answer(reference, answer):
    """Admissibility helper only; no source-system scores are produced."""
    return isinstance(answer, str) and answer in reference['admissibility']['allowed']


def execute_workload(cell):
    """Runs only in the synchronous child. Memory includes imports and solver."""
    import resource
    import tracemalloc
    tracemalloc.start(); started = time.perf_counter(); cpu = time.process_time()
    import z3
    from rational_solver_v1 import Problem, Budget, q, nodes, solve
    variables = {name: z3.Int(name) for name in cell['variables']}
    expression = sum((q(w) * variables[n] for n, w in zip(cell['variables'], cell['weights'])), q(0))
    p = Problem(scope=cell['id'], evidence_view='synthetic fixture v1', variables=variables,
                finite=dict(zip(cell['variables'], cell['domains'])), outputs={'weighted_sum': expression},
                slots=len(variables), provenance={'fixture': FIXTURE})
    p.add('synthetic:weighted-upper', expression <= q(cell['threshold']))
    if cell['fragment'] == 'nonlinear_product':
        p.add('synthetic:nonlinear', variables[cell['variables'][0]] * variables[cell['variables'][1]] <= 1)
    formula_nodes = sum(nodes(e) for _, e in p.constraints) + sum(nodes(e) for e in p.outputs.values())
    kernel_start = time.perf_counter()
    result = solve(p, Budget(**cell['budget']))
    kernel_seconds = time.perf_counter() - kernel_start
    allocation_peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    units = 'bytes' if sys.platform == 'darwin' else 'KiB'
    cov = result['coverage']; actual = result['cells']
    metrics = {'wall_seconds': time.perf_counter() - started, 'cpu_seconds': time.process_time() - cpu,
               'kernel_wall_seconds': kernel_seconds, 'peak_rss_native': rss, 'peak_rss_units': units,
               'peak_rss_bytes': rss if units == 'bytes' else rss * 1024,
               'python_allocation_peak_bytes': allocation_peak,
               'memory_scope': 'RSS is process lifetime high-water; tracemalloc is Python allocations, not total memory',
               'input_bytes': len(canonical(cell)), 'output_bytes': len(canonical(result)),
               'input_facts': sum(len(d) for d in cell['domains']) + len(cell['weights']) + 1,
               'fact_definition': 'domain entries plus rational weights plus upper threshold',
               'variables': len(variables), 'labelled_constraints': len(p.constraints),
               'generated_constraints': len(result['generated_constraints']),
               'assignment_constraints_materialized': sum(len(c['assignments']) for c in actual),
               'formula_nodes': formula_nodes, 'potential_branches': math.prod(map(len, cell['domains'])),
               'explored_branches': len(actual), 'retained_feasible_branches': cov['feasible'],
               'completed_branches': cov['completed'], 'infeasible_branches': cov['infeasible'],
               'unresolved_branches': cov['unresolved'], 'solver_total_branches': cov['total'],
               'z3_version': z3.get_version_string()}
    return {'result': result, 'metrics': metrics}


MEASUREMENTS = ('wall_seconds', 'cpu_seconds', 'kernel_wall_seconds', 'peak_rss_native',
                'peak_rss_bytes', 'python_allocation_peak_bytes', 'input_bytes', 'output_bytes',
                'input_facts', 'variables', 'labelled_constraints', 'generated_constraints',
                'assignment_constraints_materialized', 'formula_nodes', 'potential_branches',
                'explored_branches', 'retained_feasible_branches', 'completed_branches', 'infeasible_branches')


def validate_workload_response(observed):
    """Check JSON containers before any scorer or report dereferences them."""
    require(isinstance(observed, dict), 'response must be an object')
    require('failure' not in observed, 'child failure: ' + str(observed.get('failure')))
    for field in ('result', 'metrics'):
        require(isinstance(observed.get(field), dict), field + ' must be an object')
    result = observed['result']
    require(isinstance(result.get('status'), str), 'status must be a string')
    cov = result.get('coverage')
    require(isinstance(cov, dict), 'coverage must be an object')
    for key in ('total', 'completed', 'feasible', 'infeasible', 'unresolved'):
        require(key in cov, 'missing coverage: ' + key)
        value = cov[key]
        require((key in ('total', 'unresolved') and value is None) or
                (type(value) is int and value >= 0), 'invalid coverage: ' + key)
    if 'complete' in cov:
        require(type(cov['complete']) is bool, 'complete must be a Boolean')
    if 'unvisited' in cov:
        require(isinstance(cov['unvisited'], dict), 'unvisited must be an object')
    require(isinstance(result.get('cells'), list), 'cells must be a list')
    for row in result['cells']:
        require(isinstance(row, dict), 'cell must be an object')
        require(type(row.get('ordinal')) is int, 'cell ordinal must be an integer')
        require(isinstance(row.get('assignments'), dict), 'assignments must be an object')
        for field in ('witness', 'outputs', 'conflict'):
            if field in row:
                require(isinstance(row[field], dict), field + ' must be an object')


def score_workload(cell, observed):
    errors = []
    try:
        validate_workload_response(observed)
        result, metrics = observed['result'], observed['metrics']
        for key in MEASUREMENTS:
            value = metrics.get(key)
            if type(value) not in (int, float) or (type(value) is float and not math.isfinite(value)) or value < 0:
                errors.append('missing/invalid measurement: ' + key)
        if metrics.get('peak_rss_units') not in ('KiB', 'bytes'):
            errors.append('RSS units missing')
        if result['status'] != cell['expected_status']:
            errors.append('unexpected status')
        cov = result['coverage']; actual = result['cells']; oracle = cell['independent_oracle']
        if metrics.get('input_bytes') != len(canonical({k: v for k, v in cell.items() if k != 'independent_oracle'})):
            errors.append('input bytes mismatch')
        if metrics.get('output_bytes') != len(canonical(result)):
            errors.append('output bytes mismatch')
        for m, value in [('explored_branches', len(actual)), ('retained_feasible_branches', cov['feasible']),
                         ('completed_branches', cov['completed']), ('infeasible_branches', cov['infeasible']),
                         ('unresolved_branches', cov['unresolved']), ('solver_total_branches', cov['total'])]:
            if m not in metrics or metrics[m] != value:
                errors.append('coverage measurement mismatch: ' + m)
        if cell['expected_status'] == 'UnsupportedFragment':
            wanted_cov = {'total': None, 'unresolved': None, 'completed': 0,
                          'feasible': 0, 'infeasible': 0}
            if (actual or any(cov[k] != v for k, v in wanted_cov.items()) or
                    cov.get('complete', False) is not False or
                    not isinstance(result.get('reason'), str) or not result['reason'].strip()):
                errors.append('unsupported response fabricated coverage')
        else:
            count = len(oracle) if cell['expected_status'] == 'ExactWithinScope' else cell['budget']['max_integer_assignments']
            expected = oracle[:count]
            if len(actual) != count:
                errors.append('lost/extra branch')
            for j, (got, wanted) in enumerate(zip(actual, expected)):
                if got['ordinal'] != j or got['assignments'] != wanted['assignments']:
                    errors.append('assignment/ordinal mismatch')
                if got['feasibility'] != ('sat' if wanted['feasible'] else 'unsat'):
                    errors.append('feasibility mismatch')
                if wanted['feasible']:
                    if got.get('outputs') != {'weighted_sum': wanted['output']}:
                        errors.append('weighted output mismatch')
                    if any(Fraction(got['witness'][n]) != v for n, v in wanted['assignments'].items()):
                        errors.append('witness mismatch')
                elif got.get('conflict', {}).get('rechecked') != 'unsat':
                    errors.append('infeasibility not rechecked')
            feasible = sum(r['feasible'] for r in expected)
            wanted_cov = {'total': len(oracle), 'completed': count, 'feasible': feasible,
                          'infeasible': count - feasible, 'unresolved': len(oracle) - count,
                          'complete': count == len(oracle)}
            if any(cov.get(k) != v for k, v in wanted_cov.items()):
                errors.append('coverage reconciliation or completeness failed')
            if cov.get('unvisited', {}).get('start_ordinal') != count or cov.get('unvisited', {}).get('stop_ordinal') != len(oracle):
                errors.append('unvisited coverage mismatch')
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        errors.append('malformed/missing workload reply: ' + str(exc))
    return {'passed': not errors, 'errors': errors}


def run_child(cell, timeout, runner=subprocess.run):
    command = [sys.executable, '-B', str(ROOT / 'scripts/check_accounting_p12.py'), '--child']
    start = time.perf_counter()
    try:
        reply = runner(command, input=json.dumps(cell), text=True, capture_output=True,
                       timeout=timeout, cwd=ROOT, env={**os.environ, 'CUDA_VISIBLE_DEVICES': '-1'})
        if reply.returncode:
            return {'failure': 'child_exit', 'exit_code': reply.returncode, 'stderr': reply.stderr[-2000:]}
        out = json.loads(reply.stdout)
        try:
            validate_workload_response(out)
        except ValueError as exc:
            return {'failure': 'malformed_response', 'error': str(exc), 'response': out,
                    'process_wall_seconds': time.perf_counter() - start}
        out['process_wall_seconds'] = time.perf_counter() - start
        return out
    except subprocess.TimeoutExpired:
        return {'failure': 'timeout', 'timeout_seconds': timeout}
    except (OSError, ValueError) as exc:
        return {'failure': 'process_or_json_error', 'error': str(exc)}


def run_checks():
    results = []
    for suite in ('p12', 'p04', 'p06'):
        command = [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-p', f'test_accounting_{suite}.py']
        start = time.perf_counter()
        try:
            r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60,
                               env={**os.environ, 'CUDA_VISIBLE_DEVICES': '-1'})
            results.append({'command': ['CUDA_VISIBLE_DEVICES=-1'] + command, 'exit_code': r.returncode,
                            'wall_seconds': time.perf_counter() - start, 'stdout': r.stdout, 'stderr': r.stderr})
        except subprocess.TimeoutExpired:
            results.append({'command': command, 'exit_code': None, 'failure': 'timeout_60_seconds'})
    return results


def evaluate(document):
    verify_preparation(document)
    start = time.perf_counter(); p = document['preparation']; protocol = p['protocol']
    checks = run_checks()
    require(all(r['exit_code'] == 0 for r in checks), 'required test suite failed; evaluation vetoed')
    verify_preparation(document)
    answers = evaluate_chronology(p['references']['chronology'])
    chronology = score_chronology(p['references']['chronology'], answers)
    repetitions = []; workload_start = time.perf_counter()
    for cell in p['references']['workloads']:
        for repetition in range(protocol['repetitions']):
            remaining = protocol['aggregate_timeout_seconds'] - (time.perf_counter() - workload_start)
            raw = {k: v for k, v in cell.items() if k != 'independent_oracle'}
            observed = ({'failure': 'aggregate_budget_exhausted'} if remaining <= 0 else
                        run_child(raw, min(protocol['per_run_timeout_seconds'], remaining)))
            repetitions.append({'id': cell['id'], 'repetition': repetition + 1,
                                'observed': observed, 'score': score_workload(cell, observed)})
    verify_preparation(document)
    try:
        git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, timeout=3)
        provenance = {'commit': git.stdout.strip() if git.returncode == 0 else None,
                      'status': 'uncommitted files identified by content hashes; no commit made',
                      'error': git.stderr.strip() if git.returncode else None}
    except (OSError, subprocess.TimeoutExpired) as exc:
        provenance = {'commit': None, 'error': str(exc)}
    all_passed = chronology['all_passed'] and all(r['score']['passed'] for r in repetitions)
    run = {'created_at': utc(), 'status': 'finite_conformance_pass' if all_passed else 'finite_conformance_failed',
           'chronology_answers': answers, 'chronology_score': chronology,
           'workload_repetitions': repetitions, 'workload_runs_denominator': 15,
           'workload_runs_passed': sum(r['score']['passed'] for r in repetitions),
           'workload_cells_denominator': 5,
           'workload_cells_passed': sum(all(r['score']['passed'] for r in repetitions if r['id'] == c['id']) for c in p['references']['workloads']),
           'checks': checks, 'input_hashes_unchanged': True,
           'manifest': {'command': ['CUDA_VISIBLE_DEVICES=-1', sys.executable, '-B', 'scripts/check_accounting_p12.py', '--evaluate'],
                        'preparation_command': ['CUDA_VISIBLE_DEVICES=-1', sys.executable, '-B', 'scripts/check_accounting_p12.py', '--prepare'],
                        'python': sys.version, 'executable': sys.executable, 'environment': os.environ.get('CONDA_DEFAULT_ENV', 'not declared'),
                        'platform': platform.platform(), 'hardware': 'CPU only; GPU devices intentionally hidden via CUDA_VISIBLE_DEVICES=-1; no framework import',
                        'random_seeds': 'N/A: deterministic finite correctness; timing is not seeded',
                        'git': provenance, 'data_version': 'fixture v1 plus frozen input SHA-256 mapping',
                        'plan_file': PLAN, 'plan_sha256': p['input_hashes'][PLAN],
                        'reference_sha256': p['reference_sha256'], 'preparation_sha256': document['preparation_sha256'],
                        'wall_seconds': time.perf_counter() - start,
                        'output_artifacts': ['data/accounting-master/deliverables/P12/benchmark.json', 'data/accounting-master/deliverables/P12/result.md'],
                        'changed_files': CHANGED}}
    document['runs'].append(run); document['status'] = run['status']
    return document


def render_result(document):
    p = document['preparation']; run = document['runs'][-1]; score = run['chronology_score']
    lines = ['# P12 bounded benchmark result', '',
             f"Status: {run['status']}. Chronology {score['passed']}/12; workloads {run['workload_cells_passed']}/5 cells and {run['workload_runs_passed']}/15 scheduled repetitions.", '',
             'MC28/MC33/MC35 receive bounded internal evidence within G5/G10. No wider gap is closed.', '',
             f"References frozen before component execution: `{p['reference_sha256']}`.",
             f"Preparation hash: `{document['preparation_sha256']}`. All pinned inputs were checked again after execution.", '',
             'Four Apple source references were prepared from retained passages, headers and inline contexts. They are provisional; zero source-extraction tasks were scored. Debt/swap allocation remains unresolved. The scaled assets are reported numerals, not exact unrounded balances.', '',
             'The source panel contains nine purposive issuer families and eight dependent years (2018–2025). Apple, Caterpillar, HSBC and SAIC remain development families; Henkel/Midea validation candidates; JPMorgan/Ping An/Munich Re test candidates. All three test candidates are banking/insurance. Every family has acquisition/QA exposure, Apple has current annotation exposure, and evaluated-model training exposure is unknown. There is no clean heldout claim.', '',
             f"The frozen integrity manifest lists {p['exposure']['retained_original_paths']} original paths, {p['exposure']['unique_original_hashes']} unique hashes and {len(p['exposure']['exact_duplicate_groups'])} exact duplicate groups. Only task-used bytes were reverified here. Comparative tables, mirrors, revisions and language versions remain within issuer family. Semantic duplicate detection is incomplete.", '',
             'Denominators and uncertainty were predeclared: 12 chronology cases (3 valid, 9 invalid), 5 workload cells, 3 repetitions each. Missing/malformed/duplicate/extra replies, crashes, timeouts and unexpected abstentions fail. Expected invalid/partial/unsupported outcomes pass only their specified rules. No result was excluded. These are deterministic finite checks; timing differences are descriptive without population inference or ranking.', '',
             '| Decision | Primary criterion | Veto diagnostics | Main uncertainty | Next action | Not concluded |',
             '| --- | --- | --- | --- | --- | --- |',
             f"| {'Retain bounded engineering result' if run['status']=='finite_conformance_pass' else 'Repair candidate/harness'} | {score['passed']}/12 and {run['workload_runs_passed']}/15 | See case/run diagnostics in benchmark.json; pinned inputs unchanged | Synthetic coverage and provisional source interpretation | Independent result review and wider internal preparation | Accounting/forecast validity, production capacity, whole-gap closure |", '',
             '| Inference status | Finding |', '| --- | --- |',
             '| Hard veto screen | Incorrect fields, lost branches, false completeness and missing measurements explicitly checked; failures retained per case |',
             '| Statistically supported ranking | None; one deterministic implementation, no stochastic comparison |',
             '| Descriptive-only differences | Three fresh-process timing/RSS/allocation observations per cell |',
             '| Default-readiness | Not established; budgets remain convenience choices |',
             '| Next evidence needed | Broader adjudicated tasks and realistic workloads; matched replicated performance study before any ranking |', '',
             '| Workload | Facts / variables / labelled constraints / formula nodes | Potential / explored / feasible / infeasible / unresolved | Kernel seconds (three runs) | Peak RSS bytes (three runs) | Python allocation peak bytes (three runs) |',
             '| --- | --- | --- | --- | --- | --- |']
    for cell in p['references']['workloads']:
        rows = [r for r in run['workload_repetitions'] if r['id'] == cell['id']]
        ms = [r['observed'].get('metrics') if isinstance(r['observed'], dict) else None for r in rows]
        ms = [m if isinstance(m, dict) else {} for m in ms]; m = ms[0]
        sizes = ' / '.join(str(m.get(k, 'missing')) for k in ('input_facts', 'variables', 'labelled_constraints', 'formula_nodes'))
        branches = ' / '.join(str(m.get(k, 'unknown')) for k in ('potential_branches', 'explored_branches', 'retained_feasible_branches', 'infeasible_branches', 'unresolved_branches'))
        timings = ', '.join(str(round(x['kernel_wall_seconds'], 6))
                            if type(x.get('kernel_wall_seconds')) in (int, float)
                            and (type(x['kernel_wall_seconds']) is int or math.isfinite(x['kernel_wall_seconds']))
                            else 'missing/invalid' for x in ms)
        rss = ', '.join(str(x.get('peak_rss_bytes', 'missing')) for x in ms)
        allocation = ', '.join(str(x.get('python_allocation_peak_bytes', 'missing')) for x in ms)
        lines.append(f"| {cell['id']} | {sizes} | {branches} | {timings} | {rss} | {allocation} |")
    lines += ['', 'Facts count explicit domain entries, weights and threshold. Generated/assignment constraints, serialized bytes, complete replies, wall/CPU time and units are retained per repetition in benchmark.json. RSS is a process lifetime high-water mark; tracemalloc measures Python allocations only. Unsupported solver coverage is unknown (None), not zero proved branches. Source page counts are never capacity evidence.', '',
              'The independent standard-library enumerator compared every assignment and exact weighted output on identical inputs. It is a correctness comparator, not a timed competing system. The deliberately insufficient assignment budget retains an unresolved remainder; nonlinear input is explicitly unsupported.', '',
              'Engineering correctness: bounded finite conformance only. Numerical validity: exact rational answers and explicit coverage within these fixtures. Accounting validity, empirical forecast validity and human acceptance: unestablished.', '',
              'Post-run red-team: a common misunderstanding of the specification could affect both manual references and tests. Broader independent source adjudication or a counterexample would overturn a generalized interpretation. The weakest evidence is generalization from tiny synthetic tasks and four provisional source records. Candidate failure would trigger implementation diagnosis, not rejection of the research direction.', '',
              'Remaining internal work: semantic duplicate analysis, report-wide source annotation, debt/swap instrument allocation, historical retained-byte availability, realistic workload scaling, wider calendars/revisions and source-to-forecast tasks. No professional engagement or paid-review readiness is claimed.', '',
              'Executed required checks:', '']
    for check in run['checks']:
        lines.append('- `' + ' '.join(check['command']) + f"`: exit {check['exit_code']}; " + check.get('stderr', '').strip().replace('\n', ' ')[-220:])
    if 'repair' in document:
        lines += ['', f"Harness revision {p['revision']} repairs malformed-response retention and unsupported-coverage validation. The earlier benchmark, report and changed source files are preserved verbatim in benchmark.json under prior_evidence, with content hashes. Its passing run is superseded by the recorded harness defects. Reference answers and task denominators are unchanged; only the repaired preparation supplies current results."]
    lines += ['', f"Total evaluation/check wall time: {run['manifest']['wall_seconds']:.3f} seconds. Interpreter: `{run['manifest']['executable']}`. GPU devices intentionally hidden. Exact commands, package version, input/code hashes, Git observation, changed files and individual diagnostics are preserved in benchmark.json.", '']
    return '\n'.join(lines)
