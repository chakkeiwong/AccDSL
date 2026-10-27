"""Full explicit synthetic expected reports, journals and refusal controls."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from datetime import datetime,timezone
from fractions import Fraction
import json,sys,os,time,platform,subprocess,resource,traceback
import reference as m
from fixtures import payload
H=Path(__file__).resolve().parent;R=H.parents[2]
EXPECTED=json.loads((H/'expectations.json').read_text())
def bind(b,books=True):
    if books:b['payload']['expected_books_sha256']=m.h.digest(b['payload']['books'])
    b['expected_payload_sha256']=m.h.digest(b['payload']);return b
def fixture(election='proportional',loss=False):return bind(dict(profile=m.PROFILE,payload=payload(election,loss),expected_payload_sha256=''))
def expected_report(election,loss=False):
    e=deepcopy(EXPECTED[election])
    if loss:
        assert election=='proportional'
        e['closing_balances'].update(payable='-220/1',operating_expense='200/1')
        e.update(profit='-337/2',owners_profit='-1011/8',nci_profit='-337/8',nci_closing='-107/8',owners_equity_closing='1389/8',liabilities_closing='449/2',equity_closing='641/4')
    return e
def expected_journals(election):
    e=EXPECTED[election]
    return [dict(id='acquisition',origin='Conditional supplied item measurements and investment/equity elimination',at='2025-07-01T00:00:00Z',entries={'S.capital':'80/1','S.retained_pre':'20/1','S.equipment':'20/1','group.goodwill':e['goodwill'],'group.deferred_tax':'-5/1','P.investment':'-120/1','group.nci':str(-Fraction(e['nci_at_acquisition']).numerator)+'/'+str(Fraction(e['nci_at_acquisition']).denominator)}),dict(id='basis-depreciation',origin='Supplied acquired equipment basis expense',at='2026-01-01T00:00:00Z',entries={'S.equipment':'-2/1','group.depreciation':'2/1'}),dict(id='tax-liability-release',origin='Stipulated tax liability and later release; no tax recognition/rate inference',at='2026-01-01T00:00:00Z',entries={'group.deferred_tax':'1/2','group.tax_expense':'-1/2'})]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(100,100));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={H/f for f in ['reference.py','verify.py','fixtures.py','expectations.json','contract.md']}
    files.add(R/'docs/plans/accounting-acquisition-worksheet-20261027.md')
    files.update(m.SYMBOLIC/f for f in ['reference.py','contract.md','result.md','attempt-01/cases.json','attempt-01/verification.json','attempt-01/source-lock.json'])
    files.update(R/p for p in json.loads((m.SYMBOLIC/'attempt-01/source-lock.json').read_text()))
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dst=out/'inputs'/p.relative_to(R);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes())
    def ck(name,a,b=True):
        checks.append(dict(name=name,passed=a==b))
        if a!=b:raise AssertionError(name+': '+repr(a)[:200]+' != '+repr(b)[:200])
    def run(name,b,election='proportional',loss=False):
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'conditional_worksheet')
        ck(name+'/immutable',b,before);ck(name+'/original_legal_books',r['original_books'],b['payload']['books'])
        ck(name+'/all_report_fields',r['report'],expected_report(election,loss))
        ck(name+'/items',r['acquired_items'],b['payload']['acquired_items']);ck(name+'/premises',r['basis_premises'],b['payload']['basis_premises'])
        ck(name+'/scope_and_unknowns',r['symbolic_result'],m.sym.derive(b['payload']['symbolic_request']))
        ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(name+'/identity',r['request_sha256'],m.h.digest(b))
        for stage,key in [('acquisition','acquisition_worksheet'),('closing','closing_worksheet')]:
            raw={owner+'.'+account:value for owner in ['P','S'] for account,value in b['payload']['books'][owner]['snapshots'][stage]['balances'].items()}
            ck(name+'/'+stage+'/all_original_accounts',r[key]['raw'],raw)
            js=expected_journals(election)[:1] if stage=='acquisition' else expected_journals(election)
            ck(name+'/'+stage+'/all_adjustment_origins',r[key]['journals'],js)
            expected_accounts={k:Fraction(v) for k,v in raw.items()}
            for j in js:
                for account,value in j['entries'].items():expected_accounts[account]=expected_accounts.get(account,Fraction(0))+Fraction(value)
            ck(name+'/'+stage+'/all_adjusted_accounts',r[key]['adjusted'],{k:str(v.numerator)+'/'+str(v.denominator) for k,v in expected_accounts.items()})
        if loss:ck(name+'/nci_deficit_retained',Fraction(r['report']['nci_closing'])<0)
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True,books=True):
        if rehash:bind(b,books)
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason)
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));ck(name+'/no_report','report' not in r)
        controls.append(dict(id=name,request=b,result=r))
    try:
        for election in ['proportional','fair_value','none']:run(election,fixture(election),election)
        run('nci_deficit',fixture(loss=True),loss=True)
        b=fixture();b['payload']['consideration']='121/1';reject('stale_envelope',b,'payload_binding',False)
        b=fixture();b['payload']['books']['P']['snapshots']['closing']['balances']['cash']='181/1';reject('stale_books',b,'books_binding',books=False)
        b=fixture();b['payload']['acquired_items'].pop();reject('missing_item',b,'acquired_item_population')
        b=fixture();b['payload']['acquired_items'][2]=deepcopy(b['payload']['acquired_items'][1]);reject('duplicate_item',b,'acquired_item_identity')
        b=fixture();b['payload']['acquired_items'][1]['legal_balance']='71/1';reject('stale_item_amount',b,'item_legal_balance')
        b=fixture();b['payload']['acquired_items'][3]['recognised_balance']='5/1';reject('liability_wrong_sign',b,'item_kind_sign')
        b=fixture();b['payload']['acquired_items'][1]['at']='2025-07-01T00:00:00.1Z';reject('subday_item_shift',b,'item_date')
        b=fixture();b['payload']['acquired_items'][0]['currency']='HKD';reject('item_currency',b,'item_unit')
        b=fixture();b['payload']['consideration']='80/1';reject('face_value_substitution',b,'investment_binding')
        b=fixture();b['payload']['books']['S']['snapshots']['closing']['balances'].update(retained_pre='0/1',revenue='-60/1');reject('precontrol_profit_leak',b,'precontrol_equity_preserved')
        b=fixture();b['payload']['books']['S']['snapshots']['acquisition']['balances'].update(retained_pre='0/1',revenue='-20/1');reject('annual_acquisition_income',b,'acquisition_income_state')
        b=fixture();b['payload']['books']['P']['snapshots']['closing']['balances'].update(cash='190/1',capital='-310/1');reject('unexplained_parent',b,'unexplained_parent_movement')
        b=fixture();b['payload']['books']['S']['snapshots']['closing']['at']='2025-12-31T00:00:00Z';reject('closing_date',b,'snapshot_date:S/closing')
        b=fixture();b['payload']['books']['S']['unit']='thousands';reject('book_unit',b,'book_context')
        b=fixture();b['payload']['books']['S']['snapshots']['closing']['balances']['unmapped']='0/1';reject('unmapped_account',b,'account_population:S/closing')
        b=fixture();b['payload']['expense_adjustment']='21/1';reject('exhausted_basis',b,'adjustment_bounds')
        b=fixture();b['payload']['tax_release']='6/1';reject('excess_tax_release',b,'adjustment_bounds')
        b=fixture();b['payload']['operating_cash']='60/1';reject('precontrol_cash_leak',b,'postcontrol_cash_revenue')
        b=fixture();b['payload']['acquired_items'][0]['recognised_balance']='60/1';reject('invented_acquired_cash',b,'unsupported_item_remeasurement')
        b=fixture();b['payload']['synthetic_premise']='Actual company accounting';reject('actual_admission_attempt',b,'synthetic_case_required')
        b=fixture();b['payload']['basis_premises']['tax']='';reject('missing_tax_premise',b,'text_required')
        b=fixture();b['payload']['cashless']=True;reject('noncash_unsupported_schema',b,'payload_fields')
        b=fixture();b['payload']['nci_fair_value']='40/1';reject('two_nci_elections',b,'unused_nci_measurement')
        b=fixture('fair_value');b['payload']['nci_fair_value']='-1/1';reject('negative_fair_nci',b,'negative_nci_measurement')
        b=fixture();b['payload']['consideration']='10/1'
        for stage in ['acquisition','closing']:b['payload']['books']['P']['snapshots'][stage]['balances'].update(cash='290/1',investment='10/1')
        reject('bargain_gain_shortcut',b,'excess_requires_other_method')
        b=fixture();b['payload']['symbolic_request']['payload']['prior_interest']['kind']='debt';b['payload']['symbolic_request']['expected_payload_sha256']=m.h.digest(b['payload']['symbolic_request']['payload']);reject('debt_route',b,'symbolic:unresolved')
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,obj in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic synthetic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-acquisition-worksheet-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
