"""Read-only native replay from a declared bundle; fresh outputs only."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.output.resolve()
    assert out.is_relative_to(root) and out != root
    assert Path(__file__).resolve().is_relative_to(root)
    out.mkdir(exist_ok=False)
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    sys.dont_write_bytecode = True
    started = time.monotonic()
    accesses, imports, libraries, violations = set(), set(), set(), []
    environment = sorted({str(Path(sys.prefix).resolve()), str(Path(sys.base_prefix).resolve())})
    env_roots = [Path(p) for p in environment]

    def classify(path):
        if path.is_relative_to(out):
            return 'output'
        if path.is_relative_to(root):
            return 'bundle'
        if any(path.is_relative_to(p) for p in env_roots):
            return 'installed_environment'
        return 'undeclared'

    def refuse(event, detail):
        violations.append({'event': event, 'detail': str(detail)})
        raise RuntimeError('undeclared access: ' + event + ': ' + str(detail))

    def audit(event, values):
        if event == 'open':
            name, mode, flags = values
            if isinstance(name, int):
                # Pre-existing stdout/stderr descriptors are not file dependencies.
                if name not in (0, 1, 2):
                    refuse(event, 'file descriptor ' + str(name))
                return
            path = Path(os.fsdecode(name)).resolve()
            write = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            kind = classify(path)
            accesses.add((str(path), 'write' if write else 'read', kind))
            if (write and kind != 'output') or (not write and kind == 'undeclared'):
                refuse(event, path)
        elif event == 'import':
            imports.add((str(values[0]), str(values[1])))
        elif event == 'ctypes.dlopen':
            name = values[0]
            libraries.add(str(name))
            if name is not None and (not os.path.isabs(name) or classify(Path(name).resolve()) == 'undeclared'):
                refuse(event, name)
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime'):
            if classify(Path(os.fsdecode(values[0])).resolve()) != 'output':
                refuse(event, values[0])
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            if any(classify(Path(os.fsdecode(p)).resolve()) != 'output' for p in values[:2]):
                refuse(event, values[:2])
        elif event in ('subprocess.Popen', 'os.system', 'os.exec', 'socket.connect', 'socket.bind'):
            refuse(event, values[0])

    sys.addaudithook(audit)  # Before manifest reads and every project import.
    checks, results, normalized, certificate_comparisons = [], [], [], []

    def check(name, actual, expected=True):
        passed = actual == expected
        checks.append({'name': name, 'passed': passed})
        if not passed:
            raise AssertionError(name)

    def compare(name, actual, expected):
        # Only these inspected native timing fields are nonsemantic. Preserve
        # both raw results and every removed value; all other fields match exactly.
        left, right = deepcopy(actual), deepcopy(expected)
        timing_cases = {'selected history', 'zero_cells', 'missing_history_premise',
                        'incompatible_opening_mapping'}
        contexts = {'70b494c688da0d271ce6c897c5f7bd95eea2e50a79328d35fc80d3008e7995b2',
                    '31049a84a507b4582d49e62f042eb209bfc4da627b467521e4018e0fb5433f38'}
        if name in timing_cases:
            for context in contexts:
                a = left['attachments'][context]
                b = right['attachments'][context]
                check(name + ': timing field presence ' + context,
                      'solver_wall_seconds' in a, 'solver_wall_seconds' in b)
                if 'solver_wall_seconds' in b:
                    av, bv = a.pop('solver_wall_seconds'), b.pop('solver_wall_seconds')
                    check(name + ': timing finite and nonnegative ' + context,
                          all(type(v) in (int,float) and 0 <= v < float('inf') for v in [av,bv]))
                    normalized.append({'case':name,'path':'/attachments/'+context+'/solver_wall_seconds',
                                       'actual':av,'expected':bv})
        if name == 'incompatible_opening_mapping':
            for context in contexts:
                a, b = left['attachments'][context], right['attachments'][context]
                check(name + ': one contradiction ' + context, (len(a['conflicts']),len(b['conflicts'])), (1,1))
                ac, bc = a['conflicts'][0], b['conflicts'][0]
                check(name + ': same conflict labels ' + context, sorted(ac['labels']), sorted(bc['labels']))
                definition = a['definition']
                observation = next(label[len('mapping:'):] for label in ac['labels'] if label.startswith('mapping:'))
                binding = definition['bindings'][observation]
                term, = binding['terms']
                history = definition['history']
                domain = history['accounts'][term['field']]['interval']
                measurement = definition['measurements']['observations'][observation]
                check(name + ': opening snapshot contradiction ' + context,
                      binding['kind']=='snapshot' and term['kind']=='account' and
                      term['coefficient']['value']=='1/1' and domain['lower']==domain['upper'] and
                      measurement['type']['time']['at']==history['opening_date'] and
                      all(e['date'] > history['opening_date'] for e in history['events']))
                try:
                    independent.interval(Q(domain['lower']), measurement['interval'])
                except AssertionError:
                    check(name + ': independent disjoint amounts ' + context, True)
                else:
                    check(name + ': independent disjoint amounts ' + context, False)
                certificate_comparisons.append({'case':name,'context':context,
                    'rule':'Order of identical conjunctive conflict labels only; independent disjoint opening interval check',
                    'actual_label_order':ac['labels'],'frozen_label_order':bc['labels'],
                    'opening_amount':domain['lower'],'source_interval':measurement['interval']})
                ac['labels'], bc['labels'] = sorted(ac['labels']), sorted(bc['labels'])
        if name == 'missing_history_premise':
            context = '31049a84a507b4582d49e62f042eb209bfc4da627b467521e4018e0fb5433f38'
            a, b = left['attachments'][context], right['attachments'][context]
            check(name + ': same witness target', a['definition'], b['definition'])
            check(name + ': same certificate keys', set(a['witness']), set(b['witness']))
            validation = {}
            for label, child in [('actual',a),('frozen',b)]:
                validation[label] = independent.check(child['definition'], child['witness'], child['replay'])
                projection = {json.loads(k)[1]:v for k,v in child['witness'].items()
                              if json.loads(k)[0] == 'measurement'}
                check(name + ': complete measurement certificate ' + label,
                      child['replay']['measurement_witness'], projection)
            changed = []
            for key, value in a['witness'].items():
                if value == b['witness'][key]:
                    continue
                category, identifier = json.loads(key)
                check(name + ': only unbound source certificate differs ' + key,
                      category == 'measurement' and identifier not in a['definition']['bindings'])
                changed.append({'measurement':identifier,'actual':value,'frozen':b['witness'][key]})
                a['witness'][key] = b['witness'][key]
                a['replay']['measurement_witness'][identifier] = b['replay']['measurement_witness'][identifier]
            certificate_comparisons.append({'case':name,'context':context,
                'rule':'Both full certificates satisfy the identical target; only unbound source measurement choices may differ',
                'independent_checks':validation,'different_choices':changed})
        check(name + ': complete semantic result', left, right)

    try:
        manifest = read(root / 'replay-manifest.json')
        check('isolated interpreter', sys.flags.isolated, 1)
        check('retained Python version', sys.version.split()[0], '3.11.15')
        check('original worktree excluded', not root.is_relative_to(Path(manifest['original_root'])))
        for name, entry in manifest['entries'].items():
            check('before identity: ' + name, digest(root / name), entry['sha256'])
        sys.path.insert(0, str(root / 'scripts'))
        import conditional_company_opening_v1 as opening
        import conditional_company_continuation_v1 as continuation
        import company_book_carry_v1 as carry
        import z3
        import importlib.metadata
        check('retained Z3 version', z3.get_version_string(), '4.16.0')
        base = root / 'data/accounting-master'
        selected_dir = base / 'selected-reading-history-20261027'
        selected = load('isolated_selected_reading_history', selected_dir / 'compose.py')
        independent = load('isolated_history_independent', selected_dir / 'independent_check.py')
        source_independent = load('isolated_source_independent',
            base / 'debt-reading-network-20261027/independent_check.py')

        rows = read(base / 'source-opening-compatibility-20261027/attempt-01/cases.json')
        check('declared compatibility population', len(rows), 26)
        for row in rows:
            name, req = row['case'], deepcopy(row['request'])
            before = deepcopy(req)
            profile = req['profile']
            fn = {opening.PROFILE: opening.map_opening,
                  continuation.PROFILE: continuation.run, carry.PROFILE: carry.propose}[profile]
            actual = fn(req)
            results.append({'case': name, 'request': req, 'result': actual})
            compare(name, actual, row['result'])
            check(name + ': unchanged request', req, before)
            if name.startswith('opening:'):
                book = actual['opening']
                cash = book['cash_account']
                equity = next(k for k,v in book['accounts'].items() if v['classification'] == 'equity')
                check(name + ': independent balances', book['balances'], {cash:'15/1',equity:'-15/1'})
                sales = '5/1' if '(10, 2, 3)' in name else '7/1'
                check(name + ': independent memory', book['memory'], {'history': {'sales/a~1':sales}})
                check(name + ': complete source', actual['provenance']['attachment_definition'], req['attachment'])
                check(name + ': dated opening', book['date'], '2025-01-01')
                check(name + ': events', book['seen'], ['early','late'])
                check(name + ': no current flows', book['flows'], [])
            elif name.startswith('continuation:'):
                initial, current, report = req['opening_result']['opening'], actual['current'], actual['report']
                cash = initial['cash_account']
                equity = next(k for k,v in initial['accounts'].items() if v['classification'] == 'equity')
                check(name + ': independent balances', current['balances'], {cash:'14/1',equity:'-14/1'})
                check(name + ': independent journal', actual['transition']['journal'], {cash:'-1/1',equity:'1/1'})
                check(name + ': preserved memory', current['memory'], initial['memory'])
                check(name + ': preserved source', actual['opening_result'], req['opening_result'])
                check(name + ': income', report['income'], {'income':'0/1','expenses':'0/1','profit':'0/1'})
                check(name + ': financing', report['cash_flows']['activities']['financing'],
                      {'receipts':'0/1','payments':'1/1','net':'-1/1'})
                check(name + ': equity movement', report['equity']['direct_movements'], '-1/1')
                check(name + ': closing equity', report['equity']['closing'], '14/1')
                check(name + ': all reconciliations', set(report['reconciliations'].values()), {'0/1'})
            elif name.startswith('carry:'):
                old, new = req['report_request']['closing'], actual['next_opening']
                check(name + ': zero cash journal', actual['journal'][old['cash_account']], '0/1')
                check(name + ': balanced close', sum(map(Q, actual['journal'].values())), Q(0))
                check(name + ': event continuity', new['seen'], old['seen'] + [req['close_id']])
                check(name + ': reset flows', new['flows'], [])
                if name != 'carry:native_balances':
                    retained = '-102/1' if name == 'carry:loss.alpha' else '-130/1'
                    change = '3/1' if name == 'carry:loss.alpha' else '-25/1'
                    expected_balances = {k: '0/1' if v['classification'] in ('income','expense')
                        else retained if k == req['retained_account'] else old['balances'][k]
                        for k,v in old['accounts'].items()}
                    check(name + ': all independent balances', new['balances'], expected_balances)
                    check(name + ': independent closing journal', actual['journal'][req['retained_account']], change)
                    check(name + ': memory preserved', new['memory'], old['memory'])
                else:
                    native = read(base / 'company-return-execution-20261024/trace.json')['next_opening']
                    check(name + ': original native balances', new['balances'], native['balances'])
            elif actual['status'] in ('invalid','unresolved'):
                check(name + ': no successful book', all(k not in actual for k in ['opening','current','next_opening']))
        dump(out / 'compatibility-cases.json', results)

        body = read(selected_dir / 'attempt-01/request.json')
        before = deepcopy(body)
        result = selected.assess(body)
        dump(out / 'selected-history.json', {'request': body, 'result': result})
        compare('selected history', result, read(selected_dir / 'attempt-01/result.json'))
        check('selected request unchanged', body, before)
        check('distinct retained budgets', (body['source_parent']['budget']['max_formula_nodes'], body['budget']['max_formula_nodes']), (20000,10000))
        check('complete selected counts', (result['selected_observations'],result['selected_relations'],result['context_count']), (236,101,2))
        source = read(base / 'debt-reading-network-20261027/attempt-01/full-result.json')
        check('source definition retained', result['selected_source']['definition'], source['definition'])
        obligations, observations, relations, witness_checks = 0, {}, {}, {}
        for context, child in result['attachments'].items():
            definition = child['definition']
            witness_checks[context] = independent.check(definition, child['witness'], child['replay'])
            check('context history ' + context, definition['history'], body['histories'][context]['history'])
            check('context bindings ' + context, definition['bindings'], body['histories'][context]['bindings'])
            check('source scale ' + context, definition['history']['value_type']['scale'], '1000000/1')
            unmapped = set(definition['measurements']['observations']) - set(definition['bindings'])
            check('unmapped quantities ' + context, set(child['unmapped_observations']), unmapped)
            check('context obligations ' + context, len(child['target_obligations']), len(unmapped)+2)
            check('actual history unknown ' + context, child['target_existence'], 'unknown')
            obligations += len(child['target_obligations'])
            for key, value in definition['measurements']['observations'].items():
                check('unique observation ' + key, key not in observations)
                observations[key] = value
            for value in definition['measurements']['relations']:
                check('unique equation ' + value['id'], value['id'] not in relations)
                relations[value['id']] = value
        check('all 180 obligations', obligations, 180)
        check('complete observation partition', observations, source['definition']['observations'])
        check('complete equation partition', relations, {r['id']:r for r in source['definition']['relations']})
        child = next(iter(result['attachments'].values()))
        for category in ['history','measurement']:
            changed = deepcopy(child['witness'])
            key = next(k for k in changed if json.loads(k)[0] == category)
            changed[key] = str(Q(changed[key])+1)
            try:
                independent.check(child['definition'], changed, child['replay'])
            except AssertionError:
                check('independent checker rejects changed ' + category, True)
            else:
                check('independent checker rejects changed ' + category, False)
        witnesses = read(base / 'debt-reading-network-20261027/attempt-01/witnesses.json')
        for key in ['primary','nonzero']:
            witness_checks['source_' + key] = source_independent.check(source['definition'], witnesses[key])
            check('complete source witness ' + key, witness_checks['source_'+key],
                  {'complete_values':236,'checked_intervals':236,'checked_equations':101})
        dump(out / 'independent-checks.json', witness_checks)

        controls = read(selected_dir / 'attempt-01/controls.json')
        check('declared selected controls', len(controls), 10)
        for row in controls:
            name = row['name']
            frozen = read(selected_dir / 'attempt-01' / (name + '.json'))
            req, before = deepcopy(frozen['request']), deepcopy(frozen['request'])
            actual = selected.assess(req)
            dump(out / ('selected-' + name + '.json'), {'request':req,'result':actual})
            compare(name, actual, frozen['result'])
            check(name + ': declared status', actual['status'], row['expected'])
            check(name + ': unchanged request', req, before)
            check(name + ': no issuer opening', actual['executable_opening'] is None)

        for name, entry in manifest['entries'].items():
            check('after identity: ' + name, digest(root / name), entry['sha256'])
        modules = sorted({str(Path(m.__file__).resolve()) for m in list(sys.modules.values())
            if getattr(m, '__file__', None) and not m.__file__.startswith('<')})
        for path in modules:
            check('module within declared roots: ' + path, classify(Path(path)) in ('bundle','installed_environment'))
            if classify(Path(path)) == 'bundle':
                check('module inventoried: ' + path, str(Path(path).relative_to(root)) in manifest['entries'])
        # Exact import-time reads may include unsuccessful bytecode probes. Successful
        # bundle files must be inventoried; missing probes are retained in the audit.
        for path, mode, kind in list(accesses):
            if kind == 'bundle' and mode == 'read' and Path(path).is_file():
                check('read inventoried: ' + path, Path(path).name == 'replay-manifest.json' or
                      str(Path(path).relative_to(root)) in manifest['entries'])
        check('no undeclared access', violations, [])
        versions = {name:importlib.metadata.version(name) for name in
                    ['z3-solver','jsonschema','attrs','referencing','rpds-py','jsonschema-specifications']}
        summary = dict(passed=True, compatibility_exchanges=26, selected_history_exchanges=11,
                       checks=len(checks), normalized_fields=normalized,
                       certificate_comparisons=certificate_comparisons, obligations=obligations)
        dump(out / 'checks.json', {**summary,'details':checks})
        dump(out / 'run-manifest.json', {
            'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'git_commit':'N/A: unusable .git marker; no repository initialized',
            'command':[sys.executable,'-I','-B',*sys.argv],
            'python':sys.version,'environment_roots':environment,'distributions':versions,
            'cpu_gpu':'CPU-only Python/Z3; GPU intentionally hidden before project imports',
            'random_seeds':'N/A: exact conformance, not stochastic ranking',
            'wall_seconds':time.monotonic()-started,'data_version':digest(root / 'replay-manifest.json'),
            'plan':'docs/plans/accounting-executable-evidence-closure-20261027.md',
            'result':'data/accounting-master/executable-evidence-closure-20261027/result.md',
            'observed_modules':modules,'scope':manifest['excluded'],
            'artifacts':sorted(p.name for p in out.iterdir()) + ['access-audit.json'],
        })
        print(json.dumps(summary))
    except Exception as exc:
        dump(out / 'failure.json', {'error':str(exc),'type':type(exc).__name__,'checks':checks})
        raise
    finally:
        dump(out / 'access-audit.json', {
            'hook_before_project_imports':True,
            'reads_and_writes':[dict(path=p, mode=m, classification=k) for p,m,k in sorted(accesses)],
            'imports':sorted(imports),'dynamic_libraries':sorted(libraries),'violations':violations,
            'limit':'Python-visible accesses only; interpreter startup and native syscalls are not audited',
        })


if __name__ == '__main__':
    main()
