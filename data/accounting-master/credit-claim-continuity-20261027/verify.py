"""One-shot independent evidence writer; never overwrite an earlier attempt."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json, os, platform, subprocess, sys, time
import claim as m


def main():
    started = time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    attempt = sys.argv[1]
    assert attempt in ['01', '02', '03']
    out = m.HERE / ('attempt-' + attempt); out.mkdir(exist_ok=False)
    checks, cases, controls, boundaries = [], [], [], []

    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2) + '\n')

    def ck(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def add(total, key, due, value):
        total[key][due] = str(Q(total[key].get(due, '0')) + Q(value))

    lock = m.protected()
    sources = {str(p.relative_to(m.ROOT)): sha256(p.read_bytes()).hexdigest()
               for p in m.HERE.iterdir() if p.is_file()}
    save('source-lock.json', {**lock['files'], **sources})
    try:
        endpoints = json.loads((m.HERE / 'authored-endpoints.json').read_text())['cases']
        retained = json.loads((m.NATIVE / 'attempt-01/exchanges.json').read_text())
        ck('authored_case_population', list(endpoints) == [r['id'] for r in retained])
        sys.path.insert(0, str(m.ROOT / 'scripts'))
        import credit_linked_schedule_v1 as linked
        native, _ = linked.load_native()
        for row in retained:
            ident = row['id']; req, saved = row['request'], row['result']
            body = m.request(ident); before = deepcopy(row)
            result = m.assess(body)
            ck(ident + ':accepted', result['status'] == 'checked_read_only')
            ck(ident + ':endpoint', result['endpoint'] == endpoints[ident])
            ck(ident + ':unchanged_input', row == before)
            ck(ident + ':all_flags', all(result[k] == v for k, v in m.FLAGS.items()))
            ck(ident + ':validated', m.validate(body, result, m.digest(result))['status'] == 'verified')
            ck(ident + ':native_replay', native.calculate(deepcopy(req)) == saved)
            # Independent oracle: use archived portions/collections and native
            # before/after snapshots, never the candidate transition routine.
            total = {k: {} for k in ['collections', 'uncollected', 'writeoff', 'revisions']}
            movements, replacements = [], []
            writes = iter(saved['writeoff_contract'])
            unpaid = iter(saved['uncollected_contract'])
            receipts = iter(f for f in saved['cash_flows'] if f['kind'] == 'collection')
            expected_stage_ids = ['acquisition']
            for e in req['events']:
                expected_stage_ids.extend([e['id'] + '_accrual', e['id']])
            ck(ident + ':complete_stage_order', [s['stage_id'] for s in result['timeline']] == expected_stage_ids)

            def movement(index, e, component, due, value, portion=None):
                value = str(Q(value)); add(total, component, due, value)
                movements.append({'movement_index': len(movements), 'source_event_index': index,
                    'source_event_id': e['id'], 'source_event_sha256': m.digest(e),
                    'event_date': e['date'], 'information_date': e['information_date'],
                    'component': component, 'due_date': due, 'amount': value,
                    'portion_id': portion, 'legal_forgiveness': 'not_assessed'})

            for j, s in enumerate(saved['stages']):
                e = req['events'][(j - 1) // 2] if j else req['acquisition']
                if j and j % 2 == 0:
                    index = (j - 1) // 2; kind = e['operation']
                    pre = saved['stages'][j - 1]['remaining_contract']; post = s['remaining_contract']
                    if kind == 'credit_revision' and Q(e['writeoff']['fraction']):
                        w = next(writes)
                        ck(ident + ':' + s['id'] + ':portion_source', w['portion_id'] == e['writeoff']['portion_id'] and w['date'] == e['date'])
                        for d, value in w['contractual_cash'].items():
                            ck(ident + ':' + s['id'] + ':removed:' + d, Q(value) == Q(pre[d]) - Q(post[d]))
                            movement(index, e, 'writeoff', d, value, w['portion_id'])
                    elif kind == 'collect':
                        c, u = next(receipts), next(unpaid)
                        ck(ident + ':' + s['id'] + ':receipt_source', c['date'] == u['due_date'] == e['date'] and c['amount'] == e['amount'])
                        ck(ident + ':' + s['id'] + ':due_allocation', Q(c['amount']) + Q(u['amount']) == Q(pre[e['date']]) and e['date'] not in post)
                        movement(index, e, 'collections', c['date'], c['amount'])
                        movement(index, e, 'uncollected', u['due_date'], u['amount'])
                    elif kind == 'estimate_revision':
                        ck(ident + ':' + s['id'] + ':replacement_source', post == e['expected'])
                        replacements.append({'source_event_id': e['id'], 'source_event_sha256': m.digest(e),
                            'date': e['date'], 'before': deepcopy(pre), 'after': deepcopy(post),
                            'meaning': 'modeled_receipt_schedule_replacement',
                            'unchanged_terms_finding': e['findings']['unchanged_terms']})
                        for d in sorted(set(pre) | set(post)):
                            movement(index, e, 'revisions', d, Q(post.get(d, '0')) - Q(pre.get(d, '0')))
                    else:
                        ck(ident + ':' + s['id'] + ':unchanged_nominal', pre == post)
                actual = result['timeline'][j]
                ck(ident + ':' + s['id'] + ':complete_stage',
                   actual['remaining'] == s['remaining_contract'] and actual['totals'] == total
                   and actual['movement_count'] == len(movements)
                   and actual['source_sha256'] == m.digest(e)
                   and actual['native_stage_sha256'] == m.digest(s)
                   and (actual['stage_index'], actual['date'], actual['kind']) == (j, s['date'], s['kind']))
                dates = sorted(set(req['acquisition']['contract']) | set(s['remaining_contract']) |
                               {d for values in total.values() for d in values})
                ck(ident + ':' + s['id'] + ':complete_dates', [x['due_date'] for x in actual['per_due_date']] == dates)
                for d, a in zip(dates, actual['per_due_date']):
                    initial = req['acquisition']['contract'].get(d, '0')
                    remaining = s['remaining_contract'].get(d, '0')
                    lhs = Q(initial) + Q(total['revisions'].get(d, '0'))
                    rhs = Q(remaining) + sum((Q(total[k].get(d, '0')) for k in ['collections', 'uncollected', 'writeoff']), Q(0))
                    ck(ident + ':' + s['id'] + ':conservation:' + d, lhs == rhs)
                    expected = {'due_date': d, 'original': initial, **{k: total[k].get(d, '0') for k in total},
                                'remaining': remaining, 'remaining_entry_present': d in s['remaining_contract'], 'residual': '0'}
                    ck(ident + ':' + s['id'] + ':complete_components:' + d, a == expected)
            ck(ident + ':full_movement_records', result['movements'] == movements)
            ck(ident + ':full_replacements', result['schedule_replacements'] == replacements)
            for iterator in [writes, unpaid, receipts]:
                ck(ident + ':no_omitted_archive', next(iterator, None) is None)
            for k, h in result['native_financial_components_sha256'].items():
                ck(ident + ':financial_unchanged:' + k, h == m.digest(saved[k]))
            # A real call through the existing native endpoint establishes the
            # after-close boundary. No new monetary receipt is invented.
            extended = deepcopy(req); last = req['events'][-1]
            extended['events'].append({k: deepcopy(last[k]) for k in ['date', 'information_date', 'context', 'findings']} |
                                      {'id': 'probe_after_close', 'operation': 'advance'})
            refusal = native.calculate(extended)
            ck(ident + ':after_close_refusal', refusal['status'] == 'rejected' and refusal['reason'] == 'event_after_close' and refusal['posts'] is False and refusal['mutations'] == [])
            boundaries.append({'case_id': ident, 'request_sha256': m.digest(extended), 'result': refusal})
            cases.append({'request': body, 'result': result, 'record_sha256': m.digest(result)})
        by_id = {x['result']['case_id']: x for x in cases}

        def corrupt(name, case_id, edit):
            base = by_id[case_id]; broken = deepcopy(base['result']); edit(broken)
            verdict = m.validate(base['request'], broken, m.digest(broken))
            ck('control:' + name, verdict['status'] == 'rejected')
            controls.append({'name': name, 'case_id': case_id, 'fresh_hash': m.digest(broken), 'verdict': verdict})

        p = 'partial-early-writeoff'; f = 'full-early-writeoff'; z = 'zero-rate'; e = 'performing-prepayment'
        corrupt('lost_portion', p, lambda x: x['movements'].pop(0))
        corrupt('duplicate_portion', p, lambda x: x['movements'].insert(0, deepcopy(x['movements'][0])))
        corrupt('wrong_due_date_same_total', p, lambda x: x['movements'][0].update(due_date='2027-01-01'))
        corrupt('wrong_event_date', p, lambda x: x['movements'][0].update(event_date='2025-07-02'))
        corrupt('stale_event_hash', p, lambda x: x['movements'][0].update(source_event_sha256='0'*64))
        corrupt('stale_portion', p, lambda x: x['movements'][0].update(portion_id='different'))
        corrupt('changed_event_order', p, lambda x: x['timeline'].reverse())
        corrupt('erased_zero_remaining', f, lambda x: x['timeline'][-1]['remaining'].pop('2026-01-01'))
        corrupt('erased_zero_uncollected', z, lambda x: x['movements'].pop(1))
        corrupt('hidden_replacement', e, lambda x: x.update(schedule_replacements=[]))
        corrupt('wrong_replacement_sign', e, lambda x: x['movements'][1].update(amount='121/2'))
        corrupt('removed_schedule_as_cash', f, lambda x: x['movements'][0].update(component='collections'))
        corrupt('false_forgiveness', p, lambda x: x.update(legal_forgiveness=True))
        corrupt('false_portion_forgiveness', p, lambda x: x['movements'][0].update(legal_forgiveness=True))
        corrupt('false_accounting_admission', p, lambda x: x.update(accounting_admission=True))
        corrupt('false_recovery_admission', p, lambda x: x.update(recovery_admission=True))
        corrupt('false_posting', p, lambda x: x.update(posts=True))
        corrupt('false_legal_schedule_meaning', p, lambda x: x.update(amount_meaning='enforceable_legal_right'))
        corrupt('stale_native_result', p, lambda x: x.update(native_result_sha256='0'*64))
        corrupt('altered_financial_journal_binding', p, lambda x: x['native_financial_components_sha256'].update(journals='0'*64))
        corrupt('aggregate_only', p, lambda x: x['timeline'][-1].update(per_due_date=[]))
        for name, patch in [('stale_request', {'native_request_sha256':'0'*64}),
                            ('stale_result', {'native_result_sha256':'0'*64}),
                            ('unknown_case', {'case_id':'unretained'}), ('unknown_profile', {'profile':'Other/1'})]:
            req = deepcopy(by_id[p]['request']); req.update(patch); v = m.assess(req)
            ck('control:' + name, v['status'] == 'rejected'); controls.append({'name':name,'verdict':v})
        for path, h in {**lock['files'], **sources}.items():
            ck('protected:' + path, sha256((m.ROOT / path).read_bytes()).hexdigest() == h)
        save('cases.json', cases); save('controls.json', controls); save('after-close-boundaries.json', boundaries)
        save('verification.json', {'status':'PASS','cases':len(cases),'stages':sum(len(c['result']['timeline']) for c in cases),
             'assertions':len(checks),'negative_controls':len(controls),'after_close_refusals':len(boundaries),
             'protected_files':len({**lock['files'], **sources}),'checks':checks,'readiness':'not_ready'})
    except Exception as exc:
        save('failure.json', {'type':type(exc).__name__,'reason':str(exc),'checks':checks})
        raise
    finally:
        manifest = {'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=m.ROOT,text=True).strip(),
            'command':'env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str((m.HERE/'verify.py').relative_to(m.ROOT))+' '+attempt,
            'environment':{'python':platform.python_version(),'executable':sys.executable,'libraries':'standard library; pinned local native engine'},
            'cpu_gpu':'CPU only; GPU intentionally hidden; no GPU libraries imported','random_seeds':'N/A deterministic',
            'wall_seconds':round(time.monotonic()-started,3),'data_version':'source-lock.json',
            'plan':'docs/plans/accounting-credit-claim-continuity-20261027.md',
            'result':str((m.HERE/'result.md').relative_to(m.ROOT)),
            'artifacts':{str(p.relative_to(m.ROOT)):sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
        save('run-manifest.json', manifest)
    print(json.dumps({k:v for k,v in json.loads((out/'verification.json').read_text()).items() if k != 'checks'} | {'wall_seconds':manifest['wall_seconds']}))


if __name__ == '__main__':
    main()
