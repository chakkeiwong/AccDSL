"""Exact finite boundary checks; retains all source identities and failure cases."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import os
import platform
import subprocess
import sys
import time
import traceback

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
from boundary import WORLD, canonical, digest, same, request, propose, need, native_capabilities
from local_context import context


def dump(path, value): path.write_text(json.dumps(value, indent=2)+'\n')
def filehash(path): return sha256(path.read_bytes()).hexdigest()


def checks(trusted):
    out, witnesses = [], {}
    def check(name, value): out.append({'name': name, 'passed': bool(value)})
    projected = trusted['project'](); retained = trusted['migration']
    check('exact_original_projection', same(projected, retained['projected']))
    check('exact_original_afterstate', same(trusted['expected_after'], retained['expected_after']))
    other = deepcopy(projected); other['owner']['entity_id'] = 'Unrelated-synthetic-book'
    world = {'profile': WORLD, 'books': {'original-return-book': projected, 'unrelated-book': other}}
    key = 'original-return-book'; req = request(world, key, trusted)
    original = canonical(world); original_req = canonical(req)
    result = propose(world, req, trusted)
    check('retained_method_proposal_passes', result['status'] == 'proposed')
    check('whole_afterstate_matches_source', same(result['proposed_world']['books'][key], retained['expected_after']))
    check('other_book_unchanged', same(result['proposed_world']['books']['unrelated-book'], other))
    check('input_world_and_request_unchanged', canonical(world) == original and canonical(req) == original_req)
    check('existing_cash_used_once', result['proposed_world']['books'][key]['balances']['cash'] == '52')
    expected = {'cash':'-48','inventory':'20','recovery_asset':'-16','refund_liability':'40',
                'original_equity':'0','revenue':'0','cogs':'-4','selling_expense':'8'}
    check('independent_journal_matches', same(result['journal'], expected))
    check('journal_balances', sum(Fraction(x) for x in result['journal'].values()) == 0)
    cash = result['cash_effects']
    check('gross_cash_payment_48', cash['cash_payments']['operating'] == '48')
    check('gross_cash_receipts_zero', all(Fraction(x) == 0 for x in cash['cash_receipts'].values()))
    check('net_cash_minus_48', cash['cash_movements']['operating'] == '-48')
    check('no_capital_reposting', result['journal']['original_equity'] == '0')
    check('no_commit_or_admission', all(result[k] is False for k in ['committed','physical_durability','historical_admission','forecast_admission']))
    check('deterministic_proposal', same(propose(world, req, trusted), result))
    check('retry_old_request_after_application_refused', propose(result['proposed_world'], req, trusted)['reason'] == 'stale_world')
    # Request, owner, memory and state changes never leave a partial proposal.
    def adverse(name, mutate, rebind=False, status=None):
        w, q = deepcopy(world), deepcopy(req); mutate(w, q)
        if rebind: q['world_sha256'] = digest(w)
        prior = canonical(w); verdict = propose(w, q, trusted)
        witnesses[name] = {'status': verdict['status'], 'reason': verdict.get('reason')}
        check(name, verdict['status'] != 'proposed' and verdict['proposed_world'] is None
            and verdict['journal'] is None and same(verdict['world'], w) and canonical(w) == prior
            and (status is None or verdict['status'] == status))
    adverse('wrong_method', lambda w,q:q.__setitem__('method_sha256','f'*64))
    adverse('wrong_source_state', lambda w,q:q['source_state_ref'].__setitem__('digest','f'*64))
    adverse('wrong_context', lambda w,q:q['context_ref'].__setitem__('digest','f'*64))
    adverse('wrong_view', lambda w,q:q['view_ref'].__setitem__('digest','f'*64))
    adverse('request_unknown_field', lambda w,q:q.__setitem__('module_path','untrusted.py'))
    adverse('posting_module_refused', lambda w,q:q.__setitem__('posts',True))
    adverse('report_operation_not_posting', lambda w,q:q.__setitem__('operation','report'))
    adverse('changed_account_map', lambda w,q:q['account_map'].__setitem__('cash','capital'))
    adverse('changed_event_date', lambda w,q:q['event'].__setitem__('event_date','2024-07-01'))
    adverse('changed_cash_fact', lambda w,q:q['event']['parameters']['refund_cash'].__setitem__('n','41'))
    adverse('missing_finding', lambda w,q:q['findings'].__setitem__('all_rights_closed',None), status='unresolved')
    adverse('false_finding', lambda w,q:q['findings'].__setitem__('handling_is_selling_cost',False), status='unsupported')
    adverse('integer_not_boolean_finding', lambda w,q:q['findings'].__setitem__('all_rights_closed',1))
    adverse('renamed_owner', lambda w,q:w['books'][key]['owner'].__setitem__('entity_id','Northstar'), True)
    adverse('wrong_book', lambda w,q:w['books'][key]['owner'].__setitem__('book_id','Group'), True)
    adverse('wrong_branch', lambda w,q:w['books'][key]['owner'].__setitem__('branch_key','stress'), True)
    adverse('changed_shared_cash', lambda w,q:w['books'][key]['balances'].__setitem__('cash','200'), True)
    adverse('missing_memory', lambda w,q:w['books'][key].pop('component'), True)
    adverse('changed_memory', lambda w,q:w['books'][key]['component']['value'].__setitem__('settled',True), True)
    adverse('extra_account', lambda w,q:w['books'][key]['balances'].__setitem__('hidden_cash','1'), True)
    adverse('extra_state_field', lambda w,q:w['books'][key].__setitem__('hidden_state',1), True)
    adverse('changed_prior_accumulator', lambda w,q:w['books'][key]['accumulators']['cash_payments']['operating'].__setitem__('n','1'), True)
    adverse('duplicate_owner_wallet', lambda w,q:w['books'].__setitem__('second-wallet',deepcopy(w['books'][key])), True)
    altered = dict(trusted)
    def wrong_step(state,event,checker):
        value = trusted['step'](state,event,checker); value['balances']['cash'] = '53'; return value
    altered['step'] = wrong_step
    check('changed_method_result_rejected', propose(world,req,altered)['reason'] == 'method_result_mismatch')
    # The reused projection independently refuses unmapped nonzero balances.
    source = deepcopy(trusted['source_packet']); state = source['record_registry'][retained['source_state_ref']['digest']]['body']
    unmapped = next(k for k in state['balances'] if k not in trusted['account_map'])
    state['balances'][unmapped] = {'n':'1','d':'1'}
    try:
        trusted['module'].projection(source,retained['source_state_ref'],'return',need); refused = False
    except Exception as exc:
        refused = getattr(exc,'reason',None) == 'migration_unmapped_balance'
    check('unmapped_nonzero_source_refused', refused)
    native_path = ROOT/'data/accounting-master/company-family-20261023/fixture.json'
    native = json.loads(native_path.read_text())['members'][0]['path']
    capability = native_capabilities(native, projected)
    check('northstar_capability_gap_explicit', capability['status'] == 'unsupported' and len(capability['missing_capabilities']) == 7 and capability['invoked'] is False)
    check('native_owner_not_renamed', capability['owner_conversion_authorized'] is False and capability['context']['entity'] == 'Northstar')
    return {'passed':all(x['passed'] for x in out),'checks':out,'adverse':witnesses,
            'capability_gap':capability}, {'world':world,'request':req,'result':result,'descriptor':trusted['descriptor']}


def main():
    mode = sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode != '--record' or not (HERE/'manifest.json').exists(), 'record already exists'
    timer=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    trusted=context(); baseline=dict(trusted['locked'])
    for name in ['data/accounting-master/company-family-20261023/fixture.json',
                 'data/accounting-master/company-operations-20261023/operations.py',
                 'data/accounting-master/company-operations-20261023/reporting.py',
                 'data/accounting-master/company-operation-path-20261023/composition.py']:
        baseline[name]=filehash(ROOT/name)
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in manifest[group].items(): assert filehash(ROOT/name)==h,name
    result,example=checks(trusted)
    for name,h in baseline.items(): assert filehash(ROOT/name)==h,name
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
        'failed':[x['name'] for x in result['checks'] if not x['passed']],
        'protected_files':len(baseline),'wall_seconds':time.monotonic()-timer}
    if not result['passed']: dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        dump(HERE/'checks.json',result); dump(HERE/'example.json',example); dump(HERE/'source-lock.json',baseline)
        outputs={str(p.relative_to(ROOT)):filehash(p) for p in [HERE/'checks.json',HERE/'example.json',HERE/'source-lock.json']}
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; exact Fraction arithmetic',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1 before imports',
            'random_seeds':'N/A: deterministic','inputs':baseline,'outputs':outputs,
            'implementation':{str(p.relative_to(ROOT)):filehash(p) for p in HERE.glob('*.py')},
            'plan':'docs/plans/accounting-company-module-boundary-20261023.md',
            'result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert same(result,json.loads((HERE/'checks.json').read_text())), 'check replay mismatch'
        assert same(example,json.loads((HERE/'example.json').read_text())), 'example replay mismatch'
    print(json.dumps(observation)); return 0 if result['passed'] else 1


if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc:
        name=HERE/('failure-'+str(time.time_ns())+'.txt'); name.write_text(traceback.format_exc())
        print(json.dumps({'status':'failed','error':type(exc).__name__+': '+str(exc)[:400],
                         'diagnostic':str(name.relative_to(ROOT))})); sys.exit(1)
