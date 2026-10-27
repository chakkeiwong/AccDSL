"""Exact complete-output and adversarial controls, with frozen run evidence."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as F
from datetime import datetime,timezone
import json,os,sys,time,platform,subprocess,resource,traceback,fitz
import reference as m
import fixtures as f
H=Path(__file__).resolve().parent;R=H.parents[2]
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(110,110));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={R/p for p in json.loads((H/'predecessor-lock.json').read_text())}
    files.update(H/p for p in ['reference.py','fixtures.py','verify.py','prepare.py','contract.md','predecessor-lock.json'])
    files.add(R/'docs/plans/accounting-intragroup-upstream-20261027.md')
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        q=out/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    def ck(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected))
        if actual!=expected:raise AssertionError(name+': '+repr(actual)[:240]+' != '+repr(expected)[:240])
    def run(election,mix,settled,tax,sold):
        name='/'.join([election,mix,'settled' if settled else 'credit',tax,sold]);b=f.fixture(election,mix,settled,tax,sold);before=deepcopy(b);r=m.report(b)
        ck(name+'/status',r['status'],'tax_method_required' if tax=='unresolved' else 'conditional_upstream_worksheet')
        ck(name+'/immutable',b,before);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        expected=f.expected(election,mix,settled,tax,sold)
        for k,v in expected.items():ck(name+'/'+k,r[k],v)
        ck(name+'/request_identity',r['request_sha256'],f.digest(b))
        ck(name+'/base_identity',r['base_result_sha256'],b['payload']['base_result_sha256'])
        ck(name+'/unique_journals',len({x['id'] for x in r['legal_journals']}),len(r['legal_journals']))
        old=f.prior(election,mix)['result']
        ck(name+'/acquisition_balances_unchanged',r['acquisition_worksheet']['balances'],old['acquisition_worksheet']['balances'])
        for e in ['P','S']:
            state={k:F(0) for k in r['original_books'][e]['snapshots']['closing']['balances']}
            for event in r['legal_journals']:
                if event['entity']!=e:continue
                ck(name+'/balanced/'+event['id'],sum(F(x) for x in event['entries'].values()),F(0))
                for k,v in event['entries'].items():state[k]+=F(v)
                ck(name+'/nonnegative_cash/'+event['id'],state['cash']>=0)
            ck(name+'/replayed_closing/'+e,f.ser(state),r['original_books'][e]['snapshots']['closing']['balances'])
        # External payment must remain gross; paired internal cash cancels each side.
        ck(name+'/vendor_payment',r['external_cash_origins'][0]['amount'],'-20/1')
        ck(name+'/external_not_eliminated',all(x['elimination']=='0/1' for x in r['external_cash_origins']))
        ck(name+'/internal_cancelled',all(F(x['amount'])+F(x['elimination'])==0 for x in r['intragroup_cash_origins']))
        if tax=='unresolved':ck(name+'/no_report','report' not in r)
        else:
            report=r['report'];z=r['closing_worksheet']['balances']
            assets=sum(F(z.get(k,0)) for k in ['cash','inventory','equipment','goodwill','inventory_deferred_tax_asset'])
            liabilities=-sum(F(z.get(k,0)) for k in ['payable','deferred_tax','current_tax_payable'])
            income=-sum(F(z.get(k,0)) for k in ['revenue','merchandise_revenue','cost_of_sales','depreciation','operating_expense','current_tax_expense','tax_expense','intragroup_deferred_tax_expense'])
            ck(name+'/accounts_assets',assets,F(report['assets_closing']));ck(name+'/accounts_liabilities',liabilities,F(report['liabilities_closing']));ck(name+'/accounts_profit',income,F(report['profit']))
            for k in ['net_assets_at_acquisition','nci_at_acquisition','goodwill']:ck(name+'/fixed_acquisition/'+k,report[k],old['report'][k])
            if (election,mix,settled,sold)==('proportional','cash',False,'0/1'):
                anchor={'recognised':dict(profit='63/2',owners_profit='189/8',nci_profit='63/8',assets_closing='1549/4',liabilities_closing='27/1',equity_closing='1441/4'),
                        'unrecognised':dict(profit='29/1',owners_profit='87/4',nci_profit='29/4',assets_closing='1539/4',liabilities_closing='27/1',equity_closing='1431/4')}[tax]
                for k,v in anchor.items():ck(name+'/absolute/'+k,report[k],v)
                ck(name+'/absolute/cash',report['cash']['closing'],'250/1')
            if (election,mix,settled,tax,sold)==('proportional','cash',False,'recognised','1/2'):
                for k,v in dict(profit='39/1',owners_profit='483/16',nci_profit='141/16',assets_closing='396/1',liabilities_closing='113/4',equity_closing='1471/4',owners_equity_closing='5283/16',nci_closing='601/16').items():ck(name+'/half_anchor/'+k,report[k],v)
        cases.append(dict(id=name,request=b,result=r));return r
    def reject(name,b,reason,rehash=True):
        if rehash:f.bind(b)
        before=deepcopy(b);r=m.report(b);ck(name+'/status',r['status'],'invalid');ck(name+'/reason',r['reason'],reason)
        ck(name+'/immutable',b,before);ck(name+'/no_report','report' not in r);ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS));controls.append(dict(id=name,request=b,result=r))
    try:
        for rel,page,anchor in [('acquisition-intragroup-20261027/source-inspection-02/aasb10-2026.pdf',31,'eliminate in full intragroup'),('acquisition-intragroup-20261027/source-inspection-02/aasb10-2026.pdf',32,'even if this results'),('acquisition-intragroup-20261027/source-inspection-01/aasb112-compiled-sep2023.pdf',9,'appropriate tax base'),('acquisition-intragroup-20261027/source-inspection-01/aasb112-compiled-sep2023.pdf',33,'Unrealised profits resulting')]:
            txt=' '.join(fitz.open(H.parent/rel)[page-1].get_text().split());ck('source/'+rel+'/'+str(page),anchor in txt)
        run('proportional','cash',False,'recognised','0/1')
        for election in ['proportional','fair_value','none']:
            for mix in ['cash','equity','mixed']:
                for settled in [False,True]:
                    for sold in ['0/1','1/2','1/1']:
                        if (election,mix,settled,sold)!=('proportional','cash',False,'0/1'):run(election,mix,settled,'recognised',sold)
        for tax in ['unrecognised','unresolved']:
            for settled in [False,True]:
                for sold in ['0/1','1/2','1/1']:run('proportional','cash',settled,tax,sold)
        b=f.fixture();b['payload']['supplier_purchase']['amount']='19/1';reject('stale_payload',b,'payload_binding',False)
        for key,reason in [('base_result_sha256','base_result_binding'),('source_lock_sha256','source_lock_binding')]:
            b=f.fixture();b['payload'][key]='0'*64;reject(key,b,reason)
        for block,field,value,reason in [
            ('supplier_purchase','buyer','P','supplier_parties'),('supplier_purchase','vendor','P','supplier_parties'),('supplier_purchase','at','2025-06-01T00:00:00Z','supplier_date'),('supplier_purchase','amount','0/1','supplier_amount'),('supplier_purchase','currency','HKD','supplier_units'),('supplier_purchase','tax_premise','unknown','supplier_tax_premise'),
            ('trade','seller','P','upstream_parties'),('trade','buyer','S','upstream_parties'),('trade','at','2025-06-01T00:00:00Z','trade_date'),('trade','price','31/1','trade_amounts'),('trade','impairment','unknown','impairment_scope'),
            ('external_sale','seller','S','external_parties'),('external_sale','customer','S','external_parties'),('external_sale','at','2026-01-01T00:00:00Z','external_date'),('external_sale','unit','thousands','external_units'),('external_sale','fraction','1/3','selected_resale_fraction'),('external_sale','receipts','1/1','external_amounts'),('external_sale','recognition','cash_received','revenue_premise'),
            ('tax','seller_rate','1/3','selected_tax_rates'),('tax','tax_base','20/1','tax_base'),('tax','recognition','automatic','recognition_disposition'),('tax','allocation','parent_owners_stipulated_downstream','tax_allocation_required')]:
            b=f.fixture();b['payload'][block][field]=value;reject(block+'/'+field,b,reason)
        for field,value,reason in [('payer','S','settlement_pair'),('at','2025-09-01T00:00:00Z','settlement_date'),('amount','20/1','settlement_amount_units')]:
            b=f.fixture(settled=True);b['payload']['settlement'][field]=value;reject('settlement/'+field,b,reason)
        b=f.fixture();b['payload']['elimination_fraction']='3/4';reject('scaled_elimination',b,'full_elimination_required')
        b=f.fixture();b['payload']['base_request']['payload']['acquired_items'][1]['recognised_balance']='91/1';reject('changed_acquisition',b,'selected_base_request')
        b=f.fixture();s=b['payload']['books']['S']['snapshots']['closing']['balances'];s['cash']='90/1';s['capital']='-100/1';reject('balanced_missing_supplier_cash',b,'complete_legal_books')
        b=f.fixture();s=b['payload']['books']['S']['snapshots']['closing']['balances'];s['current_tax_expense']='0/1';s['current_tax_payable']='0/1';reject('balanced_missing_seller_tax',b,'complete_legal_books')
        b=f.fixture();b['payload']['event_calendar']['precontrol_close']='2025-08-01T00:00:00Z';reject('wrong_history',b,'selected_event_calendar')
        b=f.fixture();b['payload']['history_premise']='inferred';reject('invented_history',b,'history_premise')
        b=f.fixture();b['payload']['supplier_purchase']['extra']=True;reject('open_schema',b,'supplier_purchase_fields')
        b=f.fixture();b['payload']['books_sha256']='0'*64;b['expected_payload_sha256']=f.digest(b['payload']);reject('books_identity',b,'books_binding',False)
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,value in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n')
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,text=True,capture_output=True)
    manifest=dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable: '+git.stderr.strip()[:160],command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-intragroup-upstream-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
