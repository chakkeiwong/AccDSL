"""A selected source-defined late partial coupon method over the typed runtime."""
from pathlib import Path
from copy import deepcopy as cp
import sys
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'scripts'))
import declared_company_program_v2 as rt
import declared_financing_methods_v1 as h
identity=rt.digest
TEXT={'kind':'text','context':{}};DATE={'kind':'date','context':{}}
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,durable=False)
SCOPE='Supplied synthetic partial coupon instruction; operating cash classification inherited; no actual applicability or default finding.'

def select(source,sid):
    assert identity(source)==sid and source['result']['status']=='proposed_selected_coupon_carry'
    carry=source['result']['carry'];book=cp(carry['next_opening']);rr=source['request']['carry']['report_request']
    assert book['memory']['phase']=='due2' and book['memory']['paid2']=='0/1' and book['memory']['action2']=='none' and book['memory']['used'] is True
    lines=rr['mapping']['lines'];mapping={v['id']:v['accounts'][0] for v in lines};money=rt.engine.money_type(book)
    zero=h.constant(money,'0/1');ref=h.ref;binary=h.binary;const=h.constant
    negative=lambda x:binary('sub',cp(zero),x)
    bindings={name:(typ,h.memory('/'+name)) for name,typ in ((p[1:],v) for p,v in book['memory_types'].items())}
    bindings.update(cash=(money,h.account('cash')),payable=(money,h.account('interest_payable')),facility=(money,h.account('facility_debt')),amount=(money,h.event('amount')),event_date=(DATE,h.event('event_date')))
    remaining=binary('sub',ref('due2'),ref('paid2'))
    common=[('payable_matches_unpaid',binary('eq',negative(ref('payable')),remaining),['payable','due2','paid2'],'invalid'),
            ('cash_nonnegative',binary('le',cp(zero),ref('cash')),['cash'],'invalid'),
            ('partial_claim_positive',binary('lt',cp(zero),remaining),['due2','paid2'],'invalid'),
            ('used_stays_used',ref('used'),['used'],'invalid'),
            ('facility_repaid',binary('eq',ref('facility'),cp(zero)),['facility'],'invalid')]
    for name in ('mode','right','source','clause','action1','action2','due1','due2','paid1'):
        typ=book['memory_types']['/'+name];common.append(('origin_'+name,binary('eq',ref(name),const(typ,book['memory'][name])),[name],'invalid'))
    phase={'op':'any','args':[binary('eq',ref('phase'),const(TEXT,v)) for v in ('due2','partial2')]}
    pre=cp(common)+[('supported_phase',phase,['phase'],'invalid'),('strictly_late',binary('lt',const(DATE,rr['closing']['date']),ref('event_date')),['event_date'],'invalid'),
        ('positive_amount',binary('lt',cp(zero),ref('amount')),['amount'],'invalid'),
        ('cash_available',binary('le',ref('amount'),ref('cash')),['amount','cash'],'invalid'),
        ('partial_only',binary('lt',ref('amount'),remaining),['amount','due2','paid2'],'invalid')]
    post=cp(common)+[('partial_phase',binary('eq',ref('phase'),const(TEXT,'partial2')),['phase'],'invalid')]
    def requirements(rows):
        keys=sorted({k for _,_,deps,_ in rows for k in deps});return dict(manifest=h.conditions('synthetic.late-partial-coupon',{k:bindings[k][0] for k in keys},rows),bindings={k:bindings[k][1] for k in keys})
    roles={k:mapping[k] for k in ('cash','interest_payable','facility_debt')}
    ishape=h.record({'new_paid2':h.scalar('rational')});schemas={**cp(rr['schemas']),identity(ishape):ishape}
    definition=dict(profile=rt.engine.METHOD,id='synthetic.late-partial-coupon',version='1',context=cp(book['context']),account_map=roles,
        preconditions=requirements(pre),postconditions=requirements(post),
        monetary=dict(definition=dict(profile=rt.engine.monetary.PROFILE,method_id='synthetic.late-partial-coupon',version='1',
            inputs={k:h.declaration(money,k) for k in ('amount','paid2')},
            calculations=[dict(id='new_paid2',type=money,expression=binary('add',ref('paid2'),ref('amount')),requires=['paid2','amount'])],
            accounts={k:money for k in roles},cash_account='cash',
            postings=[dict(id='cash',account='cash',expression=negative(ref('amount')),requires=['amount']),dict(id='payable',account='interest_payable',expression=ref('amount'),requires=['amount'])],
            flows=[dict(id='late_coupon_payment',activity='operating',origin='late_coupon_payment',expression=negative(ref('amount')),requires=['amount'])]),
            bindings={'amount':h.event('amount'),'paid2':h.memory('/paid2')}),
        memory=dict(definition=dict(profile=rt.engine.memory.PROFILE,state_schema=book['memory_schema'],input_schema=identity(ishape),
            operations=[dict(id='write.paid2',op='replace',path=['paid2'],value=dict(kind='read',source='inputs',pointer='/new_paid2')),dict(id='write.phase',op='replace',path=['phase'],value=dict(kind='literal',value='partial2'))]),
            input_bindings={'new_paid2':dict(kind='calculation',name='new_paid2')}),residual_prerequisites=[SCOPE])
    entry=dict(method_sha256=identity(definition),method=definition,schemas=schemas,
        account_classes={k:book['accounts'][v]['classification'] for k,v in roles.items()},event_inputs={'amount':money},metadata_bindings={'event_date':'date'},clock={'kind':'direct_event_date'})
    return dict(profile='SelectedLatePartialCoupon/1',**FLAGS,source_carry_sha256=sid,opening=book,schemas=schemas,mapping=cp(rr['mapping']),
        registry=dict(profile=rt.methods.REGISTRY,context=cp(book['context']),entries={'partial_coupon':entry}),
        origin_archive=cp(source['result']['history_archive']),scope=SCOPE)

def program(selection,instructions):
    money=rt.engine.money_type(selection['opening']);commands=[]
    for item in instructions:
        assert set(item)=={'id','date','amount'}
        commands.append(dict(kind='event',method_key='partial_coupon',event=dict(id=item['id'],date=item['date'],inputs={'amount':dict(type=money,value=rt.engine.known(item['amount']),provenance=SCOPE)})))
    return dict(profile=rt.PROFILE,name='selected-late-partial-coupon',opening=cp(selection['opening']),schemas=cp(selection['schemas']),mapping=cp(selection['mapping']),registry=cp(selection['registry']),commands=commands)

def run(source,sid,selection,selected_id,instructions):
    assert identity(selection)==selected_id and selection==select(source,sid)
    body=program(selection,instructions);result=rt.run(body)
    report=rt.reports.report(rt.reports.request(body['opening'],result['current'],body['schemas'],body['mapping'])) if 'current' in result else None
    return dict(profile='SelectedLatePartialCouponResult/1',**FLAGS,source_carry_sha256=sid,selection_sha256=selected_id,
        instructions=cp(instructions),execution=result,report=report,origin_archive=cp(selection['origin_archive']),
        interpretation='explicit_new_method_no_retroactive_original_policy_success')
