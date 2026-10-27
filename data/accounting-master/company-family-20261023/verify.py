"""Deterministic family conformance; record once, replay read-only thereafter."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
import platform
import subprocess
import sys
import time
from family import HERE,PROFILE,FLAGS,common,digest,execute,joint_report,lower,render,schema,validate,verify

ROOT=HERE.parents[2]; REL=HERE.relative_to(ROOT).as_posix()
EXCHANGE=HERE.parent/'company-path-exchanges-20261023'
sys.path.insert(0,str(EXCHANGE))
from support import context

def protected():
    base=json.loads((HERE.parent/'company-policy-information-20261023/baseline.json').read_text())
    for folder in ['company-policy-information-20261023','company-text-20261023','language-scope-review-20261023']:
        for p in (HERE.parent/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and 'control-before' not in p.parts:
                base[str(p.relative_to(ROOT))]=sha256(p.read_bytes()).hexdigest()
    return base

def fixtures():
    previous,engine,_=context()
    packet=json.loads((EXCHANGE/'packet.json').read_text()); raw=previous.load_blob_files(packet)
    records=packet['record_registry']; root=records[packet['root_ref']['digest']]['body']
    export=records[root['baseline_export_ref']['digest']]['body']; source=raw[export['source_bundle_blob']['digest']]
    cases={}
    for ref in root['path_refs']:
        item=records[ref['digest']]['body']
        cases[item['name']]={'path':json.loads(raw[item['path_blob']['digest']]),'result':json.loads(raw[item['result_blob']['digest']])}
    policy=json.loads((HERE.parent/'company-policy-20261023/checks.json').read_text())
    cases['explicit_collection_policy']={'path':policy['materialization']['path'],'result':policy['generated_result']}
    family={'profile':PROFILE,'name':'Northstar authored scenarios','meaning':'authored_exogenous_scenarios',
            'weighting':'unweighted','coverage':'authored_members_only','common':common(cases['baseline']['path']),
            'members':[{'id':name,'path':case['path']} for name,case in cases.items()]}
    return family,cases,source,engine

def conformance(smoke=False):
    body,cases,source,engine=fixtures(); original=deepcopy(body); checks=[]; adverse={}
    def check(name,passed): checks.append({'name':name,'passed':bool(passed)})
    text=render(body); restored=lower(text)
    check('text_typed_content_identity',digest(restored)==digest(body))
    check('canonical_text_idempotence',render(restored)==text)
    run=execute(restored,source,engine)
    check('all_six_members_retained',len(run['members'])==len(cases)==6)
    for member in run['members']:
        case=cases[member['id']]
        check('exact_standalone_result:'+member['id'],digest(member['result'])==digest(case['result']))
        check('exact_path_identity:'+member['id'],member['path_sha256']==digest(case['path']))
        check('all_report_bytes:'+member['id'],digest([y['report'] for y in member['result']['years']])==digest([y['report'] for y in case['result']['years']]))
    check('input_not_mutated',digest(body)==digest(original))
    check('partial_family_not_all_complete',run['status']=='evaluated_with_incomplete_members')
    check('no_probability_or_historical_admission',all(run[k] is False for k in FLAGS))
    if smoke: return {'passed':all(x['passed'] for x in checks),'checks':checks},body,text,run
    def reject(name,candidate):
        try: validate(candidate); outcome={'rejected':False}
        except Exception as exc: outcome={'rejected':True,'error':type(exc).__name__+':'+str(exc).splitlines()[0][:200]}
        adverse[name]=outcome; check(name,outcome['rejected'])
    def mutation(name,edit):
        p=deepcopy(body); edit(p); reject(name,p)
    mutation('duplicate_member_identity',lambda p:p['members'].append(deepcopy(p['members'][0])))
    mutation('probability_field_refused',lambda p:p['members'][0].update(weight='1/6'))
    mutation('weighted_family_refused',lambda p:p.update(weighting='equal_weights'))
    mutation('historical_family_claim_refused',lambda p:p.update(meaning='feasible_histories'))
    mutation('exhaustive_coverage_claim_refused',lambda p:p.update(coverage='all_possible_futures'))
    for key in ['source_sha256','opening_sha256']:
        mutation('changed_common_'+key,lambda p,k=key:p['common'].__setitem__(k,'f'*64))
    for key in ['entity','book','currency']:
        mutation('different_'+key,lambda p,k=key:p['members'][1]['path']['initial_year']['context'].__setitem__(k,'Different'))
    mutation('different_opening_record',lambda p:p['members'][1]['path']['initial_year'].__setitem__('opening_digest','f'*64))
    mutation('different_source_path',lambda p:p['members'][1]['path']['initial_year']['source'].__setitem__('path','other'))
    mutation('different_claim_memory',lambda p:p['members'][1]['path']['initial_year']['opening_claims'][0].__setitem__('amount','1/1'))
    mutation('different_asset_memory',lambda p:p['members'][1]['path']['initial_year']['assets'][0].__setitem__('accumulated','1/1'))
    mutation('different_opening_facility',lambda p:p['members'][1]['path']['initial_year']['facility'].__setitem__('drawn','1/1'))
    mutation('different_debt_principal',lambda p:p['members'][1]['path']['initial_year']['debt'].__setitem__('principal','1/1'))
    mutation('different_period',lambda p:p['members'][1]['path']['continuations'][-1]['period'].__setitem__('end_exclusive','2029-01-01'))
    mutation('noncanonical_rational',lambda p:p['members'][0]['path']['initial_year']['operations'][0]['payload'].__setitem__('units','2/2'))
    mutation('nonconsecutive_common_horizon',lambda p:p['common']['periods'][1].__setitem__('start','2026-02-01'))
    mutation('nonpositive_common_period',lambda p:p['common']['periods'][0].__setitem__('end_exclusive','2025-01-01'))
    for name,bad in {
        'missing_end_family':text.rsplit('end_family;',1)[0],
        'after_end':text+'period 2030-01-01 2031-01-01;\n',
        'missing_end_member':text.replace('end_member;','',1),
        'include_forbidden':text.replace('end_family;','include secret;\nend_family;'),
        'bad_profile':text.replace(PROFILE,'Other/1',1),
        'missing_semicolon':text.replace(';','',1),
        'late_period':text.replace('end_family;','period 2028-01-01 2029-01-01;\nend_family;')}.items():
        try: lower(bad); outcome=False
        except Exception: outcome=True
        check(name,outcome)
    quoted=deepcopy(body); quoted['name']='Company '+chr(34)+'quote'+chr(34)+'; # '+chr(39)
    quoted['members'][0]['id']='member with spaces; # '+chr(39)
    check('quoted_identity_roundtrip',digest(lower(render(quoted)))==digest(quoted))
    check('blank_lines',digest(lower('\n'+text+'\n'))==digest(body))
    unicode_body=deepcopy(body); unicode_body['members']=unicode_body['members'][:1]
    unicode_body['name']='北星'; unicode_body['members'][0]['id']='情景'
    unicode_body['members'][0]['path']['name']='Northstar 公司'
    check('unicode_text_roundtrip',digest(lower(render(unicode_body)))==digest(unicode_body))
    unicode_run=execute(unicode_body,source,engine); unicode_member=unicode_run['members'][0]
    check('unicode_path_identity_matches_engine',unicode_member['path_sha256']==unicode_member['result']['branch_sha256'])
    check('unicode_result_identity_matches_engine',unicode_member['result_sha256']==engine.digest(unicode_member['result']))
    check('unicode_trusted_replay',verify(unicode_body,source,unicode_run,engine))
    check('source_bytes_refused',execute(body,source+b' ',engine)['status']=='invalid')
    check('trusted_replay',verify(body,source,run,engine))
    forged=deepcopy(run); target=forged['members'][0]
    target['result']['years'][0]['report']['lines']['cash']['value']='0/1'
    target['result_sha256']=digest(target['result'])
    check('rehashed_false_report_refused',not verify(body,source,forged,engine))
    missing=deepcopy(run); missing['members'].pop()
    check('dropped_member_refused',not verify(body,source,missing,engine))
    numeric_flags=deepcopy(run); numeric_flags['probability_admitted']=0
    check('false_is_not_numeric_zero',not verify(body,source,numeric_flags,engine))
    views={}
    for period in body['common']['periods']:
        at=period['start']; view=joint_report(body,source,run,at,engine); views[at]=view
        check('all_joint_members:'+at,len(view['members'])==6)
        check('joint_report_no_admission:'+at,all(view[k] is False for k in FLAGS))
        for m in view['members']:
            years=cases[m['id']]['result']['years']; matches=[y for y in years if y['period']['start']==at]
            if matches: check('full_joint_vector:'+at+':'+m['id'],digest(m['report'])==digest(matches[0]['report']))
            else: check('unexecuted_member_retained:'+at+':'+m['id'],m['report'] is None and m['status']=='unresolved')
    partial=next(m for m in views['2026-01-01']['members'] if m['id']=='unknown_middle_payroll')
    check('partial_cash_unknown_not_zero',partial['report']['lines']['cash']['status']=='unresolved' and 'value' not in partial['report']['lines']['cash'])
    check('partial_opening_known',partial['report']['lines']['opening_cash']['status']=='known')
    check('outside_horizon_refused',joint_report(body,source,run,'2030-01-01',engine)['status']=='invalid')
    empty=deepcopy(body); empty['members']=[]; empty_run=execute(empty,source,engine)
    check('empty_text_roundtrip',digest(lower(render(empty)))==digest(empty))
    check('empty_is_authored_selection_not_infeasibility',empty_run['status']=='empty_authored_family' and empty_run['members']==[])
    check('empty_joint_report',joint_report(empty,source,empty_run,'2025-01-01',engine)['members']==[])
    duplicate=deepcopy(body); duplicate['members']=[deepcopy(body['members'][0]),deepcopy(body['members'][0])]; duplicate['members'][1]['id']='same_path_different_label'
    duplicate_run=execute(duplicate,source,engine)
    check('equal_paths_remain_named_members',len(duplicate_run['members'])==2 and len({x['path_sha256'] for x in duplicate_run['members']})==1)
    check('equal_paths_do_not_imply_weights',duplicate_run['weighting']=='unweighted' and duplicate_run['probability_admitted'] is False)
    invalid_member=deepcopy(body); first=invalid_member['members'][0]['path']['initial_year']
    first['operations'][0]['payload']['units']='-1/1'
    invalid_run=execute(invalid_member,source,engine)
    check('member_accounting_failure_retained',len(invalid_run['members'])==6 and invalid_run['members'][0]['status']!='complete_conditional')
    check('failed_member_does_not_change_sibling',digest(invalid_run['members'][1]['result'])==digest(run['members'][1]['result']))
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'adverse':adverse,'joint_reports':views,'empty_result':empty_run,'duplicate_path_result':duplicate_run,'invalid_member_result':invalid_run},body,text,run

def main():
    flags=set(sys.argv[1:]); assert flags <= {'--record','--smoke'} and len(flags)<=1
    record='--record' in flags; smoke='--smoke' in flags
    assert not record or not (HERE/'manifest.json').exists(),'one-time recording already exists'
    baseline=json.loads((HERE/'baseline.json').read_text()) if (HERE/'baseline.json').exists() else protected()
    for name,h in baseline.items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    start=time.perf_counter(); started=datetime.now(timezone.utc).isoformat()
    evidence,body,text,run=conformance(smoke)
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    for name,h in baseline.items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    if failed:
        dest=HERE/('failure-'+datetime.now(timezone.utc).strftime('%H%M%S')); dest.mkdir()
        for p in HERE.glob('*.py'): (dest/p.name).write_bytes(p.read_bytes())
        (dest/'failure.json').write_text(json.dumps(evidence,indent=2)+'\n')
    if record and not failed:
        artifacts={'checks.json':evidence,'fixture.json':body,'result.json':run,'schema.json':schema(),'baseline.json':baseline}
        for name,value in artifacts.items(): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
        (HERE/'example.accdsl').write_text(text)
        manifest={'started_utc':started,'wall_seconds':time.perf_counter()-start,'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 python3 '+REL+'/verify.py --record','environment':'Python '+platform.python_version()+'; jsonschema; shlex; protected local engine','cpu_gpu':'CPU only; GPU intentionally hidden by CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),'random_seeds':'N/A: deterministic','data_version':baseline,'plan':'docs/plans/accounting-company-family-20261023.md','result':REL+'/result.md','files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif not smoke and not failed and (HERE/'manifest.json').exists():
        for name,value in [('checks.json',evidence),('fixture.json',body),('result.json',run),('schema.json',schema())]:
            assert digest(json.loads((HERE/name).read_text()))==digest(value),name
        assert (HERE/'example.accdsl').read_text()==text
        for name,h in json.loads((HERE/'manifest.json').read_text())['files'].items(): assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'protected_files':len(baseline),'recorded':record and not failed,'smoke':smoke,'wall_seconds':round(time.perf_counter()-start,3)}))
    return bool(failed)
if __name__=='__main__': raise SystemExit(main())
