"""Check selected coupon carry against independently authored complete states."""
from pathlib import Path
from copy import deepcopy as cp
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone,date,timedelta
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback
import selected as s
H=Path(__file__).resolve().parent;R=H.parents[2]
spec=importlib.util.spec_from_file_location('coupon_retained_record_checker',H.parent/'refused-payment-reporting-20261027/verify.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
oracle=prior.oracle
def digest(p):return sha256(p.read_bytes()).hexdigest()
def fmt(v):v=Q(v);return str(v.numerator)+'/'+str(v.denominator)

def verify(result,record,rid,req):
    assert s.identity(record)==rid and result['record_sha256']==rid and result['request_sha256']==s.identity(req)
    assert result['profile']=='SelectedUnpaidCouponCarry/1'
    for flag in s.FLAGS:assert result[flag] is False
    book=record['execution']['current'];body=record['program'];arg=req['carry'];end=book['period']['end_exclusive']
    if date.fromisoformat(book['date'])!=date.fromisoformat(end)-timedelta(days=1):
        assert result['status']=='unassessed_not_period_end' and result['carry'] is None;return True
    assert result['status']=='proposed_selected_coupon_carry';got=result['carry']
    journal={a:'0/1' for a in book['accounts']};net=Q(0)
    for a,row in book['accounts'].items():
        if row['classification'] in ('income','expense'):
            v=Q(book['balances'][a]);journal[a]=fmt(-v);net+=v
    journal[record['mapping']['capital']]=fmt(net)
    closed=cp(book);closed['balances']={a:fmt(Q(v)+Q(journal[a])) for a,v in book['balances'].items()};closed['seen'].append(arg['close_id'])
    opening=cp(closed);opening.update(period=dict(start=end,end_exclusive=arg['next_end_exclusive']),date=end,flows=[])
    assert got['journal']==journal and got['closed_book']==closed and got['next_opening']==opening
    assert got['cash_flows']==[] and got['report']==record['report']
    assert got['archive']==dict(profile='CompanyBookCarryArchive/1',context=book['context'],period=book['period'],close_id=arg['close_id'],
        closing_before_sha256=s.identity(book),closed_book_sha256=s.identity(closed),report_sha256=s.identity(record['report']),
        next_opening_sha256=s.identity(opening),memory_policies_sha256=s.identity(arg['memory_policies']),scope='Provisional recorded-balance carry; not admitted fiscal completion')
    assert result['history_archive']==dict(profile='CouponRefusalCarryArchive/1',source_record_sha256=rid,refusal=record['execution']['stop'],remaining_commands=record['execution']['remaining_commands'],prior_status=record['execution']['status'],prior_current_sha256=s.identity(book),prior_report_sha256=s.identity(record['report']),next_opening_sha256=s.identity(opening),carry_archive_sha256=s.identity(got['archive']),history_scope='same_verified_prefix_no_later_settlement_inferred')
    next_body=cp(body);next_body['opening']=opening
    assert result['opening_report']==oracle.report_oracle(next_body,opening)
    assert all(Q(v)==0 for v in result['opening_report']['reconciliations'].values())
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];cases=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def reject_result(n,fn):
        try:fn()
        except (ValueError,TypeError,KeyError,AssertionError) as err:controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    old_native=prior.native.Engine.apply
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'refused-payment-reporting-20261027/attempt-02'
        ck('upstream_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        sources=[Path(mod.__file__).resolve() for mod in list(sys.modules.values()) if getattr(mod,'__file__',None) and Path(mod.__file__).resolve().is_relative_to(R)]
        for p in sources+list(B.glob('*.json'))+[H/'selected.py',H/'verify.py',H/'contract.md',R/'docs/plans/accounting-coupon-carry-20261027.md']:pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('selected.py','verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        records=json.loads((B/'cases.json').read_text());plans=json.loads((B/'inputs-and-expectations.json').read_text());planmap={v['case']:v for v in plans}
        save('inputs-and-expectations.json',[dict(case=r['case'],source_record_sha256=s.identity(r),source_file=str((B/'cases.json').relative_to(R)),expected='unassessed_not_period_end' if ':pay:' in r['case'] else 'proposed_selected_coupon_carry',close_id='coupon-close-2027',next_end_exclusive='2029-01-01') for r in records])
        prior.native.Engine.apply=lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('native fallback forbidden'))
        for record in records:
            name=record['case'];rid=s.identity(record)
            ck(name+':upstream_complete_check',prior.assert_record(record,planmap[name]))
            req=s.request(record,rid,'coupon-close-2027','2029-01-01');result=s.propose(record,rid,req)
            ck(name+':independent_carry',verify(result,record,rid,req))
            ck(name+':input_preserved',s.identity(record)==rid)
            cases.append(dict(case=name,source_file=str((B/'cases.json').relative_to(R)),source_record_sha256=rid,request=req,result=result))
        ck('eligible_count',sum(v['result']['status']=='proposed_selected_coupon_carry' for v in cases)==6)
        ck('nonfinal_count',sum(v['result']['status']=='unassessed_not_period_end' for v in cases)==4)
        base=next(v for v in cases if v['case']=='alpha:R6:draw:pay');record=next(v for v in records if v['case']==base['case']);rid=base['source_record_sha256'];req=base['request'];res=base['result'];opening=res['carry']['next_opening']
        ck('unpaid_carry',opening['balances']['cash']=='85/16' and opening['balances']['interest_payable']=='-43/8' and opening['memory']['paid2']=='0/1')
        ck('used_right_carry',opening['memory']['used'] is True and opening['balances']['facility_debt']=='0/1')
        ck('loss_closed_to_equity',opening['balances']['capital']=='89/16' and all(opening['balances'][k]=='0/1' for k in ('income','interest_expense','fee_expense')))
        ck('prior_refusal_retained',res['history_archive']['refusal']==record['execution']['stop'])
        def refuse_request(name,mutate):
            bad=cp(req);mutate(bad);answer=s.propose(record,rid,bad)
            ck('request:'+name,answer['status']=='invalid' and answer['carry'] is None);controls.append(dict(name=name,reason=answer['reason']))
        refuse_request('drop_policy',lambda z:z['carry']['memory_policies'].pop('/used'))
        refuse_request('reset_used',lambda z:z['carry']['memory_policies'].update({'/used':dict(kind='reset',type=opening['memory_types']['/used'],value=False,provenance='wrong reset')}))
        refuse_request('reset_due',lambda z:z['carry']['memory_policies'].update({'/due2':dict(kind='reset',type=opening['memory_types']['/due2'],value='0/1',provenance='wrong reset')}))
        refuse_request('stale_report',lambda z:z['carry'].update(expected_report_sha256='0'*64))
        refuse_request('wrong_date',lambda z:z['carry']['report_request']['closing'].update(date='2028-01-01'))
        refuse_request('wrong_equity_mapping',lambda z:z['carry'].update(retained_account='cash'))
        refuse_request('repeated_close',lambda z:z['carry'].update(close_id='draw1'))
        refuse_request('wrong_next_boundary',lambda z:z['carry'].update(next_end_exclusive='2028-01-01'))
        bad=cp(record);bad['execution']['current']['memory']['paid2']='43/8'
        ck('stale_record_rejected',s.propose(bad,rid,req)['status']=='invalid');controls.append(dict(name='stale_record_rejected'))
        generic=cp(req['carry']);generic['memory_policies']['/used']=dict(kind='reset',type=opening['memory_types']['/used'],value=False,provenance='Adverse control of generic typed carry')
        proposal=s.carry.propose(generic);ck('generic_reset_passes_without_selected_semantics',proposal['status']=='proposed' and proposal['next_opening']['memory']['used'] is False)
        save('generic-reset-control.json',dict(status=proposal['status'],next_memory=proposal.get('next_opening',{}).get('memory'),interpretation='Generic typed carry permits this reset; selected coupon preservation rejects it'))
        for name,change in [('erase_payable',lambda z:z['carry']['next_opening']['balances'].update(interest_payable='0/1')),
                            ('erase_memory',lambda z:z['carry']['next_opening']['memory'].update(used=False)),
                            ('drop_refusal',lambda z:z['history_archive'].update(refusal=None)),
                            ('drop_remaining',lambda z:z['history_archive'].update(remaining_commands=[])),
                            ('invent_cash_flow',lambda z:z['carry']['cash_flows'].append({'amount':'-43/8'})),
                            ('false_admission',lambda z:z.update(fiscal_admission=True)),
                            ('wrong_opening_report',lambda z:z['opening_report']['balance_sheet'].update(total_liabilities='100/1'))]:
            bad=cp(res);change(bad);reject_result(name,lambda v=bad:verify(v,record,rid,req))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),carried_cases=6,nonfinal_cases=4,assertions=len(checks),controls=len(controls),protected_files=len(pins),scope='selected unpaid-coupon carry; no later settlement inferred')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        prior.native.Engine.apply=old_native
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact conformance',data_version='source-lock.json',plan='docs/plans/accounting-coupon-carry-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
