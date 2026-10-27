"""Joined three-year conformance; read-only replay unless --record."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from composition import execute, schema, wire, digest, revise, verify_chain, report_view

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def conformance():
    path=json.loads((HERE/'example.json').read_text())
    source=(ROOT/path['initial_year']['source']['path']).read_bytes()
    original=deepcopy(path);checks=[];witnesses={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    def case(name,change):
        p=deepcopy(path);change(p);before=deepcopy(p);r=execute(p,source)
        check(name+':pure',p==before);witnesses[name]={'path':p,'result':r};return p,r
    reference=json.loads((HERE.parent/'company-path-20261023'/'checks.json').read_text())
    expected=reference['witnesses']['three_year_path']['result']
    run=execute(path,source)
    check('published_schema',schema()==json.loads((HERE/'schema.json').read_text()))
    check('three_years_complete',run['status']=='complete_conditional' and len(run['years'])==3)
    check('chain_identity_valid',verify_chain(path,run))
    check('pure_initial_input',path==original)
    for i,(actual,old) in enumerate(zip(run['years'],expected['years'])):
        a=actual['run'];b=old['annual_run'];name='year_'+str(i)
        check(name+':21_operations',len(a['journals'])==21)
        for k in ['closing_balances','inventory_units','income','statements','indirect_cfo','facility_drawn']:
            check(name+':'+k,wire(a[k])==b[k])
        for k,line in old['annual_report']['lines'].items():
            check(name+':report_'+k,wire(actual['report']['lines'][k])==line)
        check(name+':gross_cash',wire(actual['report']['gross_cash'])==old['annual_report']['gross_cash'])
        check(name+':every_report_bridge',all(actual['report']['reconciliation'].values()))
        check(name+':claim_totals',all(sum(c[k] for c in actual['closing_memory']['claims'].values() if c['ledger']==ledger)==sum(Q(c[k]) for c in old['closing_memory']['claims'].values() if c['ledger']==ledger) for ledger in ['receivable','payable'] for k in ['recognised','settled','outstanding']))
        check(name+':asset_totals',all(sum(Q(a[k]) for a in actual['closing_memory']['assets'])==sum(Q(a[k]) for a in old['closing_memory']['assets']) for k in ['cost','accumulated']))
        check(name+':per_operation_source_links',all(j['method'] and j['input_paths'] for j in a['journals']))
        if i:check(name+':conditional_origin',actual['origin']['kind']=='conditional_predecessor' and not actual['origin']['historical_admission'])
    claims=run['years'][2]['closing_memory']['claims']
    check('all_split_claims_survive_three_years',len(claims)==14 and all(c['recognised']-c['settled']==c['outstanding'] for c in claims.values()))
    check('first_year_claims_fully_collected_once',claims['sales-ar-a']['recognised']==150 and claims['sales-ar-a']['settled']==150 and claims['sales-ar-a']['outstanding']==0)
    check('third_year_cash_independent',run['years'][2]['run']['statements']['cash']==Q(7390396,45625)+Q(516,5))
    replacement=deepcopy(path['continuations'][0])
    for o in replacement['operations']:
        if o['kind']=='delivery':o['payload']['unit_price']='12/1'
    changed=revise(path,source,1,replacement,'Second-year price, fixed collection allocations')
    cr=changed['result'];witnesses['second_year_price_revision']=changed
    check('later_revision_preserves_first_year',cr['years'][0]['result_sha256']==run['years'][0]['result_sha256'])
    check('later_revision_recomputes_entire_suffix',all(cr['years'][i]['result_sha256']!=run['years'][i]['result_sha256'] for i in [1,2]) and verify_chain(changed['path'],cr))
    check('fixed_receipts_price_revision_cash',all(cr['years'][i]['run']['statements']['cash']-run['years'][i]['run']['statements']['cash']==-Q(32,5) for i in [1,2]))
    check('fixed_receipts_price_revision_profit',cr['years'][1]['run']['statements']['profit']-run['years'][1]['run']['statements']['profit']==Q(128,5) and cr['years'][2]['run']['statements']['profit']==run['years'][2]['run']['statements']['profit'])
    check('uncollected_revised_claim_carries',cr['years'][2]['closing_memory']['claims']['sales-ar-2026-a']['outstanding']==16 and cr['years'][2]['closing_memory']['claims']['sales-ar-2026-b']['outstanding']==16)
    first=deepcopy(path['initial_year'])
    for o in first['operations']:
        if o['kind']=='delivery':o['payload']['unit_price']='11/1'
    revised=revise(path,source,0,first,'First-year price with fixed later allocations');rr=revised['result'];witnesses['first_year_price_revision']=revised
    check('root_revision_changes_all_years',all(a['result_sha256']!=b['result_sha256'] for a,b in zip(rr['years'],run['years'])))
    check('root_revision_uncollected_amount_survives',rr['years'][2]['closing_memory']['claims']['sales-ar-a']['outstanding']==15 and rr['years'][2]['closing_memory']['claims']['sales-ar-b']['outstanding']==15 and rr['years'][2]['run']['statements']['cash']-run['years'][2]['run']['statements']['cash']==-6)
    check('parent_unchanged_after_revisions',path==original and execute(path,source)==run)
    check('revision_not_historical_restatement',not revised['historical_restatement'])
    mixed=deepcopy(cr);mixed['years'][2]=deepcopy(run['years'][2])
    check('stale_suffix_refused',not verify_chain(changed['path'],mixed))
    check('wrong_branch_report_refused',report_view(changed['path'],run,'2026-01-01')['status']=='invalid')
    check('bound_report_period',report_view(path,run,'2027-01-01')['year_result_sha256']==run['years'][2]['result_sha256'])
    bad=deepcopy(run);bad['years'][1]['report']['lines']['cash']['value']+=1
    check('tampered_report_refused',not verify_chain(path,bad))
    bad=deepcopy(run);bad['years'].pop()
    check('truncated_complete_refused',not verify_chain(path,bad))
    def unknown_middle(p):
        next(o for o in p['continuations'][0]['operations'] if o['kind']=='payroll')['payload']['amount']='unknown'
    up,ur=case('unknown_middle_payroll',unknown_middle)
    check('unknown_middle_blocks_third',ur['status']=='partial' and len(ur['years'])==2 and len(ur['unexecuted'])==1 and ur['stopped_status']=='unresolved' and verify_chain(up,ur))
    check('middle_prefix_preserved',len(ur['years'][1]['run']['applied'])==11 and ur['years'][1]['report']['prefix_snapshot']['last_event']=='facility_repayment-1' and ur['years'][1]['report']['lines']['profit']['status']=='unresolved')
    check('unexecuted_third_report_unresolved',report_view(up,ur,'2027-01-01')['status']=='unresolved')
    def early_payment(p):
        events=p['continuations'][0]['operations']
        for o in events:
            if o['kind']=='collection':o['at']='2026-01-05T09:00:00Z'
        events.sort(key=lambda o:o['at'])
    fp,fr=case('middle_supplier_failure',early_payment)
    check('failed_middle_preserves_complete_first',fr['status']=='partial' and fr['years'][0]['result_sha256']==run['years'][0]['result_sha256'] and fr['stopped_status']=='funding_failure')
    check('first_split_supplier_payment_refused',fr['years'][1]['run']['event']=='supplier_payment-1-a' and all(c['settled']==0 for c in fr['years'][1]['run']['claims'].values()) and len(fr['unexecuted'])==1)
    def missing_claim(p):
        o=next(o for o in p['continuations'][0]['operations'] if o['kind']=='collection');o['payload']['allocations'][0]['claim_id']='unrecognised'
    _,bad=case('missing_carried_claim_reference',missing_claim)
    check('claim_name_not_recovered_from_totals',bad['status']=='partial' and bad['stopped_status']=='invalid' and bad['years'][1]['run']['reason']=='unrecognised_claim')
    def reuse(p):
        next(o for o in p['continuations'][1]['operations'] if o['kind']=='delivery')['payload']['claim_id']='sales-ar-a'
    _,bad=case('settled_claim_identity_reuse',reuse)
    check('zero_balance_claim_id_cannot_recur',bad['status']=='partial' and bad['stopped_status']=='invalid' and bad['years'][2]['run']['reason']=='duplicate_claim')
    _,bad=case('period_gap',lambda p:p['continuations'][0]['period'].update(start='2026-02-01'))
    check('period_gap_invalid',bad['status']=='invalid' and bad['reason']=='nonconsecutive_periods')
    _,bad=case('authored_opening_forbidden',lambda p:p['continuations'][0].update(opening_claims=[]))
    check('continuation_cannot_override_memory',bad['status']=='invalid' and bad['reason']=='path_schema')
    replacement=deepcopy(path['initial_year']);replacement['assets'][0]['life']='5/1'
    check('revision_cannot_rewrite_opening_cohort',revise(path,source,0,replacement,'bad')['reason']=='revision_changes_opening_or_period')
    check('wire_roundtrip',wire(witnesses)==json.loads(json.dumps(wire(witnesses))))
    protected=json.loads((HERE/'baseline.json').read_text())
    check('protected_evidence_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'input':path,'result':run,'witnesses':witnesses}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    start=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence=wire(conformance());target=HERE/'checks.json'
    if args.record:
        if target.exists():raise RuntimeError('Existing evidence')
        target.write_text(json.dumps(evidence,indent=2)+'\n')
        manifest={'started_utc':start,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-operation-path-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; Fraction',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':evidence['input']['initial_year']['source'],'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-operation-path-20261023.md',
            'result':'data/accounting-master/company-operation-path-20261023/result.md',
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists() and evidence!=json.loads(target.read_text()):raise AssertionError('Replay differs')
    failed=[c['name'] for c in evidence['checks'] if not c['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
