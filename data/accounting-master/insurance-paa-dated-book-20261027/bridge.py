"""Compile a conditional, separately grouped PAA example into unchanged books."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import declared_company_program_v2 as program
import declared_operating_methods_v1 as helpers

core, engine = program.core, program.engine
PROFILE = 'InsurancePAADatedBook/1'
FLAGS = dict(actual_source_admission=False, accounting_admission=False, posting_authorized=False,
             full_insurance_support=False, actual_group_identity_admission=False, actual_chronology_admission=False)
CLASSES = {'cash':'asset','held_coverage':'asset','held_claims':'asset','issued_coverage':'liability',
    'issued_claims':'liability','capital':'equity','issued_revenue':'income','held_recovery_income':'income',
    'issued_claims_expense':'expense','held_coverage_expense':'expense','equipment':'asset'}
FINDINGS = {'one_year_each_issued_contract','one_year_each_held_contract','boundaries_complete',
    'uniform_service_and_risk_release','no_acquisition_cashflows','no_investment_components','no_significant_financing',
    'remaining_coverage_not_onerous','claims_settle_within_one_year','held_recognition_conditions',
    'separate_transferred_risk_supported','nonperformance_supported','operating_cash_classification_supplied'}
DATE={'kind':'date','context':{}}; TEXT={'kind':'text','context':{}}

class Refusal(Exception):
    def __init__(self,status,reason): self.status=status; self.reason=reason

def require(condition,reason,status='invalid'):
    if not condition: raise Refusal(status,reason)

def fields(value, keys, reason):
    require(type(value) is dict and set(value)==set(keys),reason)

def fmt(value):
    value=Q(value); return f'{value.numerator}/{value.denominator}'

def validate(body):
    lock=json.loads((HERE/'source-lock.json').read_text())
    for name,h in lock.items(): require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'source_drift:'+name)
    fields(body,['profile','payload','payload_sha256'],'envelope')
    require(body['profile']==PROFILE,'profile')
    payload=body['payload'];require(core.digest(payload)==body['payload_sha256'],'payload_binding')
    fields(payload,['case_id','chart','complement','entity','currency','calendar','groups','amounts','findings',
                    'cash_policy','source_edition','assumption_scope'],'payload')
    require(payload['chart'] in ['named','renamed'] and type(payload['complement']) is bool,'chart_or_complement')
    require(payload['entity']=='I' and payload['currency']=='XCU','selected_entity_currency','unsupported')
    require(payload['source_edition']=='AASB17-compiled-Dec2022:F2023C00382','source_edition','unsupported')
    require(payload['assumption_scope']=='synthetic conditional example','assumption_scope')
    findings=payload['findings'];fields(findings,FINDINGS,'finding_population')
    for key,value in findings.items():
        require(value is not None,'unknown_'+key,'unresolved')
        require(type(value) is bool,'finding_type')
        require(value,'outside_'+key,'unsupported')
    calendar=payload['calendar']
    fields(calendar,['coverage','recognition','cutoff','interpretation','event_order'],'calendar')
    fields(calendar['coverage'],['start','end_exclusive'],'coverage')
    require(calendar['coverage']=={'start':'2024-01-01','end_exclusive':'2025-01-01'} and
            calendar['recognition']=='2024-01-01' and calendar['cutoff']=='2024-07-02','selected_synthetic_calendar','unsupported')
    require(calendar['interpretation']=='Synthetic elapsed-day service boundary; July2 is 183 of 366 days','calendar_premise')
    require(calendar['event_order']=='premiums, gross service, held service, claims measurement, claims paid, recovery measurement, recovery paid','event_order')
    start=date.fromisoformat(calendar['coverage']['start']);end=date.fromisoformat(calendar['coverage']['end_exclusive']);cut=date.fromisoformat(calendar['cutoff'])
    fraction=Q((cut-start).days,(end-start).days);require(fraction==Q(1,2),'half_service')
    groups=payload['groups'];fields(groups,['issued','held'],'groups')
    for role,group in groups.items():
        fields(group,['id','owner','role','annual_cohort','coverage','recognition']+(['underlying_group'] if role=='held' else []),'group_fields')
        require(type(group['id']) is str and bool(group['id'].strip()) and '/' not in group['id'],'group_id')
        require(group['owner']==payload['entity'] and group['role']==role,'group_owner_or_role')
        require(group['annual_cohort']=='2024' and group['coverage']==calendar['coverage'] and group['recognition']==calendar['recognition'],'group_calendar')
    require(groups['issued']['id']!=groups['held']['id'],'distinct_groups')
    require(groups['held']['underlying_group']==groups['issued']['id'],'underlying_group_link')
    amounts=payload['amounts'];fields(amounts,['opening_cash','premium','held_premium','incurred_claims','paid_claims',
        'issued_risk','quota','paid_recovery','transferred_risk','nonperformance'],'amount_population')
    numbers={}
    for key,value in amounts.items():
        require(value is not None,'unknown_'+key,'unresolved')
        require(type(value) is str and len(value)<80,'rational_encoding')
        try: numbers[key]=Q(value)
        except (ValueError,ZeroDivisionError):raise Refusal('invalid','rational_encoding')
        require(fmt(numbers[key])==value and numbers[key]>=0,'canonical_nonnegative_amount')
    fixed=dict(opening_cash=20,premium=120,held_premium=24,incurred_claims=40,paid_claims=30,
               issued_risk=2,quota=Q(1,2),paid_recovery=15)
    require(all(numbers[key]==value for key,value in fixed.items()),'outside_selected_amounts','unsupported')
    cases={'base':(Q(1),Q(0)),'separate_transferred_risk':(Q(3,2),Q(0)),'nonperformance_loss':(Q(1),Q(2))}
    require(payload['case_id'] in cases,'case_id','unsupported')
    require((numbers['transferred_risk'],numbers['nonperformance'])==cases[payload['case_id']],'case_measurements','unsupported')
    fields(payload['cash_policy'],['activity','premise'],'cash_policy')
    require(payload['cash_policy']['activity']=='operating','cash_activity','unsupported')
    require(payload['cash_policy']['premise']=='Supplied classification for this synthetic insurance example; no accounting admission','cash_premise')
    return payload,numbers,fraction

def build(body):
    p,a,fraction=validate(body);groups=p['groups'];calendar=p['calendar']
    roles={role:('paa.'+role if p['chart']=='named' else 'A'+str(100+i)) for i,role in enumerate(CLASSES)}
    context=dict(entity=p['entity'],book='legal',currency=p['currency'],case_id='paa-'+p['case_id'],mode='synthetic')
    memory=dict(issued_group=groups['issued']['id'],held_group=groups['held']['id'],underlying_group=groups['held']['underlying_group'],
        coverage_start=calendar['coverage']['start'],coverage_end_exclusive=calendar['coverage']['end_exclusive'],
        measurement_cutoff=calendar['cutoff'],source_edition=p['source_edition'],assumption_scope=p['assumption_scope'],step='0/1')
    shape={'type':'object','properties':{k:{'type':'string'} for k in memory},'required':list(memory),'additionalProperties':False}
    empty={'type':'object','properties':{},'required':[],'additionalProperties':False}
    schemas={core.digest(shape):shape,core.digest(empty):empty}
    balances={roles[key]:'0/1' for key in CLASSES};extra=17 if p['complement'] else 0
    balances.update({roles['cash']:fmt(a['opening_cash']),roles['capital']:fmt(-a['opening_cash']-extra),roles['equipment']:fmt(extra)})
    book=dict(profile=engine.BOOK,context=context,period=deepcopy(calendar['coverage']),date=calendar['recognition'],
        accounts={roles[k]:dict(classification=v) for k,v in CLASSES.items()},balances=balances,
        cash_account=roles['cash'],memory_schema=core.digest(shape),memory_types={},memory=deepcopy(memory),seen=[],flows=[])
    scalar={'kind':'rational','context':engine.type_context(book),'dimensions':{},'scale':'1/1'}
    types={key:scalar if key=='step' else DATE if key in ['coverage_start','coverage_end_exclusive','measurement_cutoff'] else TEXT for key in memory}
    book['memory_types']={'/'+key:deepcopy(typ) for key,typ in types.items()};money=engine.money_type(book)
    engine.validate_book(book,schemas)
    mapping=dict(profile=program.reports.MAP,context=deepcopy(context),lines=[dict(id=role,label=role,classification=kind,accounts=[roles[role]]) for role,kind in CLASSES.items()])
    issued,held=groups['issued']['id'],groups['held']['id'];rec=calendar['recognition'];cut=calendar['cutoff']
    incurred=a['incurred_claims']+a['issued_risk'];recovery=a['incurred_claims']*a['quota']+a['transferred_risk']-a['nonperformance']
    events=[
        ('premium_received',rec,issued,{'cash':a['premium'],'issued_coverage':-a['premium']}),
        ('held_premium_paid',rec,held,{'held_coverage':a['held_premium'],'cash':-a['held_premium']}),
        ('issued_service',cut,issued,{'issued_coverage':a['premium']*fraction,'issued_revenue':-a['premium']*fraction}),
        ('held_service',cut,held,{'held_coverage_expense':a['held_premium']*fraction,'held_coverage':-a['held_premium']*fraction}),
        ('incurred_claims',cut,issued,{'issued_claims_expense':incurred,'issued_claims':-incurred}),
        ('claims_paid',cut,issued,{'issued_claims':a['paid_claims'],'cash':-a['paid_claims']}),
        ('recovery_measured',cut,held,{'held_claims':recovery,'held_recovery_income':-recovery}),
        ('recovery_received',cut,held,{'cash':a['paid_recovery'],'held_claims':-a['paid_recovery']})]
    registry=dict(profile=program.methods.REGISTRY,context=deepcopy(context),entries={});commands=[]
    state=deepcopy(balances);expected_steps=[]
    for index,(name,at,group,postings) in enumerate(events):
        before=deepcopy(state);before_memory=deepcopy(memory)
        for role,value in postings.items():state[roles[role]]=fmt(Q(state[roles[role]])+value)
        memory['step']=fmt(index+1);identity='paa.'+name
        def conditions(expected_balances,expected_memory,with_event):
            declarations={};bindings={};checks=[]
            for role in CLASSES:
                key='balance_'+role;declarations[key]=money;bindings[key]=helpers.account(role)
                checks.append((key,helpers.binary('eq',helpers.ref(key),helpers.constant(money,expected_balances[roles[role]])),[key],'invalid'))
            for field,typ in types.items():
                key='memory_'+field;declarations[key]=typ;bindings[key]={'kind':'memory','pointer':'/'+field}
                checks.append((key,helpers.binary('eq',helpers.ref(key),helpers.constant(typ,expected_memory[field])),[key],'invalid'))
            if with_event:
                for key,typ,value in [('actual_date',DATE,at),('group_id',TEXT,group)]:
                    declarations[key]=typ;bindings[key]=helpers.event(key)
                    checks.append((key,helpers.binary('eq',helpers.ref(key),helpers.constant(typ,value)),[key],'invalid'))
            return dict(manifest=helpers.conditions(identity,declarations,checks),bindings=bindings)
        flows=[]
        if 'cash' in postings:
            flows=[dict(id='cash',activity=p['cash_policy']['activity'],origin=group+'/'+name,
                expression=helpers.constant(money,fmt(postings['cash'])),requires=[])]
        method=dict(profile=engine.METHOD,id=identity,version='1',context=deepcopy(context),account_map=deepcopy(roles),
            preconditions=conditions(before,before_memory,True),postconditions=conditions(state,memory,False),
            monetary=dict(definition=dict(profile=engine.monetary.PROFILE,method_id=identity,version='1',
                inputs={},calculations=[],accounts={role:deepcopy(money) for role in CLASSES},cash_account='cash',
                postings=[dict(id=role,account=role,expression=helpers.constant(money,fmt(value)),requires=[]) for role,value in postings.items()],flows=flows),bindings={}),
            memory=dict(definition=dict(profile=engine.memory.PROFILE,state_schema=book['memory_schema'],input_schema=core.digest(empty),
                operations=[dict(id='advance_step',op='replace',path=['step'],value=dict(kind='literal',value=memory['step']))]),input_bindings={}),
            residual_prerequisites=[p['assumption_scope'],p['source_edition'],p['cash_policy']['premise'],'Actual source, accounting and complete disclosures remain unresolved'])
        registry['entries'][name]=dict(method_sha256=core.digest(method),method=method,schemas=deepcopy(schemas),
            account_classes=deepcopy(CLASSES),event_inputs={'group_id':TEXT},metadata_bindings={'actual_date':'date'},clock={'kind':'direct_event_date'})
        commands.append(dict(kind='event',method_key=name,event=dict(id=identity,date=at,inputs={
            'group_id':dict(type=deepcopy(TEXT),value=dict(status='known',value=group),provenance='Supplied synthetic issued/held group identity')})))
        expected_steps.append(dict(id=identity,date=at,group=group,journal={roles[k]:fmt(v) for k,v in postings.items()},balances=deepcopy(state),memory=deepcopy(memory)))
    notes=[dict(id='scope',label='Conditional PAA interim example',status='unresolved',
        reason='Synthetic group/calendar/measurement facts; actual source, accounting and full note acceptance remain unresolved.')]
    commands.append(dict(kind='report',id='paa.interim',cutoff=cut,equity_movements=[],notes=notes))
    return dict(profile=program.PROFILE,name='paa.'+p['case_id'],opening=book,schemas=schemas,registry=registry,mapping=mapping,commands=commands),expected_steps

def propose(body):
    try:
        compiled,steps=build(body);execution=program.run(compiled)
        if execution['status']!='complete_provisional':
            return dict(profile=PROFILE,**FLAGS,status='native_refusal',execution=execution,compiled=compiled)
        return dict(profile=PROFILE,**FLAGS,status='proposed_conditional',request_sha256=core.digest(body),
            compiled=compiled,execution=execution,expected_steps=steps,groups=deepcopy(body['payload']['groups']),
            calendar_scope=body['payload']['calendar']['interpretation'],
            unresolved=['Actual source and accounting admission','General actuarial calibration','Full coverage-year lifecycle',
                        'Recovery-change group/calendar extension','Complete disclosures and independent acceptance'])
    except Refusal as exc:return dict(profile=PROFILE,**FLAGS,status=exc.status,reason=exc.reason)
    except (ValueError,TypeError,KeyError,OSError,ZeroDivisionError) as exc:
        return dict(profile=PROFILE,**FLAGS,status='invalid',reason=str(exc)[:300])
