"""Bounded ordered source program over the unchanged selected term executor."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'term-event-source-20261026'))
import event_text as source
core=source.core
PROFILE='SelectedTermProgram/1'
SELECTION='SelectedTermProgramSelection/1'
MAX_COMMANDS=64
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,durable=False,committed=False)

def identities(program):
    """Transport identities only; computing these does not review a selection."""
    return dict(program_sha256=core.digest(program),program_order_sha256=source.full.p.order_digest(program),
                contract_source_sha256=sha256(program['contract_source'].encode('utf-8')).hexdigest(),
                rule_source_sha256={k:sha256(v.encode('utf-8')).hexdigest() for k,v in program['rule_sources'].items()})

def compile_program(program,selection,expected_selection_sha256):
    core.closed(program,['profile','name','contract_source','rule_sources','opening','coverage','commands'],'term_program')
    core.need(program['profile']==PROFILE,'program_profile')
    core.need(type(program['name']) is str and bool(program['name']),'program_name')
    source.full.p.base.binding.bounded(program)
    core.need(len(core.canonical(program))<=core.MAX_BYTES,'program_size')
    core.need(type(program['commands']) is list and 1<=len(program['commands'])<=MAX_COMMANDS,'command_population')
    ids=set()
    for command in program['commands']:
        core.closed(command,['id','request'],'program_command')
        core.need(type(command['id']) is str and bool(command['id']) and command['id'] not in ids,'command_identity')
        core.need(type(command['request']) is dict,'command_request')
        ids.add(command['id'])
    core.closed(selection,['profile','program_sha256','program_order_sha256','contract_source_sha256','rule_source_sha256','term_selection'],'program_selection')
    core.need(selection['profile']==SELECTION,'selection_profile')
    core.need(type(expected_selection_sha256) is str and core.digest(selection)==expected_selection_sha256,'external_selection_identity')
    identity=identities(program)
    for k,v in identity.items():core.need(selection[k]==v,'selected_'+k)
    core.closed(program['rule_sources'],['assessment','amendment','collection','carry'],'program_rule_sources')
    opening=program['opening'];definition=opening['memory_definition']
    contract=source.ct.compile_text(program['contract_source'],definition)['contract']
    rules={}
    for name,text in program['rule_sources'].items():
        item=source.lower(text,carry=True) if name=='carry' else source.compile_rule(text,opening['book'],definition)
        rules[name]=item['rule']
    core.need(selection['term_selection']==source.full.selection_for(contract,rules),'reviewed_term_selection')
    return dict(profile=PROFILE,status='compiled_structural',contract=contract,rules=rules,identities=identity,
                selection_sha256=expected_selection_sha256,**FLAGS)

def execute(program,selection,expected_selection_sha256):
    """No auto-selection, population synthesis, request rewrite or durable effects."""
    stage='compile'
    try:
        compiled=compile_program(program,selection,expected_selection_sha256)
    except (ValueError,KeyError,TypeError,IndexError,RecursionError,OverflowError) as exc:
        return dict(profile=PROFILE,status='invalid_program',executed=False,successful_commands=0,
                    failed_index=None,failed_stage=stage,reason=getattr(exc,'reason',str(exc))[:350],
                    location=getattr(exc,'location',None),steps=[],**FLAGS)
    state=deepcopy(program['opening']);coverage=deepcopy(program['coverage']);steps=[]
    result=dict(profile=PROFILE,**FLAGS,executed=True,selection_sha256=expected_selection_sha256,
                **compiled['identities'])
    for index,command in enumerate(program['commands']):
        request=deepcopy(command['request'])
        call=source.full.make_call(compiled['contract'],compiled['rules'],state,request,coverage,selection['term_selection'])
        try:
            actual=source.execute_sources(program['contract_source'],program['rule_sources'],state['memory_definition'],
                         state,request,coverage,selection['term_selection'],call)
        except (ValueError,KeyError,TypeError,IndexError,RecursionError,OverflowError) as exc:
            actual=dict(execution=dict(status='invalid',failed_stage='source',reason=getattr(exc,'reason',str(exc))[:350]),
                        source_diagnostics=[dict(location=getattr(exc,'location',None))])
        if actual['execution']['status']!='proposed':
            return dict(result,status='partial' if steps else 'refused',successful_commands=len(steps),steps=steps,
                        failed_index=index,failed_command=deepcopy(command),failed_result=actual,
                        remaining_commands=deepcopy(program['commands'][index+1:]),after=state,coverage_after=coverage)
        steps.append(dict(id=command['id'],result=actual))
        state=deepcopy(actual['execution']['after']);coverage=deepcopy(actual['execution']['coverage_after'])
    return dict(result,status='complete_provisional',successful_commands=len(steps),steps=steps,
                failed_index=None,failed_command=None,failed_result=None,remaining_commands=[],after=state,coverage_after=coverage)
