"""Isolate equal effective dates in an independently native-valid input."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import importlib.util,json
import event_declarations as d
m=d.m;HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
import receivable_term_history_v1 as native
spec=importlib.util.spec_from_file_location('boundary_population',HERE.parent/'term-semantic-composition-20261026/declaration.py')
population=importlib.util.module_from_spec(spec);spec.loader.exec_module(population)
def read(p):return json.loads(p.read_text())
out=HERE/'date-boundary.json';assert not out.exists(),'evidence_exists'
case=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']['alpha']
state=deepcopy(case['steps'][0]['before']);state['book']['date']='2027-03-10'
state['book']['memory']['collection_clock']['cursor']='2027-01-02'
row=state['book']['memory']['claims']['invoice/a~1']
row['terms']['initial'].update(effective='2027-03-10',due='2027-04-30');row['due']='2027-04-30'
row['assessments']={};row.update(assessed=False,assessment_date='2027-01-02',assessed_remaining='0/1',overdue='0/1',latest_assessment='none')
derived=d.c.types.derive(state['memory_definition'],state['book']['memory'],state['book']);assert derived['status']=='typed'
state['book'].update(memory_schema=derived['schema_sha256'],memory_types=derived['memory_types']);state['schemas'][derived['schema_sha256']]=derived['schema']
native.validate(state)
request=deepcopy(case['steps'][0]['request']);request['expected_state_sha256']=m.core.digest(state);request['event']['date']='2027-03-10'
oracle=native.step(state,request);assert oracle['status']=='invalid' and oracle['reason']=='ambiguous_term_effective_date'
contract=read(HERE.parent/'term-structural-admission-20261026/contracts.json')['alpha'];rules=read(HERE/'attempt-01/rules.json')['alpha']
cov=population.populations(state,contract['semantics']);selected=m.selection_for(contract,rules)
saved=native.validate;native.validate=lambda *a,**k:(_ for _ in ()).throw(AssertionError('native_callback'))
try:result=m.execute(contract,rules,state,request,cov,selected,m.make_call(contract,rules,state,request,cov,selected))
finally:native.validate=saved
assert result['status']=='invalid' and result['reason']=='ambiguous_term_effective_date' and result['failed_stage']=='eligibility'
assert 'after' not in result and not result['provisional_transition']
out.write_text(json.dumps(dict(passed=True,before=state,request=request,native=oracle,result=result,
  note='Repaired test fixture preserves book chronology and derives leaf types after removing assessments; no candidate change',
  implementation_sha256={name:sha256((HERE/name).read_bytes()).hexdigest() for name in ['full_composition.py','nested_gate.py','date-boundary.py']}),indent=2)+chr(10))
print(json.dumps(dict(passed=True,reason=result['reason'],failed_stage=result['failed_stage'])))
