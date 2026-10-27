"""Exact state bindings into retained collection and guarded requirement engines."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-program-composition-20261026'))
import runner as program
import method_collection_totals_v1 as totals
import declared_operating_methods_v1 as builders
base=program.base;core=program.core;digest=core.digest;types=program.typed.types
PROFILE='BookStateInvariant/1';DATE={'kind':'date','context':{}};TEXT={'kind':'text','context':{}}

def validate(spec):
    base.closed(spec,['profile','context','definition','globals','collections','residual_prerequisites'])
    core.need(spec['profile']==PROFILE,'state_invariant_profile');totals.validate(spec['definition'])
    snapshot=spec['definition']['snapshot']
    core.need(set(spec['globals'])==set(snapshot['inputs']),'global_binding_population')
    core.need(set(spec['collections'])==set(snapshot['collections']),'collection_binding_population')
    core.identifiers(spec['residual_prerequisites'],'residual_prerequisites',True)
    for key,binding in spec['globals'].items():
        kind=binding.get('kind');core.need(kind in ['date','balance','memory'],'global_binding_kind')
        base.closed(binding,['kind']+(['account'] if kind=='balance' else ['pointer'] if kind=='memory' else []))
    for key,binding in spec['collections'].items():
        kind=binding.get('kind');core.need(kind in ['memory_map','seen'],'collection_binding_kind')
        base.closed(binding,['kind','fields']+(['pointer'] if kind=='memory_map' else []))
        core.need(set(binding['fields'])==set(snapshot['collections'][key]['fields']),'field_binding_population')
        for item in binding['fields'].values():
            core.need(item.get('kind') in (['key','field'] if kind=='memory_map' else ['value']),'row_binding_kind')
            base.closed(item,['kind']+(['pointer'] if item['kind']=='field' else []))
    return spec

def bind(spec,book,memory_definition,schemas):
    validate(spec);program.typed.typed_book(book,memory_definition,schemas)
    core.need(spec['context']==book['context'],'invariant_context')
    snapshot=spec['definition']['snapshot'];values={'globals':{},'collections':{}};lineage={}
    def typed_value(value,typ,declaration,path):
        core.need(typ==declaration['type'],'binding_type_mismatch:'+path)
        core.need(declaration['role']=='state','binding_state_role')
        return base.known(value)
    for key,binding in spec['globals'].items():
        kind=binding['kind'];path='/date'
        if kind=='date':value,typ=book['date'],DATE
        elif kind=='balance':
            account=binding['account'];core.need(account in book['accounts'],'invariant_account')
            value,typ=book['balances'][account],base.money_type(book);path=types.pointer(['balances',account])
        else:
            found,value=base.binding.located(book['memory'],binding['pointer']);core.need(found,'missing_memory_leaf')
            core.need(binding['pointer'] in book['memory_types'],'untyped_memory_leaf');typ=book['memory_types'][binding['pointer']]
            path='/memory'+binding['pointer']
        values['globals'][key]=typed_value(value,typ,snapshot['inputs'][key],path);lineage['global:'+key]=path
    for key,binding in spec['collections'].items():
        declarations=snapshot['collections'][key]['fields'];rows=[]
        if binding['kind']=='seen':
            for field in binding['fields']:
                core.need(declarations[field]['type']==TEXT and declarations[field]['role']=='state','seen_declaration_type')
            for i,item in enumerate(book['seen']):
                rows.append({field:typed_value(item,TEXT,declarations[field],'/seen/'+str(i)) for field in binding['fields']})
        else:
            pointer=binding['pointer'];found,population=base.binding.located(book['memory'],pointer)
            core.need(found and type(population) is dict,'memory_map_binding')
            node=memory_definition['root']
            for token in base.binding.pointer_parts(pointer):
                node=node['fields'][token] if node['node']=='record' else node['values'] if node['node']=='map' else None
                core.need(node is not None,'memory_map_path')
            core.need(node['node']=='map','declared_map_required')
            # Declaration types are checked even for an empty map.
            for field,item in binding['fields'].items():
                typ=TEXT
                if item['kind']=='field':
                    leaf=node['values']
                    for token in base.binding.pointer_parts(item['pointer']):
                        core.need(leaf['node']=='record','row_record_path');leaf=leaf['fields'][token]
                    core.need(leaf['node']=='scalar','row_scalar_required');typ=leaf['type']
                core.need(typ==declarations[field]['type'] and declarations[field]['role']=='state','row_declaration_type')
            for identity,item_value in population.items():
                row={}
                for field,item in binding['fields'].items():
                    path='/memory'+pointer+'/'+identity.replace('~','~0').replace('/','~1')
                    if item['kind']=='key':value,typ=identity,TEXT
                    else:
                        found,value=base.binding.located(item_value,item['pointer']);core.need(found,'missing_row_field')
                        leaf_pointer=pointer+'/'+identity.replace('~','~0').replace('/','~1')+item['pointer']
                        core.need(leaf_pointer in book['memory_types'],'untyped_row_field');typ=book['memory_types'][leaf_pointer];path='/memory'+leaf_pointer
                    row[field]=typed_value(value,typ,declarations[field],path)
                rows.append(row)
        values['collections'][key]={'status':'complete','rows':rows};lineage['collection:'+key]=deepcopy(binding)
    return values,lineage

def assess(spec,book,memory_definition,schemas):
    try:
        values,lineage=bind(spec,book,memory_definition,schemas)
        result=totals.assess(spec['definition'],values,[])
        return {'profile':PROFILE,**program.FLAGS,'status':result['status'],'book_sha256':digest(book),
            'invariant_sha256':digest(spec),'values':values,'lineage':lineage,'assessment':result,
            'scope':'Complete supplied internal state only; actual-source completeness unadmitted'}
    except (ValueError,TypeError,KeyError,RecursionError) as exc:
        return {'profile':PROFILE,**program.FLAGS,'status':'invalid','reason':str(exc)[:300]}

def receivable_definition(book,receivable_account):
    money=base.money_type(book);declaration=builders.declaration;ref=builders.ref;binary=builders.binary;const=builders.constant
    fields={'identity':TEXT,'customer':TEXT,'due':DATE,'issued':DATE,'sale_event':TEXT,'remaining':money,
        'assessed':core.BOOL,'assessment_date':DATE,'assessed_remaining':money,'overdue':money}
    row_types={**{k:v for k,v in fields.items() if k not in ['identity','customer','sale_event']},'as_of':DATE};true=const(core.BOOL,True);zero=const(money,'0/1');rows=[]
    def rule(name,predicate,deps,guard=None,guard_deps=None):
        rows.append({'id':name,'guard':deepcopy(true if guard is None else guard),'guard_requires':guard_deps or [],
            'predicate':predicate,'requires':deps,'admission_refs':[],'on_false':'invalid','on_unknown':'unresolved'})
    for field in ['remaining','assessed_remaining','overdue']:rule(field+'_nonnegative',binary('le',zero,ref(field)),[field])
    rule('issued_before_due',binary('le',ref('issued'),ref('due')),['issued','due'])
    rule('issued_by_now',binary('le',ref('issued'),ref('as_of')),['issued','as_of'])
    assessed=ref('assessed');not_assessed={'op':'not','arg':ref('assessed')}
    rule('assessment_after_issue',binary('le',ref('issued'),ref('assessment_date')),['issued','assessment_date'],assessed,['assessed'])
    rule('assessment_by_now',binary('le',ref('assessment_date'),ref('as_of')),['assessment_date','as_of'],assessed,['assessed'])
    for field in ['assessed_remaining','overdue']:rule('unassessed_'+field,binary('eq',ref(field),zero),[field],not_assessed,['assessed'])
    # Nested guarded implications avoid introducing another Boolean evaluator.
    after_due=binary('lt',ref('due'),ref('assessment_date'))
    by_due=binary('le',ref('assessment_date'),ref('due'))
    def both(a,b):return {'op':'all','args':[a,b]}
    rule('overdue_after_due',binary('eq',ref('overdue'),ref('assessed_remaining')),['overdue','assessed_remaining'],both(assessed,after_due),['assessed','due','assessment_date'])
    rule('zero_by_due',binary('eq',ref('overdue'),zero),['overdue'],both(assessed,by_due),['assessed','assessment_date','due'])
    manifest={'profile':builders.engine.requirements.PROFILE,'method_id':'declared.claim_state','version':'1',
        'inputs':{k:declaration(t,k) for k,t in row_types.items()},'requirements':rows,'required_known':[],'capabilities':[],
        'residual_prerequisites':['Supplied internal state only; customer selection and event generation separate']}
    snapshot={'profile':totals.snapshot.PROFILE,'method_id':'declared.claim_state','version':'1',
        'inputs':{'as_of':declaration(DATE,'as_of'),'receivable':declaration(money,'receivable')},
        'collections':{'claims':{'fields':{k:declaration(t,k) for k,t in fields.items()}},'seen':{'fields':{'id':declaration(TEXT,'seen_id')}}},
        'constraints':[{'id':'claims_unique','op':'unique','collection':'claims','field':'identity'},
            {'id':'sale_seen','op':'references','source':'claims','field':'sale_event','target':'seen','target_field':'id'},
            {'id':'claim_rows','op':'each','collection':'claims','definition':manifest,
             'bindings':{k:{'scope':'global' if k=='as_of' else 'row','field':k} for k in row_types}}],
        'residual_prerequisites':['Internal collection membership is not disclosed-history completeness']}
    assessment=builders.conditions('declared.claim_total',{'claim_total':money,'receivable':money},
        [('claim_receivable_sum',binary('eq',ref('claim_total'),ref('receivable')),['claim_total','receivable'],'invalid')])
    definition={'profile':totals.PROFILE,'method_id':'declared.claim_state','version':'1','snapshot':snapshot,'assessment':assessment,
        'bindings':{'claim_total':{'kind':'sum','collection':'claims','field':'remaining'},'receivable':{'kind':'global','input':'receivable'}},
        'residual_prerequisites':['No source or accounting admission']}
    return {'profile':PROFILE,'context':deepcopy(book['context']),'definition':definition,
        'globals':{'as_of':{'kind':'date'},'receivable':{'kind':'balance','account':receivable_account}},
        'collections':{'claims':{'kind':'memory_map','pointer':'/claims','fields':{
            k:{'kind':'key'} if k=='identity' else {'kind':'field','pointer':'/'+k} for k in fields}},
            'seen':{'kind':'seen','fields':{'id':{'kind':'value'}}}},
        'residual_prerequisites':['Actual history, source admission, event selection and policy applicability remain separate']}
