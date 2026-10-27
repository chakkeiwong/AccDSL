"""Bounded paid/unpaid financing carry on two independent account charts."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,platform,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'financing-carry-20261026'))
import selected_carry as s
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
E01=HERE.parent/'gap-program-20261026';OUT=HERE/'attempt-01'
sys.path.insert(0,str(HERE.parent/'financing-remedy-freshness-20261026'))
spec=importlib.util.spec_from_file_location('carry_remedy_state',HERE.parent/'financing-remedy-freshness-20261026/remedy_execution.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
spec=importlib.util.spec_from_file_location('carry_e01',E01/'settlement_cases.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
import company_method_clock_v1 as clock
checks=[];controls=[];cases=[]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def check(n,a,b=True):
    checks.append(dict(id=n,passed=a==b,actual_sha256=s.core.digest(a),expected_sha256=s.core.digest(b)))
    if a!=b:
        save('failed.json',dict(id=n,actual=a,expected=b));raise AssertionError(n)
def selected_call(k,request):
    h=s.core.digest(k);return s.propose(k,request,h,s.make_call(k,request,h))
def refusal(n,value,status='invalid'):
    check(n+'.status',value['status'],status);check(n+'.no_accepted_opening','next_opening' not in value)
    controls.append(dict(case=n,result=value))
def remedy(k,book,event,schemas):
    h=s.core.digest(k);return r.execute(k,book,event,schemas,h,r.make_call(k,book,event,schemas,h))

def main():
    assert not OUT.exists(),'attempt_exists';assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1'
    OUT.mkdir();started=time.monotonic()
    pins=read(HERE.parent/'financing-remedy-freshness-20261026/attempt-02/source-lock.json')
    pins.update(read(HERE.parent/'financing-carry-20261026/attempt-02/source-lock.json'))
    for n,h in pins.items():assert sha(ROOT/n)==h,n
    source=[Path(m.__file__).resolve() for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    source += [HERE/'audit.md',ROOT/'docs/plans/accounting-financing-carry-freshness-20261026.md',
               HERE.parent/'financing-remedy-freshness-20261026/result.md',
               HERE.parent/'financing-carry-20261026/result.md',HERE.parent/'financing-carry-20261026/attempt-02/checks.json']
    pins.update({str(p.relative_to(ROOT)):sha(p) for p in source if p.is_file()})
    save('source-lock.json',pins)
    for n in ['verify.py','audit.md']:(OUT/n).write_bytes((HERE/n).read_bytes())
    frozen=read(E01/'settlement-cases.json');facts={x['id']:x['facts'] for x in read(E01/'contract-condition-results.json')['cases']}
    original=e.native.Engine.apply;e.native.Engine.apply=lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('native fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            old=next(x for x in frozen if x['case']==owner+'.late')
            for path in ['paid','unpaid']:
                tag=owner+'.'+path;program,mapping=e.make('late',owner)
                check(tag+'.frozen_program',program,old['program'])
                initial=dict(series='hypothetical-'+owner,clause_status='unknown',clause_date='unknown',
                  clause_kind='unknown',observed_economy_sha256='unknown',observed_evidence_revision='unknown',acceleration_status='unknown',last_action='supplied_initial',evidence_digest='none')
                opening,schemas,extension=r.extended_state(program['opening'],program['schemas'],initial,
                  'Explicit synthetic fiscal opening; contractual findings unknown until supplied')
                book=deepcopy(opening);adapted=deepcopy(program);adapted['opening']=opening;adapted['schemas']=schemas
                for key,entry in adapted['registry']['entries'].items():
                    baseline=program['registry']['entries'][key]['method'];wanted=deepcopy(baseline)
                    wanted['memory']['definition']['state_schema']=opening['memory_schema']
                    entry['method']=wanted;entry['method_sha256']=s.core.digest(wanted)
                    entry['schemas'].update({opening['memory_schema']:schemas[opening['memory_schema']]})
                    check(tag+'.adaptation.'+key,sorted(k for k in baseline if baseline[k]!=wanted[k]),['memory'])
                financial=s.financial.make_contract(adapted,mapping)
                remedy_selection=r.make_selection(opening,schemas,initial['series'])
                trace=[]
                def apply_financing(index):
                    nonlocal book
                    cmd=adapted['commands'][index];entry=adapted['registry']['entries'][cmd['method_key']]
                    request=dict(profile=s.carry.engine.PROFILE,expected_state_sha256=s.core.digest(book),
                      expected_method_sha256=entry['method_sha256'],method=entry['method'],event=clock.event_for(entry,cmd['event']),schemas=schemas)
                    before=deepcopy(book);got=s.carry.engine.propose(book,request)
                    check(tag+'.financial.'+str(index)+'.status',got['status'],'proposed')
                    expected=deepcopy(before);oracle=old['independent_prefixes'][index]
                    expected['balances']=deepcopy(oracle['after']['balances']);expected['memory']['debt_terms']=deepcopy(oracle['after']['memory']['debt_terms'])
                    expected['date']=cmd['event']['date'];expected['seen'].append(cmd['event']['id']);expected['flows'].extend(deepcopy(oracle['flows']))
                    for part,want in [('after',expected),('journal',oracle['journal']),('flows',oracle['flows'])]:
                        check(tag+'.financial.'+str(index)+'.'+part,got[part],want)
                    relation=s.financial.transition(financial,cmd['method_key'],before,cmd['event'],got['after'],schemas)
                    check(tag+'.financial.'+str(index)+'.relation',relation['status'],'requirements_satisfied')
                    trace.append(dict(kind='financial',request=request,result=got,relation=relation));book=deepcopy(got['after'])
                def apply_remedy(identity,method,case,date,changes):
                    nonlocal book
                    ev=dict(id=tag+'.'+identity,date=date,series=initial['series'],method=method,evidence_revision='synthetic-view-1',
                      facts=deepcopy(facts[case]),provenance='Explicit hypothetical conditional finding under the selected synthetic series')
                    before=deepcopy(book);got=remedy(remedy_selection,book,ev,schemas)
                    check(tag+'.remedy.'+identity+'.status',got['status'],'proposed_conditional_status')
                    expected=deepcopy(before);expected['date']=date;expected['seen'].append(ev['id'])
                    expected['memory']['contract_status'].update(last_action=method,evidence_digest=s.core.digest(ev),**changes)
                    if method=='event_clause':
                        projected=deepcopy(before);projected.pop('date');projected.pop('seen');projected['memory'].pop('contract_status')
                        projected['memory_types']={k:v for k,v in before['memory_types'].items() if not k.startswith('/contract_status/')}
                        expected['memory']['contract_status'].update(clause_date=date,clause_kind=ev['facts']['kind'],
                          observed_economy_sha256=s.core.digest(projected),observed_evidence_revision=ev['evidence_revision'])
                    check(tag+'.remedy.'+identity+'.full_after',got['after'],expected)
                    check(tag+'.remedy.'+identity+'.journal',got['transition']['journal'],{k:'0/1' for k in before['accounts']})
                    check(tag+'.remedy.'+identity+'.flows',got['transition']['flows'],[])
                    trace.append(dict(kind='remedy',event=ev,result=got));book=deepcopy(got['after'])
                for index in range(4):apply_financing(index)
                apply_remedy('clause','event_clause','principal_unpaid_due','2027-07-02',dict(clause_status='satisfied'))
                apply_remedy('accelerate','new_acceleration','nonbankruptcy_declared','2027-07-02',dict(acceleration_status='satisfied'))
                if path=='paid':
                    apply_financing(4)
                    apply_remedy('paid','event_clause','principal_paid','2027-07-03',dict(clause_status='not_satisfied'))
                    apply_remedy('rescind','after_rescission','rescission_complete','2027-07-03',dict(acceleration_status='not_satisfied'))
                closing=deepcopy(book);closing['date']='2027-12-31'
                report_command=program['commands'][-1]
                report_request=s.carry.reports.request(opening,closing,schemas,program['mapping'],
                  report_command['equity_movements'],report_command['notes'])
                report=s.carry.reports.report(report_request);check(tag+'.report',report['status'],'reported')
                for n,a,w in [('assets',report['balance_sheet']['total_assets'],'100/1' if path=='paid' else '140/1'),
                  ('liabilities',report['balance_sheet']['total_liabilities'],'0/1' if path=='paid' else '40/1'),
                  ('equity',report['equity']['closing'],'100/1'),('profit',report['income']['profit'],'-20/1'),
                  ('cash_flow',report['cash_flows']['activities']['financing']['net'],'-60/1' if path=='paid' else '-20/1')]:check(tag+'.report.'+n,a,w)
                request=s.carry.request(report_request,'close.'+tag,mapping['retained'],'2029-01-01',s.policies(closing))
                selected=s.selection(financial,schemas,program['mapping'],mapping['retained'])
                untouched=deepcopy(request);got=selected_call(selected,request)
                check(tag+'.carry.status',got['status'],'proposed_selected_carry');check(tag+'.request_preserved',request,untouched)
                expected_closed=deepcopy(closing);expected_closed['balances'][mapping['interest']]='0/1'
                expected_closed['balances'][mapping['retained']]='20/1';expected_closed['seen'].append('close.'+tag)
                expected=deepcopy(expected_closed);expected.update(period=dict(start='2028-01-01',end_exclusive='2029-01-01'),date='2028-01-01',flows=[])
                journal={k:'0/1' for k in closing['accounts']};journal[mapping['interest']]='-20/1';journal[mapping['retained']]='20/1'
                raw=got['diagnostic_carry']
                for n,a,w in [('closed',raw['closed_book'],expected_closed),('opening',got['next_opening'],expected),
                  ('journal',raw['journal'],journal),('cash_flows',raw['cash_flows'],[]),('report',raw['report'],report),
                  ('memory',expected['memory'],closing['memory']),('archived_flows',raw['closed_book']['flows'],closing['flows'])]:check(tag+'.carry.'+n,a,w)
                check(tag+'.carry.archive',raw['archive']['next_opening_sha256'],s.core.digest(expected))
                check(tag+'.carry.flags',all(got[k] is False for k in s.FLAGS))
                check(tag+'.carry.economic_state_changes',r.economic_digest(closing)!=r.economic_digest(expected))
                stale_event=dict(id='after_carry.'+tag,date='2028-01-01',series=initial['series'],method='new_acceleration',evidence_revision='synthetic-view-1',
                  facts=deepcopy(facts['nonbankruptcy_declared'] if path=='unpaid' else facts['acceleration_event_cured']),provenance='Supplied facts cannot refresh the stored clause observation')
                stale=remedy(remedy_selection,expected,stale_event,schemas)
                check(tag+'.stale_remedy',stale['status'],'unresolved');check(tag+'.stale_no_after','after' not in stale)
                cases.append(dict(case=tag,program=adapted,financial=financial,extension=extension,remedy_selection=remedy_selection,
                  trace=trace,request=request,selection=selected,result=got,expected=expected,stale_event=stale_event,stale_result=stale))
        run_controls(cases)
        for n,h in pins.items():check('protected.'+n,sha(ROOT/n),h)
        save('cases.json',cases);save('controls.json',controls)
        summary=dict(passed=True,cases=len(cases),prefix_transitions=sum(len(x['trace']) for x in cases),controls=len(controls),assertions=len(checks),protected_files=len(pins))
        save('checks.json',dict(**summary,checks=checks))
        save('run-manifest.json',dict(**summary,command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/financing-carry-freshness-20261026/verify.py',
          git_commit='unusable repository marker; preserved unchanged',environment=dict(python=platform.python_version(),platform=platform.platform()),
          cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,
          data_version=sha(E01/'settlement-cases.json'),plan='docs/plans/accounting-financing-carry-freshness-20261026.md',
          result='data/accounting-master/financing-carry-freshness-20261026/result.md',artifact_paths=['cases.json','controls.json','checks.json','source-lock.json'],
          timestamp_utc=datetime.now(timezone.utc).isoformat()))
        print(json.dumps(summary))
    finally:e.native.Engine.apply=original

def run_controls(cases):
    paid=cases[0];unpaid=cases[1];request=paid['request'];selected=paid['selection']
    def mutate(name,change):
        candidate=deepcopy(request);change(candidate)
        refusal(name,selected_call(selected,candidate))
        return candidate
    def reset(body,pointer,value):
        typ=body['report_request']['closing']['memory_types'][pointer]
        body['memory_policies'][pointer]=dict(kind='reset',type=deepcopy(typ),value=value,
          provenance='Deliberate adverse policy; not the selected financing carry')
    for name,pointer,value in [('lost_miss','/debt_terms/missed_amount','0/1'),
      ('lost_shares','/debt_terms/new_shares','0/1'),('retimed_clause','/contract_status/clause_date','2028-01-01'),
      ('invented_freshness','/contract_status/observed_economy_sha256',r.economic_digest(paid['expected']))]:
        candidate=mutate(name,lambda b,p=pointer,v=value:reset(b,p,v))
        generic=s.carry.propose(candidate)
        check(name+'.generic_allows_typed_reset',generic['status'],'proposed')
        controls[-1]['generic_discriminator']=generic
    mutate('missing_leaf_policy',lambda b:b['memory_policies'].pop('/debt_terms/missed_amount'))
    mutate('extra_leaf_policy',lambda b:b['memory_policies'].update({'/invented':dict(kind='preserve',provenance='Adverse extra leaf')}))
    mutate('blank_policy_provenance',lambda b:b['memory_policies']['/debt_terms/missed_amount'].update(provenance=' '))
    mutate('stale_report',lambda b:b.update(expected_report_sha256='0'*64))
    mutate('wrong_retained_role',lambda b:b.update(retained_account=b['report_request']['closing']['cash_account']))
    mutate('nonpositive_next_period',lambda b:b.update(next_end_exclusive='2028-01-01'))
    candidate=deepcopy(request);candidate['report_request']['closing']['date']='2027-12-30'
    candidate['report_request']['expected_closing_sha256']=s.core.digest(candidate['report_request']['closing'])
    candidate['expected_report_sha256']=s.core.digest(s.carry.reports.report(candidate['report_request']))
    refusal('not_final_day',selected_call(selected,candidate))
    candidate=deepcopy(request);candidate['report_request']['mapping']['lines'][0]['label']='Changed mapping'
    candidate['report_request']['expected_mapping_sha256']=s.core.digest(candidate['report_request']['mapping'])
    refusal('unselected_report_mapping',selected_call(selected,candidate))
    h='0'*64;refusal('unreviewed_carry',s.propose(selected,request,h,s.make_call(selected,request,h)))
    call=s.make_call(selected,request,s.core.digest(selected));candidate=deepcopy(request);candidate['close_id']='changed.close'
    refusal('stale_carry_call',s.propose(selected,candidate,s.core.digest(selected),call))

    # A type-correct unpaid-claim reset is still refused before invoking carry.
    candidate=deepcopy(unpaid['request'])
    reset(candidate,'/debt_terms/outstanding','0/1');reset(candidate,'/debt_terms/arrears','0/1')
    refusal('unpaid_obligation_reset',selected_call(unpaid['selection'],candidate))
    raw=s.carry.propose(candidate);check('unpaid_obligation_reset.generic_proposes',raw['status'],'proposed')
    check('unpaid_obligation_reset.post_snapshot_refuses',s.financial.snapshot(unpaid['financial'],raw['next_opening'],candidate['report_request']['schemas'])['status'],'invalid')
    controls[-1]['generic_discriminator']=raw

    # Continue from the actual carried unpaid opening: observe, settle, report.
    for case in [c for c in cases if c['case'].endswith('.unpaid')]:
        tag=case['case'];book=deepcopy(case['result']['next_opening']);schemas=case['request']['report_request']['schemas']
        k=case['remedy_selection'];series=book['memory']['contract_status']['series']
        ev=dict(id='renew.'+tag,date='2028-01-01',series=series,method='event_clause',evidence_revision='synthetic-view-2',
          facts=dict(kind='principal',selected_clause_applicable=True,due_and_payable=True,unpaid=True),
          provenance='New explicitly supplied conditional observation after fiscal carry')
        fresh=remedy(k,book,ev,schemas);check(tag+'.renew.status',fresh['status'],'proposed_conditional_status')
        expected=deepcopy(book);expected['seen'].append(ev['id'])
        projection=deepcopy(book);projection.pop('date');projection.pop('seen');projection['memory'].pop('contract_status')
        projection['memory_types']={key:value for key,value in book['memory_types'].items() if not key.startswith('/contract_status/')}
        expected['memory']['contract_status'].update(clause_status='satisfied',clause_date='2028-01-01',clause_kind='principal',
          observed_economy_sha256=s.core.digest(projection),observed_evidence_revision='synthetic-view-2',
          last_action='event_clause',evidence_digest=s.core.digest(ev))
        check(tag+'.renew.full_after',fresh['after'],expected)
        conditions=read(E01/'contract-condition-results.json')['cases']
        acceleration=deepcopy(next(x['facts'] for x in conditions if x['id']=='nonbankruptcy_declared'))
        event=dict(id='revision.'+tag,date='2028-01-01',series=series,method='new_acceleration',
          facts=acceleration,evidence_revision='synthetic-view-3',provenance='Changed supplied evidence with unchanged financial record')
        revised=remedy(k,fresh['after'],event,schemas)
        refusal(tag+'.changed_revision',revised,'unresolved');check(tag+'.changed_revision.no_after','after' not in revised)
        event['evidence_revision']=None
        missing=remedy(k,fresh['after'],event,schemas)
        refusal(tag+'.missing_revision',missing,'unresolved');check(tag+'.missing_revision.no_after','after' not in missing)
        event['evidence_revision']='synthetic-view-2';event['facts']['specified_automatic_category']=True
        category=remedy(k,fresh['after'],event,schemas)
        refusal(tag+'.wrong_automatic_category',category);check(tag+'.wrong_automatic_category.no_after','after' not in category)
        event['facts']['specified_automatic_category']=False
        consistent=remedy(k,fresh['after'],event,schemas)
        check(tag+'.matching_revision.status',consistent['status'],'proposed_conditional_status')
        exact=deepcopy(expected);exact['seen'].append(event['id'])
        exact['memory']['contract_status'].update(last_action='new_acceleration',evidence_digest=s.core.digest(event),acceleration_status='satisfied')
        check(tag+'.matching_revision.full_after',consistent['after'],exact)
        case['revision_compatibility']=dict(revised=revised,missing=missing,category=category,consistent=consistent)
        entry=case['program']['registry']['entries']['settle_late'];command=deepcopy(case['program']['commands'][4])
        command['event'].update(id='next_period_payment.'+tag,date='2028-01-02')
        payment_request=dict(profile=s.carry.engine.PROFILE,expected_state_sha256=s.core.digest(fresh['after']),
          expected_method_sha256=entry['method_sha256'],method=entry['method'],event=clock.event_for(entry,command['event']),schemas=schemas)
        payment=s.carry.engine.propose(fresh['after'],payment_request)
        check(tag+'.payment.status',payment['status'],'proposed')
        before=deepcopy(expected);expected['date']='2028-01-02';expected['seen'].append(command['event']['id'])
        roles=entry['method']['account_map'];expected['balances'][roles['cash']]='0/1';expected['balances'][roles['debt']]='0/1'
        expected['memory']['debt_terms'].update(outstanding='0/1',arrears='0/1')
        flow=dict(id=s.core.digest([command['event']['id'],'settle_late']),entity=book['context']['entity'],book=book['context']['book'],
          currency='USD',event_id=command['event']['id'],date='2028-01-02',activity='financing',origin='settle_late',amount='-40/1')
        expected['flows']=[flow];journal={key:'0/1' for key in book['accounts']};journal[roles['cash']]='-40/1';journal[roles['debt']]='40/1'
        check(tag+'.payment.full_after',payment['after'],expected)
        check(tag+'.payment.journal',payment['journal'],journal);check(tag+'.payment.flows',payment['flows'],[flow])
        relation=s.financial.transition(case['financial'],'settle_late',before,command['event'],payment['after'],schemas)
        check(tag+'.payment.relation',relation['status'],'requirements_satisfied')
        new_report=s.carry.reports.report(s.carry.reports.request(book,payment['after'],schemas,case['program']['mapping']))
        check(tag+'.new_report.status',new_report['status'],'reported')
        for name,actual,want in [('profit',new_report['income']['profit'],'0/1'),('equity',new_report['equity']['closing'],'100/1'),
          ('assets',new_report['balance_sheet']['total_assets'],'100/1'),('liabilities',new_report['balance_sheet']['total_liabilities'],'0/1'),
          ('financing',new_report['cash_flows']['activities']['financing']['net'],'-40/1')]:check(tag+'.new_report.'+name,actual,want)
        check(tag+'.historical_miss',payment['after']['memory']['debt_terms']['missed_amount'],'40/1')
        check(tag+'.existing_acceleration_survives',payment['after']['memory']['contract_status']['acceleration_status'],'satisfied')
        case['next_period_continuation']=dict(observation=ev,fresh=fresh,payment_request=payment_request,payment=payment,
          expected=expected,relation=relation,report=new_report)

if __name__=='__main__':main()
