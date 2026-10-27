"""Selected raw-bound return transition; diagnostic application, never admission."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util, json, sys
import method_requirements_v1 as core
import method_requirements_v3 as requirements
import method_input_binding_v1 as binding
import method_monetary_effects_v1 as monetary
import method_memory_effects_v1 as memory
import native_return_state_structure_v1 as structure

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'data/accounting-master/typed-return-composition-20261024'
PROFILE='TypedReturnTransition/1'
BOUNDARY={'executed':False,'committed':False,'source_admission':False,
          'accounting_admission':False,'method_eligible':False,'scope':'selected_conditional_return_transition'}


def checked_builders():
    locks=json.loads((PACKAGE/'dependency-lock.json').read_text())
    for name,h in locks.items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'composition_dependency_changed:'+name)
    loaded=[]
    for name,path in [('bound_monetary_programs','typed-monetary-effects-20261024'),
                      ('bound_memory_programs','typed-memory-effects-20261024')]:
        spec=importlib.util.spec_from_file_location(name,ROOT/'data/accounting-master'/path/'examples.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        loaded.append(module)
    return loaded


def decode(raw,digest):
    binding.hash_string(digest)
    core.need(type(raw) is bytes and len(raw)<=core.MAX_BYTES,'raw_bytes_limit')
    core.need(sha256(raw).hexdigest()==digest,'raw_digest_mismatch')
    result=binding.portable.decode(raw);binding.bounded(result)
    return result


def event_schema():
    shapes=deepcopy(structure.author.schema()['properties']['events']['items'])
    state=structure.schema()['properties']
    rational=deepcopy(state['other_inventory'])
    number={'oneOf':[rational,{'const':'unknown'}]}
    for shape in shapes['oneOf']:
        p=shape['properties'];kind=p['kind']['const']
        for key in (structure.author.SETTLE_NUMBERS if kind=='settle' else ['fraction','proceeds']):
            p[key]=deepcopy(number)
        p['date']=deepcopy(state['date'])
        p['source_pointer']=deepcopy(state['component']['properties']['source_pointer'])
    return shapes


def ref(key):return {'op':'ref','id':key}
def op(name,left,right):return {'op':name,'left':left,'right':right}
def constant(value,t):return {'op':'const','value':value,'type':deepcopy(t)}


def prerequisite_manifest(state,event,state_hash,event_hash):
    context={'entity':state['context']['entity'],'book_role':state['context']['book_role'],'at':event['date']}
    def numeric(d):return {'kind':'rational','context':deepcopy(context),'dimensions':d,'scale':'1/1'}
    money=numeric({'currency:USD':1});units=numeric({'goods:unit':1})
    price=numeric({'currency:USD':1,'goods:unit':-1});scalar=numeric({})
    text={'kind':'text','context':{}};day={'kind':'date','context':{}}
    inputs,values,lineage,rules={},{},{},[]
    def add(key,t,source,pointer):
        value=read_path(state if source=='before' else event,pointer)
        digest=state_hash if source=='before' else event_hash
        source_ref='sha256:'+digest+'#'+pointer
        inputs[key]={'type':deepcopy(t),'role':'state' if source=='before' else ('caller_finding' if t==core.BOOL else 'reported_measurement'),'source_ref':source_ref}
        values[key]=({'status':'unknown','reason':'explicit_native_unknown:'+source+pointer} if value=='unknown'
                     else {'status':'known','value':value})
        lineage[key]={'source':source,'raw_sha256':digest,'pointer':pointer}
    def rule(key,predicate,deps,consequence='invalid'):
        rules.append({'id':key,'guard':constant(True,core.BOOL),'guard_requires':[],
            'predicate':predicate,'requires':deps,'admission_refs':[],
            'on_false':consequence,'on_unknown':'unresolved'})
    add('event_date',day,'event','/date');add('state_date',day,'before','/date')
    add('tax_close',day,'before','/tax_closed_until');add('start',day,'before','/period/start');add('end',day,'before','/period/end_exclusive')
    rule('chronology',{'op':'all','args':[op('le',ref('start'),ref('event_date')),op('lt',ref('event_date'),ref('end')),
         op('le',ref('state_date'),ref('event_date')),op('le',ref('tax_close'),ref('event_date'))]},['start','end','state_date','tax_close','event_date'])
    if event['kind']=='settle':
        add('component',text,'before','/component/id');add('event_component',text,'event','/component_id')
        add('settled',core.BOOL,'before','/component/settled')
        rule('component_identity',op('eq',ref('component'),ref('event_component')),['component','event_component'])
        rule('unsettled',{'op':'not','arg':ref('settled')},['settled'])
        for key in ['all_rights_closed','handling_is_selling_cost']:
            add(key,core.BOOL,'event','/'+key);rule(key,ref(key),[key],'unsupported')
        for key,t,source,pointer in [
            ('n',units,'event','/actual_units'),('sold',units,'before','/component/sold_units'),
            ('h',price,'event','/unit_handling'),('d',price,'event','/unit_deterioration'),
            ('c',price,'before','/component/unit_cost'),('p',price,'before','/component/unit_refund'),
            ('nrv',money,'event','/inventory_nrv'),('refund_cash',money,'event','/refund_cash'),('handling_cash',money,'event','/handling_cash')]:
            add(key,t,source,pointer)
        rule('quantities',{'op':'all','args':[op('lt',constant('0/1',units),ref('n')),op('le',ref('n'),ref('sold')),
             op('le',constant('0/1',price),ref('h')),op('le',constant('0/1',price),ref('d')),
             op('le',ref('d'),ref('c')),op('le',constant('0/1',money),ref('nrv'))]},['n','sold','h','d','c','nrv'])
        rule('refund_fact',op('eq',ref('refund_cash'),op('mul',ref('n'),ref('p'))),['refund_cash','n','p'])
        rule('handling_fact',op('eq',ref('handling_cash'),op('mul',ref('n'),ref('h'))),['handling_cash','n','h'])
    else:
        add('performance',core.BOOL,'event','/performance_complete');rule('performance',ref('performance'),['performance'],'unsupported')
        add('fraction',scalar,'event','/fraction');rule('whole_lot',op('eq',ref('fraction'),constant('1/1',scalar)),['fraction'],'unsupported')
        add('proceeds',money,'event','/proceeds');rule('nonnegative_proceeds',op('le',constant('0/1',money),ref('proceeds')),['proceeds'])
    definition={'profile':requirements.PROFILE,'method_id':'selected.return.'+event['kind'],'version':'1',
                'inputs':inputs,'requirements':rules,'required_known':list(inputs),'capabilities':[],
                'residual_prerequisites':['Source authority, accounting admission and whole-method eligibility remain separate.']}
    h=core.digest(definition)
    return requirements.assess({h:definition},h,values,[]),lineage


def read_path(value,pointer):
    found,item=binding.located(value,pointer)
    core.need(found,'required_path_missing:'+pointer)
    return item


def propose(state_raw,state_sha256,event_raw,event_sha256):
    try:
        monetary_programs,memory_programs=checked_builders()
        state=decode(state_raw,state_sha256);event=decode(event_raw,event_sha256)
        shape=structure.schema();structure.validate(state,shape)
        core.need(type(event) is dict and type(event.get('kind')) is str,'event_kind')
        if event['kind'] not in ['settle','sell']:
            return {**BOUNDARY,'status':'unsupported','reason':'selected_settlement_or_sale_only'}
        structure.validate(event,event_schema())
        if state['context']['currency']!='USD' or state['context']['book_role']!='legal':
            return {**BOUNDARY,'status':'unsupported','reason':'selected_USD_legal_profile_only'}
        structure.native.invariant(state)
        core.need(event['id'] not in state['seen'],'duplicate_event')
        if event['kind']=='settle':core.need(event['lot_id'] not in state['lots'],'duplicate_lot')
        else:
            core.need(event['lot_id'] in state['lots'],'unknown_lot')
            core.need(not state['lots'][event['lot_id']]['disposed'],'lot_already_disposed')
        assessed,prerequisite_lineage=prerequisite_manifest(state,event,state_sha256,event_sha256)
        if assessed['status']!='requirements_satisfied':
            return {**BOUNDARY,'status':assessed['status'],'reason':'selected_prerequisites','prerequisites':assessed}
        context={'entity':state['context']['entity'],'book_role':'legal','at':event['date']}
        definition=monetary_programs.program(event['kind'],context,structure.native.ACCOUNTS)
        if event['kind']=='settle':
            paths={'n':('event','/actual_units'),'p':('before','/component/unit_refund'),
                'c':('before','/component/unit_cost'),'d':('event','/unit_deterioration'),
                'h':('event','/unit_handling'),'nrv':('event','/inventory_nrv'),
                'refund_before':('before','/component/refund'),'recovery_before':('before','/component/recovery')}
        else:
            token=event['lot_id'].replace('~','~0').replace('/','~1')
            paths={'proceeds':('event','/proceeds'),'cost':('before','/lots/'+token+'/carrying')}
        values,lineage={},{}
        for key,(source,pointer) in paths.items():
            raw_hash=state_sha256 if source=='before' else event_sha256
            item=read_path(state if source=='before' else event,pointer)
            definition['inputs'][key]['source_ref']='sha256:'+raw_hash+'#'+pointer
            values[key]={'status':'known','value':item}
            lineage[key]={'source':source,'raw_sha256':raw_hash,'pointer':pointer}
        h=core.digest(definition);amounts=monetary.derive({h:definition},h,values)
        if amounts['status']!='derived':return {**BOUNDARY,'status':amounts['status'],'reason':'monetary_derivation','monetary':amounts}
        balances={k:monetary.fmt(monetary.bounded(monetary.rational(v)+monetary.rational(amounts['journal'][k]))) for k,v in state['balances'].items()}
        flows=[{'entity':state['context']['entity'],'activity':f['activity'],'origin':f['origin'],
                'amount':f['amount'],'date':event['date'],'event_id':event['id']} for f in amounts['flows']]
        inputs={'event_id':event['id'],'date':event['date'],'lot_id':event['lot_id'],'balances':balances,'flows':flows}
        if event['kind']=='settle':
            calculated={r['id']:r['binding']['value'] for r in amounts['diagnostics']['calculations']}
            inputs.update(component_id=state['component']['id'],units=event['actual_units'],
                          carrying=calculated['carrying'],tax_adjustment=calculated['tax_adjustment'])
        memory_definition,schemas=memory_programs.program(event['kind']);key=core.digest(memory_definition)
        staged=memory.stage({key:memory_definition},key,schemas,state,inputs)
        core.need(staged['status']=='staged','memory_staging:'+staged.get('reason',staged['status']))
        after=staged['after'];structure.native.invariant(after)
        proposal={'profile':PROFILE,'state_raw_sha256':state_sha256,'event_raw_sha256':event_sha256,
                  'implementation_bundle_sha256':sha256((PACKAGE/'dependency-lock.json').read_bytes()).hexdigest(),
                  'before_sha256':core.digest(state),'event_sha256':core.digest(event),
                  'state_schema_sha256':core.digest(shape),'event_schema_sha256':core.digest(event_schema()),
                  'prerequisites':assessed,'prerequisite_lineage':prerequisite_lineage,
                  'monetary_definition':h,'memory_definition':key,'monetary_lineage':lineage,
                  'monetary_values_sha256':core.digest(values),'memory_inputs_sha256':core.digest(inputs),
                  'journal':amounts['journal'],'flows':flows,'after':after,'committed':False}
        return {**BOUNDARY,'status':'proposed','proposal':proposal}
    except structure.native.Rejected as exc:
        return {**BOUNDARY,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}


def apply(state_raw,state_sha256,event_raw,event_sha256,proposal):
    expected=propose(state_raw,state_sha256,event_raw,event_sha256)
    if expected['status']!='proposed':return expected
    try:
        memory.bounded(proposal)
        core.need(core.canonical(proposal)==core.canonical(expected['proposal']),'proposal_fails_full_recomputation')
        return {**BOUNDARY,'status':'applied_diagnostic','after':deepcopy(expected['proposal']['after']),
                'proposal_sha256':core.digest(expected['proposal'])}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}
