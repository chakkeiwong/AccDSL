"""Compare whole financial exchanges, migration and collision recovery."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import ast
import json
import os
import subprocess
import sys
import time
from native import HERE, ROOT, ATT, OLD, n, idx
from successor import Auditor, Store, POLICY

def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    start = time.monotonic()
    lock = json.loads((HERE / 'source-lock.json').read_text())
    checks, controls, comparisons = [], [], []
    def check(name, condition):
        checks.append(dict(check=name, passed=bool(condition)))
        if not condition:
            raise AssertionError(name)
    def refused(name, expected, action):
        try:
            action()
        except (n.Refusal, n.FinanceRefusal, idx.Refusal) as error:
            code = getattr(error, 'code', str(error))
            controls.append(dict(control=name, expected=expected, observed=code))
            check(name, code == expected)
        else:
            raise AssertionError(name + ':accepted')
    def preservation():
        for name, h in lock.items():
            check('preserved:' + name, digest(ROOT / name) == h)
    preservation()
    delta = json.loads((HERE / 'protocol-delta.json').read_text())
    source = (OLD / 'verify_exchanges.py').read_text()
    native_class = next(x for x in ast.parse(source).body if isinstance(x, ast.ClassDef) and x.name == 'Auditor')
    adapted = (HERE / 'adapted_protocol.py').read_text()
    adapted_class = next(x for x in ast.parse(adapted).body if isinstance(x, ast.ClassDef))
    for name in ('request', 'exchange'):
        original = next(x for x in native_class.body if isinstance(x, ast.FunctionDef) and x.name == name)
        changed = next(x for x in adapted_class.body if isinstance(x, ast.FunctionDef) and x.name == name)
        expected = '\n'.join(source.splitlines()[original.lineno-1:original.end_lineno]).replace(delta['old'], delta['new'])
        actual = '\n'.join(adapted.splitlines()[changed.lineno-1:changed.end_lineno])
        check('only_identity_expression_changed:' + name, actual == expected)
    check('adapted_source_pinned', digest(HERE / 'adapted_protocol.py') == delta['adapted_sha256'])

    store = Store()
    base = store.base
    base.sources()
    for h, record in base.reg.items():
        base.shape(record, h)
        store.checked_base.add(h)
    publications = [e for e in base.p['exchanges'] if e['role'] == 'publication']
    by_response = {e['response_ref']['digest']: e for e in publications}
    by_id = {e['id']: e for e in base.p['exchanges']}
    def history(world):
        return [by_response[d['response_ref']['digest']] for d in world['decisions'].values()]
    seen = set()
    for publication in publications:
        for field in ('world_before', 'world_after'):
            world = publication[field]
            signature = n.sha(n.enc(world))
            if signature not in seen:
                seen.add(signature)
                original = deepcopy(world)
                converted = store.migrate(world, history(world))
                check('migration_world_exact:' + signature[:12], converted == store.mapped_world(world) and world == original)
    for old in base.p['exchanges']:
        base.exchange(old)
        response = base.body(old['response_ref'])
        label = base.record(old['response_ref'])['key'].removeprefix('response.')
        new = store.execute(label, old['request_ref'], old['submission_ref'], store.mapped_world(old['world_before']),
                            response['output_ref'] if response['output_ref'] and response['output_ref']['kind'] == 'ComponentReport' else None)
        new['id'], new['role'] = old['id'], old['role']
        matched = new['response_ref'] == old['response_ref'] and new['world_after'] == store.mapped_world(old['world_after'])
        check('full_exchange:' + old['id'], matched)
        comparisons.append(dict(exchange=old['id'], response_ref_preserved=new['response_ref'] == old['response_ref'],
                                full_world_preserved=new['world_after'] == store.mapped_world(old['world_after'])))
    for crash in base.p['crash_worlds']:
        base.crash(crash)
    for challenge in base.p['challenges']:
        base.challenge(challenge)
    base.completeness()

    # Two consecutive, valid cash/acquisition postings, not two metadata lookups.
    first, second = by_id['acquisition-allocated'], by_id['acquisition-impaired']
    rq1, sub1 = store.request(first['request_ref'], 'identity-first', 'a/b', 'c')
    rq2, sub2 = store.request(second['request_ref'], 'identity-second', 'a', 'b/c')
    opening = store.migrate(first['world_before'], [])
    ex1 = store.execute('identity-first', rq1, sub1, opening)
    between = deepcopy(ex1['world_after'])
    between['current_view_ref'] = second['world_before']['current_view_ref']
    # Demonstrate the false conflict through the actual native request method.
    legacy = n.Auditor(ATT)
    legacy.reg = store.reg
    legacy.p['blobs'].update(store.packet['blobs'])
    old_world = deepcopy(between)
    old_world.pop('identity_profile_ref')
    old_world['decisions'] = {'a/b/c': next(iter(between['decisions'].values()))}
    refused('native_full_request_collision', 'identity_conflict', lambda: legacy.request(rq2, sub2, old_world))
    ex2 = store.execute('identity-second', rq2, sub2, between)
    final = ex2['world_after']
    for label, new, old in [('first', ex1, first), ('second', ex2, second)]:
        output = store.reg[new['response_ref']['digest']]['body']['output_ref']
        expected = base.body(old['response_ref'])['output_ref']
        check('collision_financial_output:' + label, output == expected and new['world_after']['heads'] == old['world_after']['heads'])
    check('collision_two_journals', len(final['journals']) == 2 and [x['lines'] for x in final['journals']] == [x['lines'] for x in second['world_after']['journals']])
    check('collision_two_distinct_decisions', set(final['decisions']) == {idx.pair_key('a/b', 'c'), idx.pair_key('a', 'b/c')})
    for label, rq, sub, original in [('identity-first', rq1, sub1, ex1), ('identity-second', rq2, sub2, ex2)]:
        replay = store.execute(label + '.replay', rq, sub, final)
        old = store.reg[original['response_ref']['digest']]['body']
        now = store.reg[replay['response_ref']['digest']]['body']
        check('collision_retry_exact:' + label, replay['world_after'] == final and
              all(now[k] == old[k] for k in ('request_ref','submission_ref','output_ref','receipt_ref','diagnostics','published_digests')) and not now['additional_commit'])
        recovered = store.execute(label, rq, sub, original['world_before'])
        check('lost_ack_uncommitted:' + label, recovered['response_ref'] == original['response_ref'] and recovered['world_after'] == original['world_after'])
        recovered = store.execute(label + '.replay', rq, sub, original['world_after'])
        check('lost_ack_committed:' + label, recovered['world_after'] == original['world_after'] and not store.reg[recovered['response_ref']['digest']]['body']['additional_commit'])

    changed, changed_sub = store.request(rq1, 'identity-conflict', 'a/b', 'c', require_current=False)
    ex = store.execute('identity-conflict', changed, changed_sub, final)
    check('changed_bytes_conflict', store.reg[ex['response_ref']['digest']]['body']['diagnostics'] == ['identity_conflict'] and ex['world_after'] == final)
    for label, template, w, expected in [('identity-stale-view', rq1, final, 'stale_view'),
                                         ('identity-stale-head', rq2, final, 'stale_head')]:
        rq, sub = store.request(template, label, 'fresh', label)
        ex = store.execute(label, rq, sub, w)
        check(label, store.reg[ex['response_ref']['digest']]['body']['diagnostics'] == [expected] and ex['world_after'] == w)

    # A fresh, rehashed but financially wrong proposal must still be refused.
    proposal_ref = base.body(first['request_ref'])['arguments']['proposal_ref']
    proposal = deepcopy(base.body(proposal_ref))
    result = deepcopy(base.body(proposal['result_ref']))
    cash = result['closing']['accounts']['cash']
    cash['n'] = str(int(cash['n']) + int(cash['d']))
    result_ref = store.add('ComponentResult', 'component.corrupt-identity-test', result)
    proposal['result_ref'] = result_ref
    bad_proposal = store.add('Proposal', 'proposal.corrupt-identity-test', proposal)
    bad_rq, bad_sub = store.request(first['request_ref'], 'identity-invalid-finance', 'fresh', 'invalid-finance', arguments={'proposal_ref': bad_proposal})
    invalid = store.execute('identity-invalid-finance', bad_rq, bad_sub, opening)
    check('complete_request_rejects_wrong_finance', store.reg[invalid['response_ref']['digest']]['body']['diagnostics'] == ['financial_result_mismatch'] and invalid['world_after'] == opening)

    # Distinct independent legacy worlds can retain ambiguous or conflicting
    # decisions even though the old runtime cannot hold both under one key.
    twin_rq, twin_sub = store.request(first['request_ref'], 'legacy-ambiguous-twin', 'a', 'b/c')
    twin = store.execute('legacy-ambiguous-twin', twin_rq, twin_sub, opening)
    conflict_rq, conflict_sub = store.request(first['request_ref'], 'legacy-conflicting-twin', 'a/b', 'c', require_current=False)
    competing = store.execute('legacy-conflicting-twin', conflict_rq, conflict_sub, opening)
    def legacy_exchange(exchange):
        out = deepcopy(exchange)
        for field in ('world_before', 'world_after'):
            w = out[field]
            w.pop('identity_profile_ref')
            entries = {}
            for decision in w['decisions'].values():
                r = store.reg[decision['request_ref']['digest']]['body']
                entries[r['client_id'] + '/' + r['request_id']] = decision
            w['decisions'] = entries
        return out
    left, right, conflict = map(legacy_exchange, (ex1, twin, competing))
    migration_store = Store()
    migration_store.reg = store.reg
    migration_store.base.reg = store.reg
    migration_store.base.p['blobs'].update(store.packet['blobs'])
    refused('ambiguous_full_publication_history', 'ambiguous_legacy_key',
            lambda: migration_store.migrate(left['world_after'], [left, right]))
    refused('conflicting_full_publication_history', 'conflicting_decision_history',
            lambda: migration_store.migrate(left['world_after'], [left, conflict]))

    original_world = deepcopy(first['world_after'])
    retained = history(original_world)
    refused('missing_decision_history', 'incomplete_index_history', lambda: store.migrate(original_world, []))
    damaged = deepcopy(retained)
    damaged[0]['world_after']['journals'] = []
    refused('partial_original_publication', 'partial_publication', lambda: store.migrate(original_world, damaged))
    damaged_world = deepcopy(original_world)
    damaged_world['journals'] = []
    refused('lost_journal_history', 'retained_journal_history', lambda: store.migrate(damaged_world, retained))
    damaged_world = deepcopy(original_world)
    damaged_world['published_records'] = []
    refused('missing_retained_publication', 'retained_publication_missing', lambda: store.migrate(damaged_world, retained))
    refused('already_migrated_world', 'already_bound_world', lambda: store.migrate(final, []))
    check('migration_refusals_preserve_inputs', original_world == first['world_after'] and retained == history(first['world_after']))
    reordered = deepcopy(second['world_after'])
    reordered['decisions'] = dict(reversed(list(reordered['decisions'].items())))
    reordered_after = store.migrate(reordered, list(reversed(history(second['world_after']))))
    check('index_order_is_not_journal_chronology', reordered_after == store.mapped_world(second['world_after']) and reordered_after['journals'] == second['world_after']['journals'])
    duplicated = deepcopy(original_world)
    duplicated['journals'] += deepcopy(original_world['journals'])
    refused('duplicate_financial_posting_in_history', 'retained_journal_history', lambda: store.migrate(duplicated, retained))

    saved_packet = deepcopy(store.packet)
    def fresh(packet=None):
        return Auditor(saved_packet if packet is None else packet)
    missing_policy = deepcopy(final)
    missing_policy.pop('identity_profile_ref')
    refused('unbound_world_before_replay', 'identity_policy_binding', lambda: fresh().request(rq1, sub1, missing_policy))
    wrong_policy = deepcopy(final)
    wrong_policy['identity_profile_ref'] = base.alias['profile']
    refused('wrong_policy_before_replay', 'identity_policy_binding', lambda: fresh().request(rq1, sub1, wrong_policy))
    forged_index = deepcopy(final)
    forged_index['decisions'][idx.pair_key('a/b', 'c')] = final['decisions'][idx.pair_key('a','b/c')]
    refused('transplanted_decision', 'index_key_binding', lambda: fresh().request(rq1, sub1, forged_index))
    bad_packet = deepcopy(saved_packet)
    old_digest = first['request_ref']['digest']
    bad_packet['records'][old_digest] = deepcopy(base.reg[old_digest])
    bad_packet['records'][old_digest]['body']['request_id'] = 'tampered'
    refused('immutable_native_record_collision', 'immutable_record_collision', lambda: fresh(bad_packet))
    bad_packet = deepcopy(saved_packet)
    bad_packet['records'][rq1['digest']]['body']['request_id'] = 'tampered'
    refused('new_record_hash_mismatch', 'record_digest', lambda: fresh(bad_packet).request(rq1, sub1, final))
    bad_packet = deepcopy(saved_packet)
    bad_packet['base_packet_sha256'] = '0' * 64
    refused('wrong_baseline', 'base_packet_changed', lambda: fresh(bad_packet))
    refused('submission_from_other_request', 'wire_binding', lambda: fresh().request(rq1, sub2, final))
    bad_packet = deepcopy(saved_packet)
    policy = bad_packet['records'][bad_packet['identity_profile_ref']['digest']]
    policy['body']['index_format'] = 'wrong'
    refused('changed_policy_shape', 'identity_policy_shape', lambda: fresh(bad_packet).request(rq1, sub1, final))
    a = fresh()
    absent = deepcopy(final)
    absent['published_records'].remove(ex1['response_ref']['digest'])
    refused('erased_response_before_replay', 'retained_publication_missing', lambda: a.request(rq1, sub1, absent))

    dump('portable-successor.json', store.packet)
    reloaded = json.loads((HERE / 'portable-successor.json').read_text())
    audit = Auditor(reloaded)
    for h, record in reloaded['records'].items():
        audit.shape(record, h)
    for exchange in reloaded['exchanges']:
        audit.exchange(exchange)
    for migration in reloaded['migrations']:
        before, after = migration['before'], migration['after']
        check('saved_migration_exact', after == store.mapped_world(before))
    preservation()
    result = dict(passed=True, native_cases=len(base.p['cases']), native_publications=len(publications),
                  native_exchanges=len(comparisons), native_crash_worlds=len(base.p['crash_worlds']),
                  native_adverse_cases=len(base.p['challenges']), migration_worlds=len(seen),
                  collision_financial_posts=2, collision_retries=2, collision_recovery_worlds=4,
                  boundary_controls=len(controls), saved_exchanges_revalidated=len(reloaded['exchanges']),
                  protected_files=len(lock), identity_policy=POLICY, financial_profile='InsuranceComponents/1',
                  source_admission=False, accounting_admission=False, production_ready=False,
                  complete_history='caller_supplied_assumption', checks=len(checks))
    dump('checks.json', result)
    dump('comparisons.json', comparisons)
    dump('controls.json', controls)
    dump('check-detail.json', checks)
    dump('run-manifest.json', dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
          command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/insurance-identity-adoption-20261026/verify.py',
          environment=sys.version, cpu_gpu='CPU; GPU intentionally hidden; no GPU framework imported',
          data_version=digest(ATT / 'portable-exchanges.json'), random_seeds='N/A deterministic exact conformance',
          wall_seconds=time.monotonic()-start, timestamp_utc=datetime.now(timezone.utc).isoformat(),
          plan_file='docs/plans/accounting-insurance-identity-adoption-20261026.md',
          result_file=str((HERE/'result.md').relative_to(ROOT)),
          artifact_paths=['checks.json','comparisons.json','controls.json','portable-successor.json','source-lock.json','protocol-delta.json']))
    print(json.dumps(result), flush=True)

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        dump('last-failure.json', dict(type=type(error).__name__, code=getattr(error,'code',str(error))))
        raise
