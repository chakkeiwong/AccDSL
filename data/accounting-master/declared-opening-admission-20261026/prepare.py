from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import ast,json
import admission as a
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def dump(name,v):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+chr(10))
def read(p):return json.loads(p.read_text())
def constants(file,names):
    values={}
    for node in ast.parse(file.read_text()).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in names:values[target.id]=ast.literal_eval(node.value)
    assert set(values)==set(names);return values
def ref(name):return dict(op='ref',id=name)
def const(typ,value):return dict(op='const',type=deepcopy(typ),value=value)
def binary(op,left,right):return dict(op=op,left=left,right=right)
def source(path,typ):return dict(kind='path',path=path,type=deepcopy(typ))
def stage(name,op,reason,**fields):return dict(id=name,op=op,reason=reason,**fields)
def predicate(name,reason,bindings,expr):
    manifest=dict(profile=a.gate.guarded.PROFILE,method_id='opening.'+name,version='1',
        inputs={k:dict(type=deepcopy(s['type']),role='state',source_ref='Explicit native opening input binding') for k,s in bindings.items()},
        requirements=[dict(id=name,guard=const(a.core.BOOL,True),guard_requires=[],predicate=expr,requires=list(bindings),
                           admission_refs=[],on_false='invalid',on_unknown='unresolved')],
        required_known=[],capabilities=[],residual_prerequisites=['Selected synthetic empty-opening contract only'])
    return stage(name,'predicate',reason,manifest=manifest,bindings=bindings)
def main():
    assert not (HERE/'templates').exists(),'Do not rerun preparation'
    lifecycle=constants(ROOT/'scripts/declared_receivable_lifecycle_v1.py',['PROFILE','POLICY','PINS','MAX_COMMANDS'])
    operating=constants(ROOT/'scripts/declared_operating_methods_v1.py',['CLASSES','BINDER_SHA256'])
    pins=[dict(file=name,sha256=h,reason='dependency_hash:'+name) for name,h in lifecycle['PINS'].items()]
    pins.append(dict(file='company_method_clock_v1.py',sha256=operating['BINDER_SHA256'],reason='binder_dependency_hash'))
    for owner in ('alpha','beta'):
        b=read(HERE.parent/f'declarative-event-program-20261026/examples/{owner}.native-input.json');book=b['opening']
        text=a.gate.TEXT;date=a.gate.DATE;money=a.base.money_type(book);price=book['memory_types'][b['unit_cost_pointer']]
        rows=[stage('envelope','record_fields','fields:company_book',path=[],fields=list(b)),
              stage('profile','equals','profile',path=['profile'],value=lifecycle['PROFILE']),
              stage('name','text','text:name',path=['name'],label='name'),
              stage('policy_fields','record_fields','fields:company_book',path=['policy'],fields=['profile','past_due','carry','provenance'])]
        bindings={k:source(['policy',k],text) for k in ('profile','past_due','carry')}
        values={'profile':lifecycle['POLICY'],'past_due':'strictly_after_due_date','carry':'preserve_all_memory'}
        rows.append(stage('policy','record_values','explicit_policy',path=['policy'],values=values))
        rows.extend([stage('policy_provenance','text','text:policy_provenance',path=['policy','provenance'],label='policy_provenance'),
            stage('typed_book','typed_book','typed_book'),
            stage('claim_shape','map_values','claim_type_contract',path=['memory_definition','root','fields','claims'],values=deepcopy(b['memory_definition']['root']['fields']['claims']['values'])),
            stage('clock_shape','equals','clock_type_contract',path=['memory_definition','root','fields','collection_clock'],value=deepcopy(b['memory_definition']['root']['fields']['collection_clock'])),
            stage('empty_claims','equals','empty_opening_claim_population_required',path=['opening','memory','claims'],value={}),
            predicate('cursor','opening_cursor',{'cursor':source(['opening','memory','collection_clock','cursor'],date),'day':source(['opening','date'],date)},binary('eq',ref('cursor'),ref('day'))),
            stage('roles','role_population','complete_operating_roles',roles=list(operating['CLASSES'])),
            stage('roles_injective','role_injective','injective_operating_roles'),
            stage('role_classes','role_classes','operating_role_class:',classes=[dict(role=k,classification=v) for k,v in operating['CLASSES'].items()]),
            stage('cash_role','cash_role','operating_cash_role',role='cash'),
            stage('cost_leaf','memory_leaf','unit_cost_leaf'),
            stage('cost_type','memory_type','unit_cost_dimensions',type=deepcopy(price)),
            predicate('positive_cost','positive_unit_cost',{'cost':dict(kind='memory_pointer',type=deepcopy(price))},binary('lt',const(price,'0/1'),ref('cost'))),
            predicate('claim_total','claim_receivable_sum',{'receivable':dict(kind='role_balance',role='receivables',type=deepcopy(money))},binary('eq',const(money,'0/1'),ref('receivable'))),
            stage('report','opening_report','opening_report:'),
            stage('commands','commands','command_limit',maximum=lifecycle['MAX_COMMANDS'])])
        template=dict(profile=a.PROFILE,context=deepcopy(book['context']),dependency_pins=deepcopy(pins),stages=rows,
                      residuals=['Exact retained empty-opening conditions; future commands evaluated separately',
                                 'No source or accounting admission'])
        a.compile_template(template);dump(f'templates/{owner}.json',template)
    lock=read(HERE.parent/'declarative-event-program-20261026/source-lock.json')
    for folder in (HERE.parent/'opening-admission-audit-20261026',HERE.parent/'declarative-event-program-20261026'):
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ('.py','.json','.md'):lock[str(p.relative_to(ROOT))]=sha256(p.read_bytes()).hexdigest()
    for name,h in lock.items():assert sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    dump('source-lock.json',lock)
    dump('provenance.json',dict(template_source='Explicit ordered declarations from audited native validate/build/report obligations',
         policy_source='scripts/declared_receivable_lifecycle_v1.py',role_source='scripts/declared_operating_methods_v1.py',
         type_source='Retained typed opening memory definitions, chart-specific',native_builder_called=False))
    print(json.dumps(dict(templates=2,stages_per_template=21,protected_files=len(lock))))
if __name__=='__main__':main()
