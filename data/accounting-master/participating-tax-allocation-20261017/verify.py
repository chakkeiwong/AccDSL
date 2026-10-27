"""Source reproduction, independent direct entitlements, and atomic refusals."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from reference import evaluate

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]


def main():
    start=time.monotonic();checks=[];outputs=[];negatives=[]
    attempt=OUT/'attempt-01';attempt.mkdir(exist_ok=False)
    def check(name,ok): checks.append(dict(name=name,passed=bool(ok)))
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    def validate(id,r,expected=None):
        before=deepcopy(r);v=evaluate(r)
        check(id+'/accepted',v['status']=='conditional_complete')
        check(id+'/input_unchanged',r==before)
        check(id+'/no_postings',v['journals']==[] and v['mutations']==[])
        check(id+'/no_dilution_selection',v['diluted'] is None and v['selected'] is None
              and v['selection_status']=='not_evaluated')
        if v['result'] is not None:
            a={k:Q(x) for k,x in r['amounts'].items()};o=v['result'];p=a['profit_before_benefit']
            ratio=a['participating_ratio'];t=a['tax_rate']
            # Independently derive current-period entitlements, without using the stepwise reference.
            participant=p*ratio/(1+ratio)
            ordinary=p-participant+t*participant
            check(id+'/direct_ordinary',Q(o['ordinary_earnings'])==ordinary)
            check(id+'/direct_participating',Q(o['participating_earnings'])==participant)
            check(id+'/direct_eps',Q(o['basic_eps'])==ordinary/a['weighted_average_ordinary'])
            check(id+'/hypothetical_total',Q(o['total_eps_earnings'])==p+t*participant)
            check(id+'/context',o['context']==r['context'])
            for k,x in (expected or {}).items():check(id+'/'+k,o[k]==x)
        outputs.append(dict(id=id,output=v))
        return v
    for c in cases:validate(c['id'],c['request'],c['expected'])
    # The source period chain is not three unrelated snapshots.
    for i in (0,1):
        check(f'source-chain-{i+1}',outputs[i]['output']['result']['closing_base_balance']==
              cases[i+1]['request']['amounts']['opening_base_balance'])
    check('source-total-ordinary',sum(Q(outputs[i]['output']['result']['ordinary_earnings']) for i in range(3))==360)
    for i in range(3):
        check(f'recognition-location-{i+1}',outputs[i]['output']['result']==outputs[i+3]['output']['result'])
    check('negative-residual-preserved',outputs[2]['output']['result']['residual_tax']=='-150')
    check('hypothetical-not-book-profit',outputs[0]['output']['result']['total_eps_earnings']=='420'
          and cases[0]['request']['amounts']['reported_profit']=='330')

    # Payout timing and rate/rights boundaries are algebraic diagnostics, not empirical samples.
    base=cases[0]['request']
    grid_count=0
    for ratio in (Q(0),Q(1),Q(10)):
        for tax in (Q(0),Q(1,4),Q(3,10)):
            for payout in (Q(0),Q(88),Q(176)):
                r=deepcopy(base);p=Q(88);dp=payout*ratio/(1+ratio);do=payout/(1+ratio);h=tax*dp
                r['amounts'].update({k:str(v) for k,v in dict(profit_before_benefit=p,opening_base_balance=88,
                    participating_ratio=ratio,tax_rate=tax,participating_dividend=dp,
                    ordinary_base_dividend=do,ordinary_tax_dividend=h,actual_tax_benefit=h,reported_profit=p+h).items()})
                validate(f'payout-{grid_count}',r);grid_count+=1

    def bad(id,change,status,reason):
        r=deepcopy(base);change(r);before=deepcopy(r);v=evaluate(r)
        check(id+'/status',v['status']==status);check(id+'/reason',v['reason']==reason)
        check(id+'/atomic',v['result'] is None and v['trace']==[] and v['journals']==[] and v['mutations']==[])
        check(id+'/input_unchanged',r==before)
        negatives.append(dict(id=id,request=r,output=v))
    for name in base['findings']:
        bad('missing-'+name,lambda r,n=name:r['findings'].update({n:None}),'unresolved','missing_finding/'+name)
        bad('false-'+name,lambda r,n=name:r['findings'].update({n:False}),'unsupported','unsupported_finding/'+name)
    bad('nonboolean-finding',lambda r:r['findings'].update(equity_classification=1),'rejected','finding_type')
    bad('unknown-field',lambda r:r.update(final_diluted=True),'rejected','request_fields')
    bad('missing-context',lambda r:r.pop('context'),'rejected','request_fields')
    bad('final-diluted-request',lambda r:r.update(operation='diluted'),'unsupported','operation_not_supported')
    bad('future-facts',lambda r:r['context'].update(facts_available_on='2024-04-01'),'rejected','future_information')
    bad('bad-date',lambda r:r['context'].update(start='2023-02-30'),'rejected','date')
    bad('wrong-profile',lambda r:r['context'].update(rule='current-all-GAAP'),'rejected','source_profile')
    bad('duplicate-classes',lambda r:r['context'].update(participating_class='O'),'rejected','class_collision')
    bad('zero-denominator',lambda r:r['amounts'].update(weighted_average_ordinary='0'),'rejected','ordinary_denominator')
    bad('unknown-denominator',lambda r:r['amounts'].update(weighted_average_ordinary=None),'unresolved','missing_amount/weighted_average_ordinary')
    bad('numeric-rational',lambda r:r['amounts'].update(tax_rate=0.3),'rejected','rational_type')
    bad('noncanonical',lambda r:r['amounts'].update(tax_rate='6/20'),'rejected','noncanonical_rational')
    bad('tax-one',lambda r:r['amounts'].update(tax_rate='1'),'rejected','tax_rate')
    bad('negative-profit',lambda r:r['amounts'].update(profit_before_benefit='-1'),'unsupported','loss_tax_not_specified')
    bad('negative-ratio',lambda r:r['amounts'].update(participating_ratio='-1'),'rejected','negative_amount')
    bad('ratio-mismatch',lambda r:r['amounts'].update(participating_dividend='10'),'rejected','dividend_rights_mismatch')
    bad('wrong-benefit',lambda r:r['amounts'].update(actual_tax_benefit='1'),'rejected','actual_tax_mismatch')
    bad('wrong-tax-payout',lambda r:r['amounts'].update(ordinary_tax_dividend='1'),'rejected','tax_benefit_payout_mismatch')
    bad('double-count-benefit',lambda r:r['amounts'].update(reported_profit='420'),'rejected','reported_profit_mismatch')
    bad('unfunded-payout',lambda r:r['amounts'].update(participating_dividend='400',ordinary_base_dividend='40',
        ordinary_tax_dividend='120',actual_tax_benefit='120',reported_profit='450'),'rejected','unfunded_base_dividend')

    lock=json.loads((OUT/'input-lock.json').read_text())['files']
    with tempfile.TemporaryDirectory(prefix='accdsl-participating-tax-') as temporary:
        copied=Path(temporary)
        for item in lock:
            p=copied/item['path'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/item['path'],p)
        for item in lock:
            p=copied/item['path'];original=p.read_bytes();p.write_bytes(original+b'\nchanged\n')
            v=evaluate(base,source_root=copied)
            check('changed-source/'+item['path'],v['status']=='rejected' and v['reason']=='source_or_input_changed'
                  and v['result'] is None and v['trace']==[])
            p.write_bytes(original)
    result=dict(checks=len(checks),failures=sum(not c['passed'] for c in checks),detail=checks,
        authored_cases=len(cases),payout_cases=grid_count,adverse_requests=len(negatives),source_challenges=len(lock),
        outputs=outputs,adverse=negatives)
    (attempt/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    manifest=dict(command='python3 data/accounting-master/participating-tax-allocation-20261017/verify.py',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        environment='system Python standard library; deterministic rational arithmetic',
        hardware='CPU only; no numerical framework import or GPU detection',seeds='N/A: exact deterministic cases',
        data_version='frozen authored-cases.json and input-lock.json',wall_seconds=time.monotonic()-start,
        plan='docs/plans/accounting-participating-tax-allocation-20261017.md',result=str((OUT/'result.md').relative_to(ROOT)),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
               for p in (OUT/'reference.py',Path(__file__).resolve(),OUT/'input-lock.json',attempt/'checks.json')])
    (attempt/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('checks','failures','authored_cases','payout_cases','adverse_requests','source_challenges')}))
    if result['failures']:raise SystemExit(1)


if __name__=='__main__':main()
