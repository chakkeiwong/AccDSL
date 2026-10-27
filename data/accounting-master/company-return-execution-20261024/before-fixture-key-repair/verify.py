"""Deterministic reference conformance; preserve failed checks before repair."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json,os,platform,subprocess,sys,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
from retained_execution_context import load,event_for,adapter_for,AUTHOR
from native_returns import initialize,propose,apply,invariant,Rejected,q,fmt,canon,digest,INCOME,FINDINGS
from native_reports import report,carry

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def conformance():
    author,packet,item,financial=load();initial=item('opening');checks=[];adverse={};trace=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    def rejected(name,fn,status='invalid'):
        try:fn();result={'status':'accepted'}
        except Rejected as exc:result={'status':exc.status,'reason':exc.reason}
        except Exception as exc:result={'status':'unexpected_exception','reason':type(exc).__name__+':'+str(exc)}
        adverse[name]=result;check(name,result['status']==status)
    opening=initialize(author,initial['books']['P'],initial['compound']['prior_interest_expensed'])
    current=deepcopy(opening);retained=deepcopy(initial);states={'opening':deepcopy(opening)};proposals={};events={};adapters={}
    for tr in packet['transitions']:
        key=tr['id'].removesuffix('.commit');original=item('event.'+key);event=event_for(key,original,author)
        events[key]=event;adapter=adapter_for(retained,financial) if event['kind']=='surrounding' else None;adapters[key]=adapter
        before=canon(current);proposal=propose(current,event,adapter);new=apply(current,event,proposal,adapter)
        expected=item('state.'+key);expected_proposal=item('proposal.'+key)
        check(key+'_proposal_input_unchanged',canon(current)==before)
        check(key+'_all_P_balances',{k:fmt(v) for k,v in expected['books']['P'].items()}==new['balances'])
        check(key+'_whole_P_journal',{k:fmt(v) for k,v in expected_proposal['journals']['P'].items()}==proposal['journal'])
        expected_flows=[{**f,'amount':fmt(f['amount']),'date':event['date'],'event_id':event['id']} for f in expected_proposal['cash'] if f['entity']=='P']
        check(key+'_gross_P_cash',expected_flows==proposal['flows'])
        check(key+'_refund_memory',q(new['component']['refund'])==Q(expected['returns']['refund']))
        check(key+'_recovery_memory',q(new['component']['recovery'])==Q(expected['returns']['recovery']))
        check(key+'_settled_memory',new['component']['settled']==expected['returns']['settled'])
        check(key+'_recovered_lot_allocation',sum(q(l['carrying']) for l in new['lots'].values())==Q(expected['return_inventory']))
        check(key+'_uncommitted_only',proposal['committed'] is False)
        # Reuse retained methods only for the surrounding trace and independent
        # comparator; never adopt saved after-state into the native reference.
        computed,_,_=financial.derive(retained,original,lambda ok,why,*status:(_ for _ in ()).throw(ValueError(why)) if not ok else None)
        check(key+'_retained_full_state_replayed',canon(computed)==canon(expected))
        retained=computed;current=new;states[key]=deepcopy(new);proposals[key]=proposal
        trace.append({'id':key,'event':event,'proposal':proposal})
    annual=report(opening,current);expected=item('report.annual')['legal']['P']
    check('annual_profit',q(annual['income']['profit'])==Q(expected['profit'])==Q(99,2))
    check('annual_equity',q(annual['balance_sheet']['equity'])==Q(expected['equity'])==Q(1343,2))
    check('annual_cash',q(annual['closing_cash'])==Q(expected['cash'])==Q(983,2))
    check('annual_current_tax',q(annual['income']['current_tax'])==Q(21,2))
    check('annual_deferred_tax',q(annual['income']['deferred_tax'])==6)
    check('first_current_tax',q(proposals['tax-h1']['journal']['current_tax'])==8)
    check('second_current_tax_increment',q(proposals['tax-h2']['journal']['current_tax'])==Q(5,2))
    check('operating_cash',q(annual['cash_flows']['operating']['net'])==Q(203,2))
    check('investing_cash',q(annual['cash_flows']['investing']['net'])==-20)
    check('financing_cash',q(annual['cash_flows']['financing']['net'])==-90)
    check('opening_interest_bridge',q(annual['indirect_operating']['opening_interest_paid'])==-10)
    check('indirect_equals_direct',sum(q(v) for v in annual['indirect_operating'].values())==Q(203,2))
    next_open=carry(opening,current,'2027-01-01')
    check('carry_all_income_reset',all(q(next_open['balances'][k])==0 for k in INCOME))
    check('carry_retained_transfer',q(next_open['balances']['retained'])==Q(-123,2))
    check('carry_cash_unchanged',next_open['balances']['cash']==current['balances']['cash'])
    check('carry_lifetime_events',next_open['seen']==current['seen'])
    check('carry_lots_history',next_open['lots']==current['lots'])
    check('carry_tax_event_history',next_open['tax_adjustments']==current['tax_adjustments'])
    check('carry_period_cash_reset',not next_open['flows'])
    check('carry_source_preserved',next_open['source']==current['source'])
    check('carry_conditional_not_observed',next_open['conditional'] is True)
    tax_next={**deepcopy(events['tax-h2']),'id':'tax-next','date':'2026-12-31','start':'2026-01-01','end_exclusive':'2027-01-01'}
    next_proposal=propose(next_open,tax_next);next_close=apply(next_open,tax_next,next_proposal)
    check('next_year_old_adjustment_not_reapplied',q(next_proposal['journal']['current_tax'])==0)
    check('next_year_no_deferred_repeat',q(next_proposal['journal']['deferred_tax'])==0)
    next_report=report(next_open,next_close)
    check('next_year_no_activity_profit',q(next_report['income']['profit'])==0)
    check('next_year_no_activity_cash',q(next_report['cash_flows']['operating']['net'])==0)
    # Transition proposals are untrusted; applying always recomputes semantics.
    pre=states['redeem'];settle=events['returns'];good=proposals['returns'];original=canon(pre)
    bad=deepcopy(good);bad['journal']['cash']='-47/1'
    rejected('changed_journal_refused',lambda:apply(pre,settle,bad))
    bad2=deepcopy(good);bad2['after']['balances']['cash']='353/1'
    rejected('changed_after_state_refused',lambda:apply(pre,settle,bad2))
    bad3=deepcopy(good);bad3['method_bundle']='attacker'
    rejected('changed_method_identity_refused',lambda:apply(pre,settle,bad3))
    changed=deepcopy(settle);changed['refund_cash']='41/1'
    rejected('changed_event_fact_refused',lambda:apply(pre,changed,good))
    rejected('stale_proposal_refused',lambda:apply(states['returns'],settle,good))
    rejected('second_settlement_refused',lambda:propose(states['returns'],{**settle,'id':'new-settlement'}))
    rejected('disposed_lot_refused',lambda:propose(states['recovered-sale'],{**events['recovered-sale'],'id':'new-sale'}))
    rejected('old_event_id_after_carry',lambda:propose(next_open,{**events['recovered-sale'],'date':'2026-09-01'}))
    for k in ['all_rights_closed','handling_is_selling_cost']:
        for value,status in [('unknown','unresolved'),(False,'unsupported'),(0,'invalid')]:
            e=deepcopy(settle);e[k]=value
            rejected(k+'_'+str(value),lambda e=e:propose(pre,e),status)
    weak=deepcopy(pre);weak['balances']['cash']='1/1';weak['balances']['capital']=fmt(q(weak['balances']['capital'])+q(pre['balances']['cash'])-1)
    before=canon(weak);rejected('cash_shortfall_is_economic_failure',lambda:propose(weak,settle),'funding_failure')
    check('cash_failure_atomic',canon(weak)==before)
    check('all_rejected_settlements_atomic',canon(pre)==original)
    for k in FINDINGS:
        for value,status in [('unknown','unresolved'),(False,'unsupported')]:
            s=deepcopy(states['internal-settle']);s['tax_premises'][k]=value;before=canon(s)
            rejected('tax_'+k+'_'+str(value),lambda s=s:propose(s,events['tax-h1']),status)
            check('tax_'+k+'_'+str(value)+'_atomic',canon(s)==before)
    rejected('no_annual_report_before_tax',lambda:report(opening,states['depreciation-h2']),'unresolved')
    rejected('no_carry_before_tax',lambda:carry(opening,states['depreciation-h2'],'2027-01-01'),'unresolved')
    rejected('wrong_tax_start',lambda:propose(states['depreciation-h2'],{**events['tax-h2'],'start':'2025-01-01'}))
    rejected('wrong_tax_cutoff',lambda:propose(states['depreciation-h2'],{**events['tax-h2'],'date':'2025-12-30'}))
    inconsistent=deepcopy(pre);inconsistent['lots']['fake']={'id':'fake','component_id':pre['component']['id'],'units':'1/1','carrying':'1/1','tax_base':'1/1','acquired':'2025-01-01','disposed':False}
    rejected('extra_inventory_allocation_refused',lambda:invariant(inconsistent))
    # Imported unchanged legacy authoring checks and all locked sources are
    # verified, without recording or rewriting the predecessor evidence.
    import importlib.util
    spec=importlib.util.spec_from_file_location('return_schema_readonly_verification',AUTHOR/'verify.py')
    legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    schema_result,*_=legacy.conformance();check('predecessor_107_checks',schema_result==json.loads((AUTHOR/'checks.json').read_text()))
    m=json.loads((AUTHOR/'manifest.json').read_text());locks={}
    for key in ['inputs','implementation','outputs']:locks.update(m[key])
    for p in [AUTHOR/'manifest.json',ROOT/'docs/plans/accounting-company-return-execution-20261024.md']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():check('protected_'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'adverse':adverse}, {'trace':trace,'annual':annual,'next_opening':next_open,'next_year_report':next_report},locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for n,h in m[group].items():assert sha(ROOT/n)==h,n
    result,trace,locks=conformance();observation={'mode':mode,'passed':result['passed'],
        'checks':len(result['checks']),'failed':[c['name'] for c in result['checks'] if not c['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not result['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        dump(HERE/'checks.json',result);dump(HERE/'trace.json',trace);dump(HERE/'source-lock.json',locks)
        outputs={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'checks.json',HERE/'trace.json',HERE/'source-lock.json']}
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; exact finite reference',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic',
            'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':outputs,'plan':'docs/plans/accounting-company-return-execution-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert canon(result)==canon(json.loads((HERE/'checks.json').read_text()))
        assert canon(trace)==canon(json.loads((HERE/'trace.json').read_text()))
    print(json.dumps(observation));return 0 if result['passed'] else 1
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as exc:
        p=HERE/('failure-'+str(time.time_ns())+'.txt');p.write_text(traceback.format_exc())
        print(json.dumps({'status':'failed','error':type(exc).__name__+': '+str(exc)[:350],'diagnostic':str(p.relative_to(ROOT))}));sys.exit(1)
