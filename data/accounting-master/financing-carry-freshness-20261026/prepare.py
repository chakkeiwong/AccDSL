"""Prepare a bounded /3 compatibility verifier; preserve completed /2 evidence."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
OLD=HERE.parent/'financing-carry-20261026'
FRESH=HERE.parent/'financing-remedy-freshness-20261026'
read=lambda p:json.loads(p.read_text())
sha=lambda p:sha256(p.read_bytes()).hexdigest()
assert not (HERE/'successor-sources.json').exists(),'already_prepared'
assert read(OLD/'attempt-02/checks.json')['passed']
assert read(FRESH/'attempt-02/checks.json')['passed']
for folder in [OLD/'attempt-02',FRESH/'attempt-02']:
    for n,h in read(folder/'source-lock.json').items():assert sha(ROOT/n)==h,n
text=(OLD/'verify.py').read_text()
text=text.replace('import selected_carry as s',"sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'financing-carry-20261026'))\nimport selected_carry as s",1)
text=text.replace("OUT=HERE/'attempt-02'","OUT=HERE/'attempt-01'",1)
text=text.replace("sys.path.append(str(HERE.parent/'financing-remedy-state-binding-20261026'))",
                  "sys.path.insert(0,str(HERE.parent/'financing-remedy-freshness-20261026'))",1)
text=text.replace("HERE.parent/'financing-remedy-state-binding-20261026/remedy_execution.py'",
                  "HERE.parent/'financing-remedy-freshness-20261026/remedy_execution.py'",1)
text=text.replace("pins=read(HERE.parent/'financing-remedy-state-binding-20261026/attempt-01/source-lock.json')",
                  "pins=read(HERE.parent/'financing-remedy-freshness-20261026/attempt-02/source-lock.json')\n    pins.update(read(HERE.parent/'financing-carry-20261026/attempt-02/source-lock.json'))",1)
text=text.replace("HERE.parent/'financing-remedy-state-binding-20261026/result.md'",
                  "HERE.parent/'financing-remedy-freshness-20261026/result.md',\n               HERE.parent/'financing-carry-20261026/result.md',HERE.parent/'financing-carry-20261026/attempt-02/checks.json'",1)
text=text.replace("for n in ['selected_carry.py','verify.py','audit.md']:","for n in ['verify.py','audit.md']:",1)
text=text.replace("clause_economic_sha256='unknown',acceleration_status='unknown'",
 "clause_kind='unknown',observed_economy_sha256='unknown',observed_evidence_revision='unknown',acceleration_status='unknown'",1)
text=text.replace("ev=dict(id=tag+'.'+identity,date=date,series=initial['series'],method=method,",
 "ev=dict(id=tag+'.'+identity,date=date,series=initial['series'],method=method,evidence_revision='synthetic-view-1',",1)
old="""projected={k:deepcopy(before[k]) for k in ['profile','context','period','accounts','balances','cash_account','flows']}
                        projected.update(memory={k:v for k,v in before['memory'].items() if k!='contract_status'},
                          memory_types={k:v for k,v in before['memory_types'].items() if not k.startswith('/contract_status/')})
                        expected['memory']['contract_status'].update(clause_date=date,clause_economic_sha256=s.core.digest(projected))"""
new="""projected=deepcopy(before);projected.pop('date');projected.pop('seen');projected['memory'].pop('contract_status')
                        projected['memory_types']={k:v for k,v in before['memory_types'].items() if not k.startswith('/contract_status/')}
                        expected['memory']['contract_status'].update(clause_date=date,clause_kind=ev['facts']['kind'],
                          observed_economy_sha256=s.core.digest(projected),observed_evidence_revision=ev['evidence_revision'])"""
assert text.count(old)==1;text=text.replace(old,new,1)
text=text.replace("stale_event=dict(id='after_carry.'+tag,date='2028-01-01',series=initial['series'],method='new_acceleration',",
 "stale_event=dict(id='after_carry.'+tag,date='2028-01-01',series=initial['series'],method='new_acceleration',evidence_revision='synthetic-view-1',",1)
text=text.replace("'/contract_status/clause_economic_sha256'","'/contract_status/observed_economy_sha256'",1)
text=text.replace("ev=dict(id='renew.'+tag,date='2028-01-01',series=series,method='event_clause',",
 "ev=dict(id='renew.'+tag,date='2028-01-01',series=series,method='event_clause',evidence_revision='synthetic-view-2',",1)
old="""projection={key:deepcopy(book[key]) for key in ['profile','context','period','accounts','balances','cash_account','flows']}
        projection.update(memory={key:value for key,value in book['memory'].items() if key!='contract_status'},
          memory_types={key:value for key,value in book['memory_types'].items() if not key.startswith('/contract_status/')})
        expected['memory']['contract_status'].update(clause_status='satisfied',clause_date='2028-01-01',
          clause_economic_sha256=s.core.digest(projection),last_action='event_clause',evidence_digest=s.core.digest(ev))"""
new="""projection=deepcopy(book);projection.pop('date');projection.pop('seen');projection['memory'].pop('contract_status')
        projection['memory_types']={key:value for key,value in book['memory_types'].items() if not key.startswith('/contract_status/')}
        expected['memory']['contract_status'].update(clause_status='satisfied',clause_date='2028-01-01',clause_kind='principal',
          observed_economy_sha256=s.core.digest(projection),observed_evidence_revision='synthetic-view-2',
          last_action='event_clause',evidence_digest=s.core.digest(ev))"""
assert text.count(old)==1;text=text.replace(old,new,1)
anchor="        entry=case['program']['registry']['entries']['settle_late'];command=deepcopy(case['program']['commands'][4])"
addition="""        conditions=read(E01/'contract-condition-results.json')['cases']
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
"""
assert text.count(anchor)==1;text=text.replace(anchor,addition+anchor,1)
text=text.replace('accounting-financing-carry-20261026.md','accounting-financing-carry-freshness-20261026.md')
text=text.replace('financing-carry-20261026/verify.py','financing-carry-freshness-20261026/verify.py')
text=text.replace("result='data/accounting-master/financing-carry-20261026/result.md'","result='data/accounting-master/financing-carry-freshness-20261026/result.md'",1)
assert not (HERE/'verify.py').exists();(HERE/'verify.py').write_text(text)
(HERE/'successor-sources.json').write_text(json.dumps(dict(predecessor_verifier_sha256=sha(OLD/'verify.py'),
 reused_selected_carry_sha256=sha(OLD/'selected_carry.py'),remedy_profile='SelectedConditionalRemedy/3',
 remedy_sha256=sha(FRESH/'remedy_execution.py'),verifier_sha256=sha(HERE/'verify.py')),indent=2)+chr(10))
print(json.dumps(dict(prepared=True,reused_carry=True,remedy_profile='SelectedConditionalRemedy/3')))
