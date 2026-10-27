"""Build explicit declarations from inspected constants and retained typed data."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import ast,importlib.util,json
import structure as s
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];p=s.p;core=s.core
module_spec=importlib.util.spec_from_file_location('term_semantic_declaration',HERE.parent/'term-semantic-composition-20261026/declaration.py')
semantic=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(semantic)
def read(path):return json.loads(path.read_text())
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+chr(10))
def constants(file,names):
    result={}
    for node in ast.parse(file.read_text()).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in names:result[target.id]=ast.literal_eval(node.value)
    assert set(result)==set(names);return result
def stage(identity,op,reason,**fields):return dict(id=identity,op=op,reason=reason,**fields)

def main():
    assert not (HERE/'contracts.json').exists(),'preparation_already_complete'
    native=constants(ROOT/'scripts/receivable_term_history_v1.py',['PROFILE','PINS'])
    life=constants(ROOT/'scripts/declared_receivable_lifecycle_v1.py',['PINS'])
    operating=constants(ROOT/'scripts/declared_operating_methods_v1.py',['CLASSES','BINDER_SHA256'])
    clock=constants(ROOT/'scripts/company_method_clock_v1.py',['TRANSITION_SHA256'])
    types=constants(ROOT/'scripts/company_memory_types_v1.py',['ENGINE_SHA256'])
    engine=constants(ROOT/'scripts/company_book_transition_v1.py',['PINS'])
    pins={}
    for group in (native['PINS'],life['PINS'],engine['PINS'],
      {'company_method_clock_v1.py':operating['BINDER_SHA256'],
       'company_book_transition_v1.py':clock['TRANSITION_SHA256']}):
        for n,h in group.items():
            if n in pins:assert pins[n]==h,n
            assert sha256((ROOT/'scripts'/n).read_bytes()).hexdigest()==h,n
            pins[n]=h
    assert types['ENGINE_SHA256']==pins['company_book_transition_v1.py']
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases'];contracts={}
    for chart,case in evidence.items():
        state=case['final'];book=state['book'];price=book['memory_types'][state['unit_cost_pointer']]
        mapping={('opening' if name=='book' else name):name for name in state}
        fields=state['memory_definition']['root']['fields']
        rows=[stage('envelope','record_fields','exact_normalized_state_fields',path=[],fields=list(mapping)),
          stage('profile','equals','term_state_profile',path=['profile'],value=native['PROFILE']),
          stage('typed_book','typed_book','typed_book'),
          stage('claim_shape','map_values','term_claim_type',path=['memory_definition','root','fields','claims'],values=deepcopy(fields['claims']['values'])),
          stage('clock_shape','equals','term_clock_type',path=['memory_definition','root','fields','collection_clock'],value=deepcopy(fields['collection_clock'])),
          stage('roles','role_population','complete_operating_roles',roles=list(operating['CLASSES'])),
          stage('roles_injective','role_injective','injective_operating_roles'),
          stage('role_classes','role_classes','operating_role_class:',classes=[dict(role=k,classification=v) for k,v in operating['CLASSES'].items()]),
          stage('cash_role','cash_role','operating_cash_role',role='cash'),
          stage('cost_leaf','memory_leaf','unit_cost_leaf'),stage('cost_type','memory_type','unit_cost_dimensions',type=deepcopy(price))]
        manifest=dict(profile=s.admission.gate.guarded.PROFILE,method_id='term.structural.cost',version='1',
          inputs={'cost':dict(type=deepcopy(price),role='state',source_ref='Selected cost leaf')},
          requirements=[dict(id='positive_cost',guard=dict(op='const',type=core.BOOL,value=True),guard_requires=[],
            predicate=dict(op='lt',left=dict(op='const',type=deepcopy(price),value='0/1'),right=dict(op='ref',id='cost')),
            requires=['cost'],admission_refs=[],on_false='invalid',on_unknown='unresolved')],
          required_known=[],capabilities=[],residual_prerequisites=['Selected structural cost premise only'])
        rows.extend([stage('positive_cost','predicate','positive_unit_cost',manifest=manifest,bindings={'cost':dict(kind='memory_pointer',type=deepcopy(price))}),
          stage('migration_fields','record_fields','term_migration',path=['migration'],fields=['source_book_sha256','premise','scope']),
          stage('migration_premise','text','migration_premise',path=['migration','premise'],label='migration_premise'),
          stage('migration_scope','equals','migration_scope',path=['migration','scope'],
            value='Imported last assessment and initial terms under supplied no-prior-amendment premise')])
        template=dict(profile=s.admission.PROFILE,context=deepcopy(book['context']),
          dependency_pins=[dict(file=n,sha256=h,reason='native_dependency:'+n) for n,h in pins.items()],stages=rows,
          residuals=['Selected snapshot structural conditions; old internal success label does not grant opening admission'])
        projection=s.bundle.d.f.f.spec_for(state,'terms')
        projection['fields']={'premise':projection['fields']['premise']}
        structure=dict(profile=s.PROFILE,normalization=mapping,template=template,projections={'terms':projection},
          checks=[dict(id='migration_source_digest',op='sha256_format',reason='migration_source_digest',path=['migration','source_book_sha256']),
            dict(id='term_premises',op='projected_nonblank_text',reason='term_premise',projection='terms',field='premise')],
          residuals=['Digest syntax does not establish source availability or migration truth'])
        contracts[chart]=dict(profile=s.CONTRACT,context=deepcopy(book['context']),roles=deepcopy(state['roles']),
          unit_cost_pointer=state['unit_cost_pointer'],structure=structure,semantics=semantic.build(state),
          residuals=['Selected complete supplied synthetic snapshot only; no future-command or new-period admission',
            'Actual history completeness, source provenance and accounting authority remain unadmitted'])
        s.validate_contract(contracts[chart],state)
    dump('contracts.json',contracts)
    dump('preparation.json',dict(contracts=len(contracts),stages_per_contract=15,additional_checks=2,
      native_financial_builder_called=False,dependency_pins=pins,
      semantic_source='data/accounting-master/term-semantic-composition-20261026/declaration.py',
      source_basis='Inspected native constants and previously native-validated retained memory definitions'))
    print(json.dumps(dict(contracts=len(contracts),stages=15,additional_checks=2,dependency_pins=len(pins))))
if __name__=='__main__':main()
