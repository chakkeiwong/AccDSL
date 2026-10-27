"""Independent columns, publication boundaries and correction-origin challenges."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode=True
from reference import OUT,ROOT,CATALOG,FIXTURE,TRUE_FINDINGS,EPS_FINDINGS,calculate


def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for n in ['reference.py','verify.py','authored-cases.json','input-lock-v2.json','synthetic-editions-v2.json']:
        shutil.copy2(OUT/n,attempt/n)
    checks=[];exchanges=[];adverse_cases=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for item in json.loads((OUT/'input-lock-v2.json').read_text())['files']:
        check('input/'+item['path'],hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'])
    assert all(c['passed'] for c in checks)
    authored=json.loads((OUT/'authored-cases.json').read_text());expected=authored['expected']
    baseline=json.loads((ROOT/'data/accounting-master/p17-completion-20261014/P17-04/error-estimate/computed.json').read_text())['paths']
    catalog_before=(ROOT/CATALOG).read_bytes();fixture_before=(ROOT/FIXTURE).read_bytes()
    for case in authored['cases']:
        req=deepcopy(case['request']);before=deepcopy(req);a=calculate(req)
        exchanges.append(dict(id=case['id'],request=req,result=a))
        check(case['id']+'/status',a['status']=='conditional_complete',a['reason'])
        if a['status']!='conditional_complete':continue
        report=a['report'];edition=a['selected_edition']
        check(case['id']+'/edition',edition['id']==case['edition'],edition['id'])
        check(case['id']+'/readonly',a['mutations']==[] and report['posts_correction'] is False and before==req and a==calculate(req))
        check(case['id']+'/full-covered-columns',set(report['statements'])==set(map(str,edition['years'])))
        check(case['id']+'/cutoffs',edition['published']<=req['public_cutoff'] and edition['ingested']<=req['system_cutoff'])
        for year,row in report['statements'].items():
            key=edition['kind']+'_'+year
            for column,value in expected['rows'][key].items():
                check(case['id']+'/'+year+'/'+column,row[column]==value,dict(actual=row[column],expected=value))
            other=('error' if edition['kind']=='restated' else 'original')+'_'+year
            check(case['id']+'/'+year+'/monthly-comparator',row==baseline[other])
            flow=report['cash_equity_flows'][year]
            check(case['id']+'/'+year+'/operating',flow['operating_direct']==flow['operating_indirect']==expected['operating_cash'][key])
            check(case['id']+'/'+year+'/cash-roll',Q(flow['closing_cash'])-Q(flow['opening_cash'])==Q(flow['operating_direct'])+Q(flow['investing']))
            check(case['id']+'/'+year+'/equity-roll',Q(flow['opening_equity'])+Q(flow['profit'])==Q(flow['closing_equity']))
        if edition['kind']=='restated':
            check(case['id']+'/third-opening',report['third_statement']==expected['earliest_opening'])
            for name,key in [('earliest_opening','opening_correction'),('comparative','comparative_correction'),('current_opening','current_opening_correction')]:
                check(case['id']+'/'+name,report['corrections'][name]==expected[key])
            bridge=report['equity_bridge']
            check(case['id']+'/equity-independent',bridge==dict(original_current_opening_equity='260',earliest_opening_correction='-15/2',comparative_profit_correction='-15/2',corrected_current_opening_equity='245',current_profit='45/2',closing_equity='535/2',current_profit_prior_error_charge='0',cash_correction='0'))
            check(case['id']+'/no-double-opening',Q('260')+Q('-15/2')+Q('-15/2')+Q('45/2')==Q(report['statements']['2025']['equity']))
        else:
            check(case['id']+'/no-future-correction',report['corrections']=={} and report['third_statement'] is report['equity_bridge'] is report['earliest_opening'] is None)
    base=next(x['request'] for x in authored['cases'] if x['id']=='current-restated')
    no_third=deepcopy(base);no_third['findings']['material_earliest_opening_effect']=False
    a=calculate(no_third)
    check('separate-opening-materiality',a['status']=='conditional_complete' and a['report']['third_statement'] is None and a['report']['earliest_opening']==expected['earliest_opening'])
    unknown_original=deepcopy(authored['cases'][0]['request'])
    for k in TRUE_FINDINGS-{'authority_profile_admitted','tax_facts_admitted'}:unknown_original['findings'][k]=None
    a=calculate(unknown_original)
    check('original-not-conditioned-on-later-correction',a['status']=='conditional_complete' and a['selected_edition']['id']=='original-2024' and a['report']['corrections']=={})
    latest_earlier=deepcopy(base);latest_earlier['selector']['year']=2023
    a=calculate(latest_earlier)
    check('opening-is-not-full-2023-income',a['status']=='conditional_complete' and a['selected_edition']['id']=='original-2024' and a['report']['statements']['2023']==expected['rows']['original_2023'])
    def adverse(id,status,reason,mutate):
        req=deepcopy(base);mutate(req);adverse_cases.append(dict(id=id,request=req,status=status,reason=reason))
    for key in TRUE_FINDINGS:
        adverse('missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['findings'].update({k:None}))
        adverse('false-'+key,'unsupported','finding_'+key,lambda r,k=key:r['findings'].update({k:False}))
    for key in EPS_FINDINGS:
        adverse('missing-'+key,'unresolved','missing_'+key,lambda r,k=key:r['findings'].update({k:None}))
        adverse('true-'+key,'unsupported','eps_profile_required',lambda r,k=key:r['findings'].update({k:True}))
    adverse('unknown-opening-materiality','unresolved','missing_material_earliest_opening_effect',lambda r:r['findings'].update(material_earliest_opening_effect=None))
    adverse('wrong-entity','rejected','context_mismatch',lambda r:r['context'].update(entity='other'))
    adverse('wrong-rule','rejected','context_mismatch',lambda r:r['context'].update(rule='current-IFRS'))
    adverse('wrong-unit','rejected','context_mismatch',lambda r:r['context'].update(unit='thousands'))
    adverse('unknown-edition','rejected','edition_unknown',lambda r:r['selector'].update(mode='edition',edition='missing'))
    adverse('edition-wrong-year','rejected','edition_year_mismatch',lambda r:r['selector'].update(mode='edition',edition='original-2023',year=2024))
    adverse('explicit-unpublished','unresolved','no_available_edition',lambda r:(r['selector'].update(mode='edition',edition='restated-2025'),r.update(public_cutoff='2026-04-01')))
    adverse('explicit-not-ingested','unresolved','no_available_edition',lambda r:(r['selector'].update(mode='edition',edition='restated-2025'),r.update(system_cutoff='2026-04-02')))
    adverse('year-not-yet-published','unresolved','no_available_edition',lambda r:r.update(public_cutoff='2025-03-30'))
    adverse('unsupported-year','unsupported','year_profile',lambda r:r['selector'].update(year=2022))
    adverse('boolean-year','unsupported','year_profile',lambda r:r['selector'].update(year=True))
    adverse('mixed-selector','rejected','selector_identity',lambda r:r['selector'].update(edition='original-2024'))
    adverse('bad-cutoff','rejected','date_encoding',lambda r:r.update(public_cutoff='2026-02-30'))
    adverse('integer-finding','rejected','finding_type',lambda r:r['findings'].update(fully_practicable=1))
    adverse('forged-numbers','rejected','request_shape',lambda r:r.update(statements={'2024':{'net_profit':'30'}}))
    adverse('post-comparative','rejected','report_only',lambda r:r.update(operation='post'))
    adverse('post-correction','rejected','request_shape',lambda r:r.update(post_correction=True))
    for case in adverse_cases:
        before=deepcopy(case['request']);a=calculate(case['request']);case['actual']=dict(status=a['status'],reason=a['reason'])
        check(case['id']+'/refusal',(a['status'],a['reason'])==(case['status'],case['reason']),case['actual'])
        check(case['id']+'/atomic',a['report'] is a['selected_edition'] is None and a['mutations']==[] and case['request']==before)
    def absent(p):
        if str(p.relative_to(ROOT))==CATALOG:raise FileNotFoundError(p)
        return p.read_bytes()
    def corrupt(p):return b'changed' if str(p.relative_to(ROOT))==FIXTURE else p.read_bytes()
    for id,reader,status,reason in [('missing-catalog',absent,'unresolved','input_bytes_missing'),('changed-facts',corrupt,'rejected','input_bytes_changed')]:
        a=calculate(base,reader);check(id,(a['status'],a['reason'])==(status,reason) and a['report'] is None)
    check('original-files-unchanged',catalog_before==(ROOT/CATALOG).read_bytes() and fixture_before==(ROOT/FIXTURE).read_bytes())
    summary=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),attempt=attempt.name,checks=len(checks),
        failures=sum(not c['passed'] for c in checks),failed=[c for c in checks if not c['passed']],
        cases=len(authored['cases']),adverse_inputs=len(adverse_cases),resolver_challenges=2,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/comparative-rebuild-20261016/verify.py',
        interpreter=sys.executable,environment='tfgpu Python standard library/Fraction; no ML import',
        gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        data_version='input-lock-v2.json; independently authored editions and statement columns',
        random_seeds='N/A: deterministic',wall_seconds=round(time.monotonic()-started,3),
        plan='docs/plans/accounting-comparative-rebuild-20261016.md',result='data/accounting-master/comparative-rebuild-20261016/result.md',
        outputs=[str((attempt/n).relative_to(ROOT)) for n in ['summary.json','checks.json','exchanges.json','adverse.json']])
    for n,v in [('summary.json',summary),('checks.json',checks),('exchanges.json',exchanges),('adverse.json',adverse_cases)]:
        (attempt/n).write_text(json.dumps(v,indent=2)+'\n')
    print(json.dumps({k:summary[k] for k in ['attempt','checks','failures','failed','cases','adverse_inputs','wall_seconds']}))
    if summary['failures']:raise SystemExit(1)


if __name__=='__main__':main()
