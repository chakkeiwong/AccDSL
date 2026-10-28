"""Prospective supplied coupon amendment; not modification accounting admission."""
from copy import deepcopy
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'data/accounting-master/company-state-persistent-rate-failures-20261028/fixture.py'
s=importlib.util.spec_from_file_location('retained_amendment_parent',p)
prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
program,h=prior.program,prior.h

def make(owner='alpha',amend=True):
    b,roles=prior.make('fixed',owner);book=b['opening'];money=program.engine.money_type(book)
    unit=book['memory_types']['/terms/stage'];date_type=h.DATE
    shape=deepcopy(b['schemas'][book['memory_schema']]);terms=shape['properties']['terms']
    terms['properties'].update(revision=h.scalar('rational'),amendment_effective=h.scalar('date'))
    terms['required']+=['revision','amendment_effective']
    book['memory']['terms'].update(revision='0/1',amendment_effective='2028-01-01')
    book['memory_types'].update({'/terms/revision':deepcopy(unit),'/terms/amendment_effective':deepcopy(date_type)})
    book['memory_schema']=program.digest(shape);b['schemas'][book['memory_schema']]=shape
    entry=b['registry']['entries']['coupon'];method=entry['method'];entry['schemas'][book['memory_schema']]=shape
    method['memory']['definition']['state_schema']=book['memory_schema']
    method['id']='literature.synthetic.coupon.with-explicit-amendment'
    for key in ['preconditions','postconditions']:method[key]['manifest']['method_id']=method['id']
    method['monetary']['definition']['method_id']=method['id']
    pre=method['preconditions'];pre['manifest']['inputs']['revision']=h.declaration(unit,'revision')
    pre['bindings']['revision']=h.memory('/terms/revision')
    for row in pre['manifest']['requirements']:
        if row['id']=='supplied_coupon_matches_type':
            row.update(id='coupon_matches_explicit_revision',predicate=h.binary('eq',h.ref('coupon'),h.binary('add',h.constant(money,'5/1'),h.binary('mul',h.constant(money,'2/1'),h.ref('revision')))),requires=['coupon','revision'])
    for name,predicate in [('revision_nonnegative',h.binary('le',h.constant(unit,'0/1'),h.ref('revision'))),('revision_at_most_one',h.binary('le',h.ref('revision'),h.constant(unit,'1/1')))]:
        pre['manifest']['requirements'].append(dict(id=name,guard=h.constant(program.core.BOOL,True),guard_requires=[],predicate=predicate,requires=['revision'],admission_refs=[],on_false='invalid',on_unknown='unresolved'))
    for name,binding in [('event_date',h.event('event_date')),('effective',h.memory('/terms/amendment_effective'))]:
        pre['manifest']['inputs'][name]=h.declaration(date_type,name)
        pre['bindings'][name]=binding
    pre['manifest']['requirements'].append(dict(id='revision_effective_before_payment',guard=h.binary('eq',h.ref('revision'),h.constant(unit,'1/1')),guard_requires=['revision'],predicate=h.binary('le',h.ref('effective'),h.ref('event_date')),requires=['effective','event_date'],admission_refs=[],on_false='invalid',on_unknown='unresolved'))
    entry['metadata_bindings']={'event_date':'date'}
    method['residual_prerequisites']=['Supplied annual fixed coupons5 before and7 after recorded revision1; no principal/carrying change or other recognition assumed. Actual modification treatment and authority unverified.']
    entry['method_sha256']=program.digest(method)
    amendment=deepcopy(entry);m=amendment['method'];ident='literature.synthetic.prospective-coupon-amendment';m['id']=ident
    types=dict(stage=unit,revision=unit,coupon=money,new_coupon=money,approved=program.core.BOOL,event_date=date_type,effective=date_type)
    binds=dict(stage=h.memory('/terms/stage'),revision=h.memory('/terms/revision'),coupon=h.memory('/terms/coupon'),new_coupon=h.event('new_coupon'),approved=h.event('approved'),event_date=h.event('event_date'),effective=h.memory('/terms/amendment_effective'))
    constraints=[('after_carry_stage',h.binary('eq',h.ref('stage'),h.constant(unit,'0/1')),['stage'],'invalid'),
                 ('unmodified_revision',h.binary('eq',h.ref('revision'),h.constant(unit,'0/1')),['revision'],'invalid'),
                 ('old_coupon5',h.binary('eq',h.ref('coupon'),h.constant(money,'5/1')),['coupon'],'invalid'),
                 ('declared_effective_date',h.binary('eq',h.ref('event_date'),h.ref('effective')),['event_date','effective'],'invalid'),
                 ('supplied_new_coupon7',h.binary('eq',h.ref('new_coupon'),h.constant(money,'7/1')),['new_coupon'],'invalid'),
                 ('supplied_approval',h.ref('approved'),['approved'],'unsupported')]
    m['preconditions']=dict(manifest=h.conditions(ident,types,constraints),bindings=binds)
    post_types=dict(revision=unit,coupon=money,stage=unit)
    post=[('recorded_revision1',h.binary('eq',h.ref('revision'),h.constant(unit,'1/1')),['revision'],'invalid'),
          ('recorded_coupon7',h.binary('eq',h.ref('coupon'),h.constant(money,'7/1')),['coupon'],'invalid'),
          ('payment_not_fabricated',h.binary('eq',h.ref('stage'),h.constant(unit,'0/1')),['stage'],'invalid')]
    m['postconditions']=dict(manifest=h.conditions(ident,post_types,post),bindings={k:binds[k] for k in post_types})
    empty=h.record({});empty_hash=program.digest(empty);b['schemas'][empty_hash]=empty
    m['monetary']=dict(definition=dict(profile=program.engine.monetary.PROFILE,method_id=ident,version='1',inputs={},calculations=[],accounts={'cash':money},cash_account='cash',postings=[],flows=[]),bindings={})
    m['account_map']={'cash':roles['cash']}
    m['memory']=dict(definition=dict(profile=program.engine.memory.PROFILE,state_schema=book['memory_schema'],input_schema=empty_hash,operations=[
        dict(id='revision',op='replace',path=['terms','revision'],value=dict(kind='literal',value='1/1')),
        dict(id='coupon',op='replace',path=['terms','coupon'],value=dict(kind='literal',value='7/1'))]),input_bindings={})
    amendment.update(method_sha256=program.digest(m),schemas=deepcopy(b['schemas']),account_classes={'cash':'asset'},event_inputs={'approved':deepcopy(program.core.BOOL),'new_coupon':deepcopy(money)},metadata_bindings={'event_date':'date'})
    b['registry']['entries']['amend_coupon']=amendment
    for e in b['registry']['entries'].values():b['schemas'].update(deepcopy(e['schemas']))
    policies=b['commands'][2]['memory_policies']
    for key in ['/terms/revision','/terms/amendment_effective']:policies[key]=dict(kind='preserve',provenance='Preserve revision and explicit amendment effective date')
    if amend:
        inputs={k:dict(type=deepcopy(amendment['event_inputs'][k]),value=program.engine.known(v),provenance='Explicit synthetic prospective amendment premise') for k,v in dict(approved=True,new_coupon='7/1').items()}
        b['commands'].insert(3,dict(kind='event',method_key='amend_coupon',event=dict(id='amend.2028',date='2028-01-01',inputs=inputs)))
    b['name']='explicit-fixed-coupon-amendment-'+owner+('-changed' if amend else '-unchanged')
    for command in b['commands']:
        if command['kind'] in ['report','carry']:command['notes'].append(dict(id='amendment',label='Supplied prospective coupon revision',status='unresolved',reason='No principal/carrying change or other recognition assumed; actual contract and modification treatment not admitted'))
    return b,roles


def validate_scope(bundle):
    """Check this fixture's preserve-only terms; not generic source authentication."""
    for command in bundle['commands']:
        if command['kind']!='carry':continue
        for path in bundle['opening']['memory_types']:
            if not path.startswith('/terms/') or path=='/terms/stage':continue
            policy=command['memory_policies'].get(path)
            if not policy or policy.get('kind')!='preserve':
                raise ValueError('term_change_without_event:'+path)


def run(bundle):
    validate_scope(bundle)
    return program.run(bundle)
