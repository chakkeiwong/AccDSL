"""Exact differential checks plus independently authored financial expectations."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import dispatcher as d

ROOT, HERE = d.ROOT, d.HERE
PLAN = 'docs/plans/company-state-common-request-20261028.md'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    inputs = {ROOT / PLAN, HERE / 'dispatcher.py', Path(__file__), HERE / 'registry.json', HERE / 'schema.json'}
    checks, cases = [], {}
    def read(relative):
        p = ROOT / relative; inputs.add(p)
        return json.loads(p.read_text())
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected,
                           actual_sha256=d.digest(actual), expected_sha256=d.digest(expected)))
    packet = read('data/accounting-master/company-path-exchanges-20261023/packet.json')
    records = packet['record_registry']
    root = records[packet['root_ref']['digest']]['body']
    record = next(records[r['digest']]['body'] for r in root['path_refs']
                  if records[r['digest']]['body']['name'] == 'second_year_price_revision')
    ref = record['path_blob']; p = ROOT / packet['blobs'][ref['digest']]['path']; inputs.add(p)
    raw = p.read_bytes()
    assert sha256(raw).hexdigest() == ref['digest'] and len(raw) == ref['byte_length']
    path = json.loads(raw)
    source_path = ROOT / path['initial_year']['source']['path']; inputs.add(source_path)
    source = source_path.read_bytes()
    policy = read('data/accounting-master/company-policy-20261023/policy.json')
    modules = {k: d.native_module(k) for k in d.ENTRIES}
    def envelope(cap, payload, resource=None):
        resources = {} if cap == 'book_report' else {'source': source if resource is None else resource}
        req = dict(profile='CompanyNativeRequest/1', capability=cap, operation=d.ENTRIES[cap][0],
            implementation_sha256=d.registry()[cap]['implementation_sha256'], payload=deepcopy(payload),
            payload_sha256=d.digest(payload), resources=[dict(id=k, sha256=sha256(v).hexdigest(), byte_length=len(v))
                                                        for k,v in resources.items()],
            population=dict(scope='supplied_native_input', actual_company_coverage='unknown'),
            information=dict(use='audit_only', view='archival_exogenous_stress'), joins=[])
        return req, resources
    def state_payload(p):
        req = dict(profile='CompanyStateInspectionRequest/1', owner='CompanyOperationPathDraft/1',
            path_sha256=modules['state_inspection'].rel.native.digest(p), source_sha256=sha256(source).hexdigest(),
            context=deepcopy(p['initial_year']['context']),
            information=dict(use='audit_only', view='archival_exogenous_stress'), joins=[],
            queries=[dict(id='annual', kind='annual_report', period_start=p['initial_year']['period']['start']),
                     dict(id='claim', kind='claim_history', claim_id='opening-ar'),
                     dict(id='prefix', kind='event_prefix', year_index=0, operation_id='collection-1-a')])
        return dict(request=req, path=deepcopy(p))
    def policy_payload(p, pol, role):
        return dict(path=deepcopy(p), request=dict(profile='CompanyPolicyEffectRequest/1',
            owner='CompanyOperationPathDraft/1', role=role, path_sha256=modules['policy_effect'].rel.native.digest(p),
            source_sha256=sha256(source).hexdigest(), context=deepcopy(p['initial_year']['context']),
            information=dict(use='audit_only', view='archival_exogenous_stress'), policy=deepcopy(pol)))
    def run(name, cap, payload, resource=None):
        req, resources = envelope(cap, payload, resource)
        saved = deepcopy((req, resources))
        module = modules[cap]
        if cap == 'book_report':
            direct = module.report(payload['request'])
        else:
            direct = module.inspect(payload['request'], payload['path'], resources['source'])
        result = d.dispatch(req, resources)
        check(name + ': dispatch', result['dispatch_status'], 'returned')
        check(name + ': entire native result', result.get('native_result'), direct)
        check(name + ': immutable', (req, resources) == saved, True)
        check(name + ': result identity', result.get('request_sha256'), d.digest(req))
        for key in ['source_admission', 'actor_information_admission', 'legal_authority_admission',
                    'population_complete', 'full_company_constructor', 'financial_composition', 'physical_durability']:
            check(name + ': ' + key, result[key], False)
        cases[name] = dict(request=req, result=result, direct_result=direct)
        return result['native_result']
    base = state_payload(path)
    r = run('state complete', 'state_inspection', base)
    check('complete native execution', r['admission']['native_result']['status'], 'complete_conditional')
    unknown = deepcopy(path); unknown['initial_year']['opening_claims'][0]['amount'] = 'unknown'
    r = run('state unknown opening', 'state_inspection', state_payload(unknown))
    check('unknown has no population', r['admission']['population_inspection'], None)
    invalid = deepcopy(base); invalid['request']['context']['currency'] = 'EUR'
    r = run('state native invalid', 'state_inspection', invalid)
    check('native invalid preserved', (r['status'], r['reason']), ('invalid', 'context_mismatch'))
    r = run('state corrupt source', 'state_inspection', base, source + b' ')
    check('native raw-byte refusal', (r['status'], r['reason']), ('invalid', 'source_digest'))
    malformed = deepcopy(base); malformed['request'] = {}
    run('state malformed native request', 'state_inspection', malformed)
    for role in ['generate_inputs', 'validate_equalities', 'compare_targets']:
        r = run('policy ' + role, 'policy_effect', policy_payload(path, policy, role))
        if role == 'compare_targets':
            check('independent policy differences', [v['actual_minus_target'] for v in r['comparisons']], ['-36/5'] * 4)
            check('target comparison no equality verdict', r['equality_constraint_result'], None)
        if role == 'validate_equalities':
            check('equality violations', r['status'], 'violates_equalities')
    full = deepcopy(policy); full['fraction'] = '1/1'
    r = run('policy creates partial path', 'policy_effect', policy_payload(path, full, 'generate_inputs'))
    check('partial native outcome survives', r['native_result']['status'], 'partial')
    check('partial native reason survives', r['native_result']['years'][-1]['run']['reason'], 'over_settlement')
    run('state partial path', 'state_inspection', state_payload(r['materialization']['path']))
    up = deepcopy(policy); up['parent_path_sha256'] = modules['policy_effect'].rel.native.digest(unknown)
    r = run('policy unknown opening', 'policy_effect', policy_payload(unknown, up, 'compare_targets'))
    check('unknown target amounts stay absent', [v['actual'] for v in r['comparisons']], [None] * 4)
    unfixed = deepcopy(policy); unfixed['fraction'] = 'unknown'
    r = run('policy unresolved parameter', 'policy_effect', policy_payload(path, unfixed, 'generate_inputs'))
    check('unresolved policy does not execute', r['native_execution_attempted'], False)
    report_cases = read('data/accounting-master/insurance-paa-dated-book-20261027/attempt-01/cases.json')
    authored = read('data/accounting-master/insurance-paa-dated-book-20261027/authored-expectations.json')
    for row in report_cases:
        body = row['result']['execution']['trace'][-1]['request']
        r = run('report ' + row['id'], 'book_report', dict(request=body))
        check(row['id'] + ': retained report', r, row['report'])
        check(row['id'] + ': verification', modules['book_report'].verify(body, r), True)
        check(row['id'] + ': remains interim', (r['as_of'], r['scope'], r['fiscal_complete']),
              ('2024-07-02', 'recorded_period_only', False))
        if row['id'] in authored:
            expected = authored[row['id']]
            check(row['id'] + ': independent balances', body['closing']['balances'], expected['closing'])
        if row['id'] == 'base/named':
            check('independent assets liabilities equity', r['balance_sheet'],
                  dict(total_assets='119/1', total_liabilities='72/1', equity_including_profit='47/1'))
            check('independent profit and cash', (r['income']['profit'], r['cash_flows']['closing_cash']), ('27/1', '101/1'))
    report_body = deepcopy(report_cases[0]['result']['execution']['trace'][-1]['request'])
    report_body['expected_mapping_sha256'] = '0' * 64
    r = run('report stale mapping', 'book_report', dict(request=report_body))
    check('native report refusal', (r['status'], r['reason']), ('invalid', 'stale_mapping'))
    run('report malformed request', 'book_report', dict(request={}))
    control_checks(base, envelope, checks, cases, check)
    check('canonical digest matches native Unicode', d.digest({'label': '公司'}),
          modules['book_report'].digest({'label': '公司'}))
    for module in list(sys.modules.values()) + list(modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and Path(filename).is_file() and Path(filename).resolve().is_relative_to(ROOT):
            inputs.add(Path(filename).resolve())
    # Include transitive native implementation paths from the earlier reviewed manifest.
    prior = read('data/accounting-master/company-state-policy-effects-20261028/attempt-01/run-manifest.json')
    inputs.update(ROOT / p for p in prior['source_hashes'] if p.endswith('.py'))
    failed = [c for c in checks if not c['passed']]
    verification = dict(status='fail' if failed else 'pass', checks=len(checks), cases=len(cases), failed=failed)
    manifest = dict(git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], environment=sys.version,
        cpu_gpu='CPU-only deterministic exact arithmetic; no accelerator imports', random_seeds='N/A deterministic',
        data_version='Retained price-revision path, explicit policy, seven PAA interim report requests',
        utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic() - start,
        plan_file=PLAN, result_file=str((HERE / 'result.md').relative_to(ROOT)),
        output_paths=[str((out / n).relative_to(ROOT)) for n in ['verification.json', 'checks.json', 'results.json.gz']],
        source_hashes={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)})
    for name, value in [('verification', verification), ('checks', checks), ('run-manifest', manifest)]:
        (out / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    (out / 'results.json.gz').write_bytes(gzip.compress(d.canonical(cases), mtime=0))
    for name in ['dispatcher.py', 'check_dispatch.py', 'schema.json', 'registry.json']:
        (out / name).write_bytes((HERE / name).read_bytes())
    print(json.dumps(verification))
    return bool(failed)


def control_checks(base, envelope, checks, cases, check):
    for name, change, status, reason in [
        ('unknown capability', lambda r: r.update(capability='arbitrary_loader'), 'unsupported', 'native_capability'),
        ('unknown operation', lambda r: r.update(operation='execute_python'), 'unsupported', 'native_operation'),
        ('stale implementation', lambda r: r.update(implementation_sha256='0' * 64), 'invalid', 'implementation_digest'),
        ('stale payload', lambda r: r['payload']['request'].update(owner='other'), 'invalid', 'payload_digest'),
        ('unexpected field', lambda r: r.update(callable='eval'), 'invalid', 'envelope_schema'),
        ('missing population', lambda r: r.pop('population'), 'invalid', 'envelope_schema'),
        ('false coverage', lambda r: r['population'].update(actual_company_coverage='complete'), 'invalid', 'envelope_schema'),
        ('join', lambda r: r.update(joins=['BankComponents/1']), 'unsupported', 'cross_profile_join'),
        ('duplicate resource', lambda r: r['resources'].append(deepcopy(r['resources'][0])), 'invalid', 'resource_descriptors'),
        ('wrong byte length', lambda r: r['resources'][0].update(byte_length=0), 'invalid', 'resource_digest'),
    ]:
        req, resources = envelope('state_inspection', base); change(req)
        result = d.dispatch(req, resources); cases[name] = dict(request=req, result=result)
        check(name, (result['dispatch_status'], result['reason']), (status, reason))
        check(name + ': no financial result', 'native_result' in result, False)
    actor = dict(use='actor_action', actor_id='supplied-manager', economic_time='2026-01-01T00:00:00Z',
                 decision_cutoff='2026-01-01T00:00:00Z', system_cutoff='2026-01-01T00:00:00Z',
                 observation_or_action='choose supplied policy', receipt_evidence_refs=['unadmitted-receipt'],
                 authority_evidence_refs=['unadmitted-authority'])
    for use in ['actor_action', 'actor_observation']:
        req, resources = envelope('state_inspection', base); req['information'] = dict(actor, use=use)
        result = d.dispatch(req, resources); cases[use] = dict(request=req, result=result)
        check(use, (result['dispatch_status'], result['reason']), ('unsupported', 'actor_operator_unimplemented'))
        check(use + ': requirements preserved', result['actor_requirement'], req['information'])
    for name, field, value in [('missing actor', 'actor_id', ''), ('bad cutoff', 'decision_cutoff', 'yesterday'),
                               ('missing evidence', 'receipt_evidence_refs', [])]:
        req, resources = envelope('state_inspection', base); req['information'] = deepcopy(actor)
        req['information'][field] = value
        result = d.dispatch(req, resources); cases[name] = dict(request=req, result=result)
        check(name, (result['dispatch_status'], result['reason']), ('invalid', 'envelope_schema'))
    for name, transform, reason in [('missing resource', lambda r: {}, 'resource_set'),
                                  ('text source', lambda r: {'source': 'text'}, 'resource_not_bytes'),
                                  ('corrupt bytes', lambda r: {'source': r['source'] + b' '}, 'resource_digest')]:
        req, resources = envelope('state_inspection', base)
        result = d.dispatch(req, transform(resources)); cases[name] = dict(request=req, result=result)
        check(name, (result['dispatch_status'], result['reason']), ('invalid', reason))


if __name__ == '__main__':
    raise SystemExit(main())
