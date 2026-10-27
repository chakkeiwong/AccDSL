"""Independent full-state checks for selected partial coupon settlement."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime, timezone
import importlib.util, json, os, platform, resource, subprocess, sys, time, traceback
import partial as s
H=Path(__file__).resolve().parent; R=H.parents[2]
sys.path.insert(0,str(H.parent/'coupon-carry-20261027'))
spec=importlib.util.spec_from_file_location('partial_carry_checker',H.parent/'coupon-carry-20261027/verify.py')
prior=importlib.util.module_from_spec(spec); spec.loader.exec_module(prior)
oracle=prior.oracle
def digest(p): return sha256(p.read_bytes()).hexdigest()
def fmt(v):
    v=Q(v); return str(v.numerator)+'/'+str(v.denominator)

def expected(source, instructions):
    cur=cp(source['result']['carry']['next_opening'])
    rr=source['request']['carry']['report_request']
    mapping={v['id']:v['accounts'][0] for v in rr['mapping']['lines']}
    traces=[]
    for item in instructions:
        before=cp(cur); amount=Q(item['amount'])
        assert 0<amount<-Q(cur['balances'][mapping['interest_payable']])
        assert amount<=Q(cur['balances'][mapping['cash']])
        journal={a:'0/1' for a in cur['accounts']}
        journal[mapping['cash']]=fmt(-amount)
        journal[mapping['interest_payable']]=fmt(amount)
        cur['balances']={a:fmt(Q(v)+Q(journal[a])) for a,v in cur['balances'].items()}
        cur['memory']['paid2']=fmt(Q(cur['memory']['paid2'])+amount)
        cur['memory']['phase']='partial2'
        cur['date']=item['date']; cur['seen'].append(item['id'])
        flow=dict(id=s.identity([item['id'],'late_coupon_payment']),
            entity=cur['context']['entity'],book=cur['context']['book'],
            currency=cur['context']['currency'],event_id=item['id'],date=item['date'],
            activity='operating',origin='late_coupon_payment',amount=fmt(-amount))
        cur['flows'].append(flow)
        traces.append(dict(before=before,after=cp(cur),journal=journal,flows=[flow]))
    return cur,traces

def verify(result,source,sid,selection,selected_id,instructions):
    assert s.identity(source)==sid and s.identity(selection)==selected_id
    assert result['profile']=='SelectedLatePartialCouponResult/1'
    assert result['source_carry_sha256']==sid and result['selection_sha256']==selected_id
    assert result['instructions']==instructions
    assert result['interpretation']=='explicit_new_method_no_retroactive_original_policy_success'
    for flag in s.FLAGS: assert result[flag] is False
    assert result['origin_archive']==source['result']['history_archive']
    assert result['origin_archive']['next_opening_sha256']==s.identity(selection['opening'])
    body=s.program(selection,instructions); actual=result['execution']
    current,trace=expected(source,instructions)
    assert actual['profile']==s.rt.PROFILE and actual['status']=='complete_provisional'
    assert actual['program_sha256']==s.identity(body)
    assert actual['current']==current and actual['opening']==selection['opening']
    assert actual['stop'] is None and actual['remaining_commands']==[]
    assert actual['reports']==[] and actual['archives']==[]
    assert len(actual['trace'])==len(trace)
    for flag in s.rt.FLAGS: assert actual[flag] is False
    for got,want,command in zip(actual['trace'],trace,body['commands']):
        assert got['command']==command
        assert got['before_sha256']==s.identity(want['before'])
        assert got['after_sha256']==s.identity(want['after'])
        assert got['opening_before_sha256']==got['opening_after_sha256']==s.identity(selection['opening'])
        assert got['observation'] is None and got['result']['status']=='proposed'
        for key in ('after','journal','flows'): assert got['result']['transition'][key]==want[key]
    assert result['report']==oracle.report_oracle(body,current)
    assert all(Q(v)==0 for v in result['report']['reconciliations'].values())
    assert result['report']['income']==dict(income='0/1',expenses='0/1',profit='0/1')
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120))
    attempt=sys.argv[1]; assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt); A.mkdir(exist_ok=False)
    start=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    checks=[]; controls=[]; cases=[]; pins={}
    def save(n,v): (A/n).write_text(json.dumps(v,indent=2)+'\n')
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v: raise AssertionError(n)
    def reject(n,fn):
        try: fn()
        except (ValueError,TypeError,KeyError,AssertionError) as e:
            controls.append(dict(name=n,reason=str(e))); ck('reject:'+n,True)
        else: ck('reject:'+n,False)
    old_native=prior.prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'coupon-carry-20261027/attempt-01'
        ck('upstream_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():
            ck('source:'+n,digest(R/n)==v); pins[n]=v
        sources=[Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(R)]
        for p in sources+list(B.glob('*.json'))+[H/n for n in ('partial.py','verify.py','contract.md','recovery-review.md')]+[R/'docs/plans/accounting-coupon-partial-settlement-20261027.md']:
            pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('partial.py','verify.py','contract.md','recovery-review.md'): (A/n).write_bytes((H/n).read_bytes())
        records=[v for v in json.loads((B/'cases.json').read_text()) if ':R6:draw:' in v['case']]
        ck('four_origins',len(records)==4)
        schedules=dict(single=[dict(id='late-coupon-1',date='2028-01-02',amount='85/16')],
            split=[dict(id='late-coupon-1',date='2028-01-02',amount='85/32'),dict(id='late-coupon-2',date='2028-01-03',amount='85/32')])
        save('inputs-and-expectations.json',dict(origins=[dict(case=v['case'],sha256=s.identity(v)) for v in records],schedules=schedules,final_cash='0/1',final_signed_payable='-1/16',paid2='85/16',income='0/1',source_file=str((B/'cases.json').relative_to(R))))
        prior.prior.native.Engine.apply=lambda *a,**k: (_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        for source in records:
            sid=s.identity(source); selection=s.select(source,sid); selected_id=s.identity(selection)
            for name,instructions in schedules.items():
                result=s.run(source,sid,selection,selected_id,instructions)
                ck(source['case']+':'+name,verify(result,source,sid,selection,selected_id,instructions))
                ck('source_and_selection_preserved',s.identity(source)==sid and s.identity(selection)==selected_id)
                ck('exact_final_amounts',result['execution']['current']['balances'][selection['opening']['cash_account']]=='0/1' and result['execution']['current']['memory']['paid2']=='85/16')
                cases.append(dict(case=source['case']+':'+name,source_carry_sha256=sid,selection=selection,selection_sha256=selected_id,instructions=instructions,result=result))
            a,b=cases[-2:]
            ck('same_balances_memory',a['result']['execution']['current']['balances']==b['result']['execution']['current']['balances'] and a['result']['execution']['current']['memory']==b['result']['execution']['current']['memory'])
            ck('distinct_dated_flows',a['result']['execution']['current']['flows']!=b['result']['execution']['current']['flows'])
        source=records[0]; sid=s.identity(source); base=cases[1]
        sel=base['selection']; selected_id=base['selection_sha256']; inst=base['instructions']; res=base['result']
        for name,change in [('stale_origin',lambda z:z['result']['carry']['next_opening']['memory'].update(used=False)),('lost_origin_refusal',lambda z:z['result']['history_archive'].update(refusal=None))]:
            bad=cp(source); change(bad); reject(name,lambda v=bad:s.run(v,sid,sel,selected_id,inst))
        bad=cp(sel); bad['opening']['memory']['action2']='pay'
        reject('stale_selection',lambda:s.run(source,sid,bad,selected_id,inst))
        reject('reidentified_changed_selection',lambda:s.run(source,sid,bad,s.identity(bad),inst))
        badinstructions=[('early_date',[dict(id='early',date='2027-12-31',amount='1/1')],0),
            ('unaffordable',[dict(id='excess',date='2028-01-02',amount='43/8')],0),
            ('over_claim',[dict(id='excess',date='2028-01-02',amount='6/1')],0),
            ('zero',[dict(id='zero',date='2028-01-02',amount='0/1')],0),
            ('negative',[dict(id='negative',date='2028-01-02',amount='-1/1')],0),
            ('duplicate_id',[inst[0],{**inst[1],'id':inst[0]['id']}],1),
            ('backward_date',[inst[0],{**inst[1],'date':'2028-01-01'}],1),
            ('old_event_id',[{**inst[0],'id':'draw1'}],0)]
        for name,instructions,count in badinstructions:
            out=s.run(source,sid,sel,selected_id,instructions)['execution']
            ck('refuse:'+name,out['status'] in ('invalid','stopped_provisional'))
            if 'current' in out:
                want,_=expected(source,instructions[:count]); ck('refusal_state:'+name,out['current']==want and len(out['trace'])==count)
                ck('refusal_commands:'+name,out['remaining_commands']==s.program(sel,instructions)['commands'][count:])
            controls.append(dict(name=name,status=out['status'],reason=out.get('reason',out.get('stop',{}).get('reason'))))
        mutations=[('noncumulative_paid2',lambda z:z['execution']['current']['memory'].update(paid2='85/32')),
            ('reset_used',lambda z:z['execution']['current']['memory'].update(used=False)),
            ('rewrite_action',lambda z:z['execution']['current']['memory'].update(action2='pay')),
            ('wrong_activity',lambda z:z['execution']['current']['flows'][0].update(activity='financing')),
            ('missing_refusal',lambda z:z['origin_archive'].update(refusal=None)),
            ('false_admission',lambda z:z.update(accounting_admission=True)),
            ('wrong_report',lambda z:z['report']['income'].update(expenses='85/16')),
            ('wrong_journal',lambda z:z['execution']['trace'][0]['result']['transition']['journal'].update({sel['opening']['cash_account']:'0/1'}))]
        for name,change in mutations:
            bad=cp(res);change(bad);reject(name,lambda v=bad:verify(v,source,sid,sel,selected_id,inst))
        for n,v in pins.items(): ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='selected partial coupon only; original refusal retained')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks)); save('failure.json',summary)
    finally:
        prior.prior.native.Engine.apply=old_native
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact conformance',data_version='source-lock.json',plan='docs/plans/accounting-coupon-partial-settlement-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
