from copy import deepcopy
import structure as s
p=s.p;core=s.core
def retype(state):return s.bundle.d.f.f.configure(state)

def structural_corruptions(base):
    cases=[]
    def add(name,mutate,typed=False):
        state=deepcopy(base);mutate(state)
        if typed:retype(state)
        cases.append((name,state))
    add('extra_state_field',lambda x:x.update(extra='unexpected'))
    add('missing_state_field',lambda x:x.pop('migration'))
    add('wrong_state_profile',lambda x:x.update(profile='Other/1'))
    add('missing_schema',lambda x:x['schemas'].pop(x['book']['memory_schema']))
    def add_claim_field(x):
        x['memory_definition']['root']['fields']['claims']['values']['fields']['extra']={'node':'scalar','type':p.guards.TEXT}
        for row in x['book']['memory']['claims'].values():row['extra']='extra'
    add('typed_extra_claim_field',add_claim_field,True)
    def add_clock_field(x):
        x['memory_definition']['root']['fields']['collection_clock']['fields']['extra']={'node':'scalar','type':p.guards.TEXT}
        x['book']['memory']['collection_clock']['extra']='extra'
    add('typed_extra_clock_field',add_clock_field,True)
    add('missing_role',lambda x:x['roles'].pop('payables'))
    add('duplicate_role',lambda x:x['roles'].update(inventory=x['roles']['receivables']))
    add('wrong_role_class',lambda x:x['book']['accounts'][x['roles']['receivables']].update(classification='liability'))
    add('wrong_cash_role',lambda x:x['roles'].update(cash=x['roles']['receivables'],receivables=x['roles']['cash']))
    add('missing_cost_pointer',lambda x:x.update(unit_cost_pointer='/missing'))
    def cost_value(x,value):
        parts=p.base.binding.pointer_parts(x['unit_cost_pointer']);node=x['book']['memory']
        for part in parts[:-1]:node=node[part]
        node[parts[-1]]=value
    add('zero_cost',lambda x:cost_value(x,'0/1'))
    add('negative_cost',lambda x:cost_value(x,'-1/1'))
    def cost_type(x):
        node=x['memory_definition']['root']
        for part in p.base.binding.pointer_parts(x['unit_cost_pointer']):node=node['fields'][part]
        node['type']=deepcopy(p.base.money_type(x['book']))
    add('wrong_cost_dimensions',cost_type,True)
    add('extra_migration_field',lambda x:x['migration'].update(extra='unexpected'))
    add('missing_migration_field',lambda x:x['migration'].pop('premise'))
    add('wrong_migration_scope',lambda x:x['migration'].update(scope='Unsupported replacement premise'))
    add('blank_migration_premise',lambda x:x['migration'].update(premise='   '))
    add('short_migration_digest',lambda x:x['migration'].update(source_book_sha256='abc'))
    add('uppercase_migration_digest',lambda x:x['migration'].update(source_book_sha256='A'*64))
    add('nonhex_migration_digest',lambda x:x['migration'].update(source_book_sha256='g'*64))
    add('empty_migration_premise',lambda x:x['migration'].update(premise=''))
    add('blank_term_premise',lambda x:x['book']['memory']['claims']['invoice/a~1']['terms']['initial'].update(premise='   '))
    add('empty_term_premise',lambda x:x['book']['memory']['claims']['invoice/a~1']['terms']['initial'].update(premise=''))
    return cases

def run(contract,state,coverage,selection=None,call=None):
    selection=core.digest(contract) if selection is None else selection
    return s.admit(contract,state,coverage,selection,s.contract_call(contract,state,coverage,selection) if call is None else call)

def contract_controls(base,contract,coverage_for,check,records,compare):
    def invalid(name,c=contract,state=base,reason='',**kwargs):
        result=run(c,state,coverage_for(state,c),**kwargs)
        check(result['status']=='invalid' and reason in result.get('reason',''),name+':'+result.get('reason',''))
        records.append(dict(case=name,result=result))
    altered=deepcopy(contract);altered['residuals'].append('Changed reviewed condition')
    invalid('stale_reviewed_selection',c=altered,selection=core.digest(contract),reason='reviewed_term_contract')
    cov=coverage_for(base,contract);call=s.contract_call(contract,base,cov,core.digest(contract))
    state=deepcopy(base);term=state['book']['memory']['claims']['invoice/a~1'];term['terms']=dict(reversed(list(term['terms'].items())))
    invalid('stale_input_order',state=state,call=call,reason='stale_term_contract_call')
    compare('reordered_fresh',state,contract,'selected_term_state_satisfied')
    for name in ('claims','terms','assessments'):
        cov=coverage_for(base,contract);cov[name]['status']='partial'
        result=run(contract,base,cov);check(result['status']=='unresolved','partial_'+name)
        records.append(dict(case='partial_'+name,result=result))
    altered=deepcopy(contract);altered['structure']['template']['dependency_pins'][0]['sha256']='0'*64
    invalid('dependency_veto',c=altered,reason='native_dependency:')
    altered=deepcopy(contract);altered['structure']['checks'][0]['op']='custom_regex'
    invalid('unsupported_extra_check',c=altered,reason='structure_check_op')
    altered=deepcopy(contract);altered['structure']['checks'][1]['field']='missing'
    invalid('undeclared_text_field',c=altered,reason='structure_text_type')
    altered=deepcopy(contract);altered['semantics']['common']['globals']['receivable']['account']=base['roles']['cash']
    invalid('wrong_semantic_receivable_link',c=altered,reason='selected_receivable_binding')
    # A valid native alternate cost location is outside this independently selected contract.
    state=deepcopy(base);typ=state['book']['memory_types'][state['unit_cost_pointer']]
    found,value=p.base.binding.located(state['book']['memory'],state['unit_cost_pointer']);assert found
    state['memory_definition']['root']['fields']['alternate_cost']={'node':'scalar','type':deepcopy(typ)}
    state['book']['memory']['alternate_cost']=value;state['unit_cost_pointer']='/alternate_cost';retype(state)
    invalid('native_valid_unselected_cost',state=state,reason='selected_role_cost_binding')
