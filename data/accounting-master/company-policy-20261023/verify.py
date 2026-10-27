"""Matched fixed-versus-policy settlement checks with trusted local replay."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import time
from jsonschema import Draft202012Validator

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
EXCHANGE=HERE.parent/'company-path-exchanges-20261023'
sys.path.insert(0,str(EXCHANGE));sys.path.insert(0,str(HERE))
from exchanges import load
from support import context
import policy as method


def conformance():
    previous,engine,validate=context();packet=json.loads((EXCHANGE/'packet.json').read_text())
    raw=previous.load_blob_files(packet);records=packet['record_registry'];root=records[packet['root_ref']['digest']]['body']
    paths={records[r['digest']]['body']['name']:records[r['digest']]['body'] for r in root['path_refs']}
    fixed_body=paths['second_year_price_revision'];fixed=json.loads(raw[fixed_body['path_blob']['digest']])
    defs=[fixed['initial_year']]+fixed['continuations'];year=defs[1]
    policy={'profile':'SettlementPolicyDraft/1','policy_id':'receivable-90pct-example',
        'parent_path_sha256':method.digest(fixed),'year_index':1,
        'delivery_operations':['delivery-1-a','delivery-1-b'],
        'collection_operations':['collection-1-a','collection-1-b'],
        'claim_ids':['sales-ar-2026-a','sales-ar-2026-b'],'fraction':'9/10',
        'installment_shares':['1/2','1/2'],'rounding':'exact_rational_no_rounding',
        'scope':'named_delivery_claims_only','real_behavior_evidence':False}
    protected_path=deepcopy(fixed);protected_policy=deepcopy(policy)
    generated=method.generate(fixed,policy);assert generated['status']=='materialized_conditional_path'
    candidate=generated['path']
    export=records[root['baseline_export_ref']['digest']]['body']
    source=raw[export['source_bundle_blob']['digest']]
    # Read-only: use the exact saved source and locally locked interpreter.
    fixed_run=engine.wire(engine.execute(fixed,source));candidate_run=engine.wire(engine.execute(candidate,source))
    checks=[];witnesses={}
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    assessment=method.validate_policy(fixed,policy)
    check('policy_scope_valid',assessment['status']=='validated_scoped_policy')
    check('policy_evidence_only_illustrative',assessment['real_behavior_evidence'] is False)
    check('parent_result_matches_fixed_exchange',method.digest(fixed)==fixed_body['branch_sha256'])
    check('fixed_input_bytewise_unchanged',method.digest(fixed)==generated['parent_path_sha256'])
    check('generator_does_not_mutate_inputs',fixed==protected_path and policy==protected_policy)
    check('fixed_replay_matches_saved_result',fixed_run==json.loads(raw[fixed_body['result_blob']['digest']]))
    check('both_second_year_paths_complete',fixed_run['status']==candidate_run['status']=='complete_conditional')
    check('fixed_semantics_unchanged',engine.wire(engine.execute(fixed,source))==fixed_run)
    check('generated_child_replays',engine.verify_chain(candidate,candidate_run))
    check('baseline_complete_exchange_replays',validate(packet,raw)['status']=='validated_synthetic_exchange')
    changes=[]
    fixed_collections=[o for o in year['operations'] if o['kind']=='collection']
    generated_year=candidate['continuations'][0]
    generated_collections=[o for o in generated_year['operations'] if o['kind']=='collection']
    for x,y in zip(fixed_collections,generated_collections):
        for a,b in zip(x['payload']['allocations'],y['payload']['allocations']):
            if a!=b:changes.append((x['id'],a['claim_id'],a['amount'],b['amount']))
    check('exactly_four_allocation_values_in_two_operations_change',changes==[
        ('collection-1-a','sales-ar-2026-a','396/5','432/5'),
        ('collection-1-a','sales-ar-2026-b','396/5','432/5'),
        ('collection-1-b','sales-ar-2026-a','396/5','432/5'),
        ('collection-1-b','sales-ar-2026-b','396/5','432/5')])
    changed=[]
    for x,y in zip(year['operations'],candidate['continuations'][0]['operations']):
        if x!=y:changed.append((x['id'],x['kind']))
    check('operation_diff_is_collection_only',changed==[('collection-1-a','collection'),('collection-1-b','collection')])
    restored=deepcopy(candidate)
    for old,new in zip(fixed['continuations'][0]['operations'],restored['continuations'][0]['operations']):
        if old['id'] in policy['collection_operations']:
            for a,b in zip(old['payload']['allocations'],new['payload']['allocations']):
                if a['claim_id'] in policy['claim_ids']:b['amount']=a['amount']
    check('entire_non_target_path_preserved',restored==fixed)
    check('earlier_year_result_preserved',fixed_run['years'][0]==candidate_run['years'][0])
    check('third_year_inputs_fixed',candidate['continuations'][1]==fixed['continuations'][1])
    fy=fixed_run['years'][1];cy=candidate_run['years'][1]
    check('revenue_equal',fy['report']['lines']['revenue']==cy['report']['lines']['revenue'])
    check('profit_equal',fy['report']['lines']['profit']==cy['report']['lines']['profit'])
    check('cost_equal',fy['report']['lines']['cost_of_sales']==cy['report']['lines']['cost_of_sales'])
    fixed_cash=Q(fy['report']['lines']['cash']['value']);new_cash=Q(cy['report']['lines']['cash']['value'])
    fixed_ar=Q(fy['report']['lines']['receivables']['value']);new_ar=Q(cy['report']['lines']['receivables']['value'])
    check('cash_receivable_conservation',(new_cash-fixed_cash)==(fixed_ar-new_ar)==Q(144,5))
    check('new_invoice_less_collectible_equals_ar',Q(384)-2*(Q(192)*Q(9,10))==Q(192,5))
    check('actual_generated_receivables_match_independent_amount',new_ar==Q(192,5))
    for cid in policy['claim_ids']:
        claim=cy['closing_memory']['claims'][cid]
        check('claim_conservation:'+cid,Q(claim['recognised'])==Q(claim['settled'])+Q(claim['outstanding'])==192)
        check('claim_policy_amount:'+cid,Q(claim['settled'])==Q(864,5) and Q(claim['outstanding'])==Q(96,5))
    expected_deltas={'cash':Q(144,5),'receivables':-Q(144,5),'operating_cash':Q(144,5),'cash_change':Q(144,5)}
    for line,fixed_value in fy['report']['lines'].items():
        actual=Q(cy['report']['lines'][line]['value'])-Q(fixed_value['value'])
        check('all_annual_report_deltas:'+line,actual==expected_deltas.get(line,Q(0)))
    check('generated_state_balances',sum(Q(v) for v in cy['run']['closing_balances'].values())==0)
    check('following_year_cash_difference_carried',Q(candidate_run['years'][2]['report']['lines']['cash']['value'])-Q(fixed_run['years'][2]['report']['lines']['cash']['value'])==Q(144,5))
    check('following_year_receivable_difference_carried',Q(candidate_run['years'][2]['report']['lines']['receivables']['value'])-Q(fixed_run['years'][2]['report']['lines']['receivables']['value'])==-Q(144,5))
    changed_candidate=method.generate(fixed,policy)
    check('deterministic_materialization',changed_candidate['path']==candidate)
    check('unadmitted_policy_timing',generated['information_admission']['status']=='unresolved')
    check('no_predictive_claim',generated['forecast_admission'] is False and generated['real_behavior_evidence'] is False)
    for name,edit,reason in [
        ('changed_parent',lambda p:p.update(parent_path_sha256='0'*64),'parent_path_identity'),
        ('duplicate_target_claim',lambda p:p.update(claim_ids=p['claim_ids']+[p['claim_ids'][0]]),'duplicate_claim_target'),
        ('wrong_delivery',lambda p:p.update(delivery_operations=['collection-1-a']),'delivery_binding'),
        ('over_one_fraction',lambda p:p.update(fraction='11/10'),'fraction_domain'),
        ('installment_shares_not_sum_one',lambda p:p.update(installment_shares=['1/3','1/3']),'fraction_domain'),
        ('rounding_not_exact',lambda p:p.update(rounding='nearest_cent'),'policy_schema'),
        ('policy_claim_mismatch',lambda p:p.update(claim_ids=['sales-ar-2026-a']),'claim_binding')]:
        bad=deepcopy(policy);edit(bad);result=method.generate(fixed,bad);witnesses[name]=result
        check(name+':refused',result.get('status')=='invalid' and result.get('reason')==reason)
    bad=deepcopy(policy);bad.update(collection_operations=['delivery-1-a','collection-1-b'])
    value=method.generate(fixed,bad)
    check('wrong_collection_operation_refused',value.get('status')=='invalid')
    changed_path=deepcopy(fixed);changed_year=changed_path['continuations'][0]
    collection=next(o for o in changed_year['operations'] if o['id']=='collection-1-a')
    delivery=next(o for o in changed_year['operations'] if o['id']=='delivery-1-a')
    changed_year['operations'].remove(collection);changed_year['operations'].insert(changed_year['operations'].index(delivery),collection)
    bad=deepcopy(policy);bad['parent_path_sha256']=method.digest(changed_path)
    value=method.validate_policy(changed_path,bad);witnesses['collection_before_delivery']=value
    check('unsorted_collection_before_delivery_refused',value.get('reason')=='operation_chronology')
    collection['at']=delivery['at']
    bad['parent_path_sha256']=method.digest(changed_path)
    value=method.validate_policy(changed_path,bad)
    check('same_instant_collection_before_delivery_refused',value.get('reason')=='collection_before_delivery')
    # A recomputed path identity cannot make an excessive settlement executable.
    forged=deepcopy(candidate);next(o for o in forged['continuations'][0]['operations'] if o['id']=='collection-1-a')['payload']['allocations'][-2]['amount']='999/1'
    forged_run=engine.wire(engine.execute(forged,source))
    witnesses['forged_allocation']=forged_run
    stopped=forged_run['years'][1]['run']
    check('forged_over_settlement_rejected',forged_run['status']=='partial' and stopped['status']=='invalid' and stopped['reason']=='over_settlement')
    check('materialization_trace_verifies',method.verify_materialization(fixed,policy,generated)['status']=='verified_materialization')
    tampered=deepcopy(generated)
    next(o for o in tampered['path']['continuations'][0]['operations'] if o['id']=='collection-1-a')['payload']['allocations'][-1]['amount']='85/1'
    tampered['child_path_sha256']=method.digest(tampered['path'])
    check('rehashed_non_policy_amount_rejected',method.verify_materialization(fixed,policy,tampered).get('reason')=='policy_materialization_mismatch')
    tampered=deepcopy(generated);tampered['allocation_trace'][0]['prior_amount']='0/1'
    check('changed_trace_refused',method.verify_materialization(fixed,policy,tampered).get('reason')=='policy_materialization_mismatch')
    for name,edit,status,reason in [
        ('unknown_fraction',lambda p:p.update(fraction='unknown'),'unresolved','policy_fraction_or_share_unknown'),
        ('unknown_share',lambda p:p.update(installment_shares=['unknown','1/2']),'unresolved','policy_fraction_or_share_unknown'),
        ('duplicate_delivery',lambda p:p['delivery_operations'].append('delivery-1-a'),'invalid','duplicate_delivery'),
        ('duplicate_collection',lambda p:p.update(collection_operations=['collection-1-a','collection-1-a']),'invalid','duplicate_collection'),
        ('negative_fraction',lambda p:p.update(fraction='-1/10'),'invalid','fraction_domain'),
        ('negative_share',lambda p:p.update(installment_shares=['-1/2','3/2']),'invalid','fraction_domain'),
        ('invalid_rational_lexical',lambda p:p.update(fraction='0.9'),'invalid','policy_schema'),
        ('zero_denominator',lambda p:p.update(fraction='1/0'),'invalid','policy_schema'),
        ('noncanonical_fraction',lambda p:p.update(fraction='18/20'),'invalid','rational'),
        ('unknown_field',lambda p:p.update(executable_code='raise RuntimeError'),'invalid','policy_schema'),
        ('year_out_of_range',lambda p:p.update(year_index=4),'invalid','year_index')]:
        p=deepcopy(policy);edit(p);value=method.generate(fixed,p);witnesses[name]=value
        check(name,value.get('status')==status and value.get('reason')==reason)
    def change_path(name,edit,status,reason):
        path=deepcopy(fixed);edit(path['continuations'][0]);p=deepcopy(policy);p['parent_path_sha256']=method.digest(path)
        value=method.generate(path,p);witnesses[name]=value
        check(name,value.get('status')==status and value.get('reason')==reason)
    delivery=lambda y:next(o for o in y['operations'] if o['id']=='delivery-1-a')
    collection=lambda y:next(o for o in y['operations'] if o['id']=='collection-1-a')
    change_path('unknown_invoice',lambda y:delivery(y)['payload'].update(unit_price='unknown'),'unresolved','delivery_inputs_unknown')
    change_path('unknown_transfer',lambda y:delivery(y)['payload'].update(control_transferred='unknown'),'unresolved','delivery_inputs_unknown')
    change_path('false_transfer',lambda y:delivery(y)['payload'].update(control_transferred=False),'unsupported','control_transfer_not_established')
    change_path('negative_invoice',lambda y:delivery(y)['payload'].update(units='-1/1'),'invalid','negative_invoice_input')
    change_path('noncanonical_invoice',lambda y:delivery(y)['payload'].update(units='32/2'),'invalid','invoice_rational')
    change_path('duplicate_operation',lambda y:y['operations'].append(deepcopy(delivery(y))),'invalid','duplicate_operation_id')
    change_path('duplicate_issued_claim',lambda y:delivery(y)['payload'].update(claim_id='sales-ar-2026-b'),'invalid','duplicate_issued_claim')
    change_path('unknown_schedule',lambda y:delivery(y).update(at='unknown'),'unresolved','operation_instants_unknown')
    change_path('missing_target_allocation',lambda y:collection(y)['payload']['allocations'].pop(),'invalid','target_allocation_coverage')
    change_path('duplicate_allocation',lambda y:collection(y)['payload']['allocations'].append(deepcopy(collection(y)['payload']['allocations'][-1])),'invalid','duplicate_allocation')
    def extra_collection(y):
        op=deepcopy(collection(y));op['id']='collection-extra';y['operations'].insert(y['operations'].index(collection(y)),op)
    change_path('extra_collection_outside_policy',extra_collection,'unsupported','additional_target_claim_settlement')
    for fraction in ['0/1','1/1']:
        p=deepcopy(policy);p['fraction']=fraction;m=method.generate(fixed,p)
        check('fraction_endpoint_conserves:'+fraction,m['status']=='materialized_conditional_path' and
            all(Q(c['generated_collections'])+Q(c['uncollected'])==Q(c['invoice_amount']) for c in m['claim_totals']))
    protected=json.loads((HERE/'baseline.json').read_text()) if (HERE/'baseline.json').exists() else {}
    check('protected_files_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(x['passed'] for x in checks),'witnesses':witnesses,
        'materialization':generated,'fixed_result':fixed_run,'generated_result':candidate_run},policy


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    target=HERE/'checks.json'
    if args.record and target.exists():raise RuntimeError('Existing evidence; read-only replay')
    if args.record:
        protect={}
        for d in [EXCHANGE,EXCHANGE.parent/'company-operation-path-20261023',EXCHANGE.parent/'company-operations-20261023']:
            for f in d.iterdir():
                if f.is_file():protect[str(f.relative_to(ROOT))]=hashlib.sha256(f.read_bytes()).hexdigest()
        (HERE/'baseline.json').write_text(json.dumps(protect,indent=2)+'\n')
    started=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence,policy_data=conformance()
    if args.record:
        (HERE/'checks.json').write_text(json.dumps(evidence,indent=2)+'\n')
        (HERE/'policy.json').write_text(json.dumps(policy_data,indent=2)+'\n')
        (HERE/'schema.json').write_text(json.dumps(method.schema(),indent=2)+'\n')
        manifest={'started_utc':started,'wall_seconds':time.perf_counter()-clock,
          'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-policy-20261023/verify.py --record',
          'environment':'system Python '+platform.python_version()+'; jsonschema; trusted local replay',
          'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
          'data_version':json.loads((HERE/'baseline.json').read_text()),
          'random_seeds':'N/A: deterministic','plan':'docs/plans/accounting-company-policy-20261023.md',
          'result':'data/accounting-master/company-policy-20261023/result.md',
          'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file() and p.name!='manifest.json'}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists():
        if evidence!=json.loads(target.read_text()):raise AssertionError('Replay mismatch')
        if policy_data!=json.loads((HERE/'policy.json').read_text()):raise AssertionError('Policy mismatch')
        if method.schema()!=json.loads((HERE/'schema.json').read_text()):raise AssertionError('Schema mismatch')
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
