"""Prospective date-only terms on both retained synthetic account charts."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import receivable_term_history_v1 as terms
spec=importlib.util.spec_from_file_location('term_legacy_examples',ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)

def migration_fixture(chart='alpha'):
    body,roles,_=legacy.lifecycle_fixture(chart);body['commands']=body['commands'][:5]
    result=terms.life.run(body);assert result['status']=='complete_provisional'
    book=result['current']
    request={'profile':terms.MIGRATION,'book':book,'expected_book_sha256':terms.core.digest(book),
        'memory_definition':body['memory_definition'],'schemas':body['schemas'],'roles':body['roles'],
        'unit_cost_pointer':body['unit_cost_pointer'],'premise':'Constructed initial terms unchanged since sale; prior assessment population unknown'}
    return request,body,roles

def event(state,operation,identity,day,**values):
    kinds=terms.event_types(state['book'],operation)
    return {'profile':terms.STEP,'expected_state_sha256':terms.core.digest(state),'operation':operation,
        'event':{'id':identity,'date':day,'inputs':{k:{'type':deepcopy(kinds[k]),'value':terms.engine.known(v),
            'provenance':'Constructed prospective date-only example'} for k,v in {'approved':True,**values}.items()}}}

def amend(state,identity='extend.1',day='2027-03-10',term_id='extension1',due='2027-04-30'):
    row=state['book']['memory']['claims']['invoice/a~1']
    return event(state,'amend',identity,day,claim_id='invoice/a~1',customer='Customer A',prior_term=row['current_term'],
        term_id=term_id,due=due,premise='Supplied prospective extension only; no consideration, interest, principal or impairment change')

def case(chart):
    migration,body,roles=migration_fixture(chart);m=terms.migrate(migration)
    assert m['status']=='migrated_provisional',m
    state=m['state'];original=deepcopy(state);steps=[]
    def apply(request):
        nonlocal state
        before=deepcopy(state);result=terms.step(state,request)
        assert result['status']=='proposed',result
        assert state==before and terms.verify(state,request,result)
        steps.append({'before':before,'request':request,'result':result});state=result['after']
        return result
    first=apply(amend(state));claim=state['book']['memory']['claims']['invoice/a~1']
    assert claim['due']=='2027-04-30' and claim['overdue']=='20/1'
    assert claim['assessments']==original['book']['memory']['claims']['invoice/a~1']['assessments']
    assert state['book']['balances']==original['book']['balances'] and set(first['transition']['journal'].values())=={'0/1'}
    apply(event(state,'assess','assess.mar','2027-03-31',start='2027-03-01',end_exclusive='2027-04-01'))
    claim=state['book']['memory']['claims']['invoice/a~1'];assert claim['overdue']=='0/1' and claim['assessed_remaining']=='20/1'
    apply(amend(state,'extend.2','2027-04-10','extension2','2027-05-31'))
    apply(event(state,'collect','receipt.new','2027-04-15',claim_id='invoice/a~1',customer='Customer A',amount='5/1'))
    claim=state['book']['memory']['claims']['invoice/a~1'];assert claim['remaining']=='15/1' and claim['assessed_remaining']=='20/1'
    apply(event(state,'assess','assess.apr','2027-04-30',start='2027-04-01',end_exclusive='2027-05-01'))
    apply(event(state,'assess','assess.jun','2027-06-30',start='2027-05-01',end_exclusive='2027-07-01'))
    claim=state['book']['memory']['claims']['invoice/a~1'];assert claim['overdue']=='15/1'
    apply(event(state,'assess','assess.year','2027-12-31',start='2027-07-01',end_exclusive='2028-01-01'))
    report=terms.life.reports.request(body['opening'],state['book'],state['schemas'],body['mapping'])
    carry_request={'profile':terms.CARRY,'expected_state_sha256':terms.core.digest(state),'report_request':report,
                   'close_id':'term.year.close','retained_account':roles['retained'],'next_end_exclusive':'2029-01-01'}
    carried=terms.carry(state,carry_request);assert carried['status']=='proposed',carried
    assert terms.verify(state,carry_request,carried)
    assert carried['after']['book']['memory']['claims']==state['book']['memory']['claims']
    carry_before=deepcopy(state);state=carried['after']
    apply(event(state,'collect','receipt.next','2028-01-10',claim_id='invoice/a~1',customer='Customer A',amount='15/1'))
    apply(event(state,'assess','assess.next','2028-01-31',start='2028-01-01',end_exclusive='2028-02-01'))
    claim=state['book']['memory']['claims']['invoice/a~1']
    assert claim['remaining']==claim['overdue']=='0/1' and len(claim['terms'])==3 and len(claim['assessments'])==6
    assert claim['assessments']['imported']['overdue']=='20/1' and claim['assessments']['assess.jun']['overdue']=='15/1'
    assert state['book']['balances'][roles['cash']]=='130/1' and state['book']['balances'][roles['receivables']]=='0/1'
    assert state['book']['balances'][roles['retained']]=='-20/1'
    return {'migration_request':migration,'migration':m,'steps':steps,'carry_before':carry_before,'carry_request':carry_request,'carry':carried,'final':state}

def cases():return {chart:case(chart) for chart in ['alpha','beta']}
