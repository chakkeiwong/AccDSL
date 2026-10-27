"""Complete reporting of the accepted prefix at the certified failed payment."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone
from itertools import product
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(H.parent/'guarded-memory-runtime-20261026'))
import bridge as b
import expected as oracle
import company_execution_v1 as native
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
cv=load('reporting_symbolic_substitute',H.parent/'financial-assertion-continuity-20261027/verify.py')
def digest(path):return sha256(path.read_bytes()).hexdigest()

def symbolic_state(case,count):
    mode,right,r1,r2,receipt,a1,a2=case
    values=dict(I1=Q(5) if mode=='fixed' else min(Q(6),max(Q(3),100*Q(r1))),I2=Q(5) if mode=='fixed' else min(Q(6),max(Q(3),100*Q(r2))),R=Q(receipt))
    return cv.substitute(cv.ep.state(count,mode,right,a1,a2),values)

def assert_record(record,plan):
    body,mapping=b.build(*plan['premises'],chart=plan['chart'])
    assert record['case']==plan['case'] and record['program']==body and record['mapping']==mapping
    current,trace,stop=oracle.financial_oracle(body,mapping,plan['premises']);actual=record['execution']
    assert actual['program_sha256']==b.rt.digest(body)
    assert actual['current']==current and len(actual['trace'])==len(trace)
    assert actual['status']==('stopped_provisional' if stop else 'complete_provisional')
    assert actual['remaining_commands']==body['commands'][len(trace):]
    assert actual['opening']==body['opening'] and actual['reports']==[] and actual['archives']==[]
    for flag in b.rt.FLAGS:assert actual[flag] is False
    for got,want,command in zip(actual['trace'],trace,body['commands']):
        assert got['command']==command and got['before_sha256']==b.rt.digest(want['before'])
        assert got['after_sha256']==b.rt.digest(want['after'])
        for part in ('after','journal','flows'):assert got['result']['transition'][part]==want[part]
    if stop:
        assert actual['stop']['command']==body['commands'][len(trace)]
        assert actual['stop']['before_sha256']==actual['stop']['after_sha256']==b.rt.digest(current)
        assert actual['stop']['status']=='invalid' and 'transition' not in actual['stop']['result']
        assert stop['key'] not in current['seen']
    else:assert actual['stop'] is None
    sym=symbolic_state(plan['premises'],len(trace))
    assert {k:Q(current['balances'][mapping[k]]) for k in b.CLASSES}=={k:Q(v) for k,v in sym['book'].items()}
    for k,v in sym['memory'].items():
        assert Q(current['memory'][k])==Q(v) if k in ('due1','due2','paid1','paid2') else current['memory'][k]==v
    flows=[(r['event_id'],r['origin'],r['activity'],r['origin'],Q(r['amount'])) for r in current['flows']]
    # The symbolic recurrence omits the zero repayment when no first draw was made;
    # retain zero flows in the full runtime/oracle comparison and omit only here.
    assert [v for v in flows if v[-1]]==[tuple(v[:4])+(Q(v[4]),) for v in sym['flows'] if Q(v[4])]
    assert record['report']==oracle.report_oracle(body,current)
    assert record['report']['status']=='reported' and record['report']['scope']=='recorded_period_only'
    assert all(Q(v)==0 for v in record['report']['reconciliations'].values())
    assert record['claim_scope']=='recorded_prefix_only_no_default_or_late_settlement'
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def refuse(n,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError) as err:controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old_native=native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'financing-viability-boundary-20261027/attempt-01'
        ck('baseline_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        source_files=[Path(mod.__file__).resolve() for mod in list(sys.modules.values()) if getattr(mod,'__file__',None) and Path(mod.__file__).resolve().is_relative_to(R)]
        for path in source_files+list(B.glob('*.json'))+[H/'verify.py',H/'contract.md',R/'docs/plans/accounting-refused-payment-reporting-20261027.md']:pins[str(path.relative_to(R))]=digest(path)
        save('source-lock.json',pins)
        for n in ('verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        plans=[]
        for chart in ('alpha','beta'):
            for actions in product(('pay','draw'),repeat=2):plans.append(dict(case=chart+':R6:'+':'.join(actions),chart=chart,premises=['floating',True,'19/320','43/800','6',*actions],expected='stopped_provisional'))
            plans.append(dict(case=chart+':R7:draw:pay',chart=chart,premises=['floating',True,'19/320','43/800','7','draw','pay'],expected='complete_provisional'))
        save('inputs-and-expectations.json',plans)
        native.Engine.apply=lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('native financial fallback forbidden'))
        for plan in plans:
            body,mapping=b.build(*plan['premises'],chart=plan['chart']);before=cp(body)
            result=b.rt.run(body);report=b.report(body,result['current'])
            record=dict(case=plan['case'],program=body,mapping=mapping,execution=result,report=report,claim_scope='recorded_prefix_only_no_default_or_late_settlement')
            ck(plan['case']+':complete_independent_record',assert_record(record,plan))
            ck(plan['case']+':input_unchanged',body==before)
            ck(plan['case']+':expected_status',result['status']==plan['expected'])
            ck(plan['case']+':runtime_checker',b.rt.verify(body,result))
            ck(plan['case']+':report_source_unknown','Source and accounting admission' in report['unresolved'])
            ck(plan['case']+':event_completeness_unknown','Event-population completeness' in report['unresolved'])
            cases.append(record)
        base=next(v for v in cases if v['case']=='alpha:R6:draw:pay');plan=next(v for v in plans if v['case']==base['case']);cur=base['execution']['current'];report=base['report']
        ck('unpaid_cash',Q(cur['balances']['cash'])==Q(85,16))
        ck('unpaid_coupon',Q(cur['balances']['interest_payable'])==-Q(43,8) and Q(cur['memory']['due2'])==Q(43,8) and Q(cur['memory']['paid2'])==0)
        ck('repaid_not_reusable',Q(cur['balances']['facility_debt'])==0 and cur['memory']['used'] is True)
        ck('exact_statements',report['balance_sheet']=={'total_assets':'1597/16','total_liabilities':'843/8','equity_including_profit':'-89/16'} and report['income']=={'income':'6/1','expenses':'185/16','profit':'-89/16'})
        ck('exact_flow_totals',report['cash_flows']['activities']['operating']=={'receipts':'6/1','payments':'99/16','net':'-3/16'} and report['cash_flows']['activities']['financing']=={'receipts':'1/1','payments':'1/1','net':'0/1'})
        ck('full_second_coupon_not_only_shortfall',-Q(cur['balances']['interest_payable'])==Q(86,16) and -Q(cur['balances']['interest_payable'])!=Q(1,16))
        mutations=[('erase_payable',lambda z:z['execution']['current']['balances'].update(interest_payable='0/1')),
                   ('claim_payment',lambda z:z['execution']['current']['memory'].update(paid2='43/8')),
                   ('erase_remaining',lambda z:z['execution'].update(remaining_commands=[])),
                   ('claim_completion',lambda z:z['execution'].update(status='complete_provisional')),
                   ('mark_refused_seen',lambda z:z['execution']['current']['seen'].append('pay2')),
                   ('change_receipt',lambda z:z['execution']['current']['balances'].update(income='-7/1')),
                   ('change_origin',lambda z:z['execution']['current']['flows'][0].update(origin='operating_receipt')),
                   ('wrong_report_payable',lambda z:z['report']['balance_sheet'].update(total_liabilities='100/1')),
                   ('net_away_gross_flows',lambda z:z['report']['cash_flows']['activities'].update(financing={'receipts':'0/1','payments':'0/1','net':'0/1'})),
                   ('drop_failed_state',lambda z:z['execution'].update(current=z['program']['opening'])),
                   ('drop_refusal',lambda z:z['execution'].update(stop=None)),
                   ('invent_default',lambda z:z.update(claim_scope='legal_default'))]
        for name,change in mutations:
            bad=cp(base);change(bad);refuse(name,lambda v=bad:assert_record(v,plan))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),native_fallback_disabled=True,scope='exact refused-prefix states and complete recorded-period reports')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        native.Engine.apply=old_native
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact deterministic conformance',data_version='source-lock.json',plan='docs/plans/accounting-refused-payment-reporting-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
