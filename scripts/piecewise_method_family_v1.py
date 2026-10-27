"""Exact conditional piecewise-affine method families; no native admission."""
from copy import deepcopy
from fractions import Fraction as Q
import time
import z3
import joint_measurement_constraints_v1 as joint
import method_monetary_effects_v1 as effects
import conditional_history_family_v1 as history

core, solver = joint.core, joint.solver
PROFILE = 'PiecewiseMethodFamily/1'
BOUNDARY = {**effects.BOUNDARY, 'scope':'conditional_piecewise_monetary_method_only',
            'actual_history':'unknown','executable_opening':None}
MAX_BRANCHES = 64
MAX_TOTAL_NODES = 100000


class BranchLimit(ValueError): pass
class Unsupported(ValueError): pass


def validate(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','method','selected_method_digest','domains',
                           'measurements','obligations','branch_limit'],'method_family')
    core.need(definition['profile']==PROFILE,'profile')
    method=definition['method'];effects.compile_definition(method)
    core.need(definition['selected_method_digest']==core.digest(method),'method_digest_mismatch')
    core.need(type(definition['branch_limit']) is int and 0<=definition['branch_limit']<=MAX_BRANCHES,'branch_limit')
    domains=definition['domains']
    core.need(type(domains) is dict and set(domains)==set(method['inputs']),'complete_input_domains')
    premises,missing={},[]
    def domain(item,where):
        core.closed(item,['interval','premise','source_ref'],'quantity_domain')
        core.text(item['source_ref'],'source_ref');p=item['premise'];joint.premise(p)
        if p is None:missing.append(where)
        elif p['id'] in premises:core.need(premises[p['id']]==p,'conflicting_premise_identity')
        else:premises[p['id']]=deepcopy(p)
        x=item['interval'];core.closed(x,['lower','upper','lower_inclusive','upper_inclusive'],'interval')
        lo,hi=effects.rational(x['lower']),effects.rational(x['upper'])
        core.need(type(x['lower_inclusive']) is bool and type(x['upper_inclusive']) is bool,'endpoint_inclusion')
        core.need(lo<hi or lo==hi and x['lower_inclusive'] and x['upper_inclusive'],'nonempty_interval')
    for key,item in domains.items():domain(item,'input:'+key)
    types={'calculation':{r['id']:r['type'] for r in method['calculations']},
           'journal':method['accounts'],
           'flow':{r['id']:method['accounts'][method['cash_account']] for r in method['flows']}}
    core.need(type(definition['measurements']) is list and len(definition['measurements'])<=256,'measurement_limit')
    ids=set()
    for row in definition['measurements']:
        core.closed(row,['id','category','target','type','domain'],'output_measurement')
        core.text(row['id'],'measurement_id');core.need(row['id'] not in ids,'duplicate_measurement');ids.add(row['id'])
        core.need(type(row['category']) is str and row['category'] in types,'output_category')
        core.text(row['target'],'output_target');core.need(row['target'] in types[row['category']],'output_target')
        core.need(row['type']==types[row['category']][row['target']],'measurement_type_mismatch')
        domain(row['domain'],'measurement:'+row['id'])
    core.need(type(definition['obligations']) is list and len(definition['obligations'])<=256,'obligation_limit')
    ids=set()
    for row in definition['obligations']:
        core.closed(row,['id','meaning','affects'],'obligation');core.text(row['id'],'obligation_id')
        core.need(row['id'] not in ids,'duplicate_obligation');ids.add(row['id'])
        core.text(row['meaning'],'meaning');core.identifiers(row['affects'],'affects',nonempty=True)
    core.closed(budget,joint.BUDGET_FIELDS,'budget');limit=solver.Budget(**budget)
    core.need(limit.max_slots==0 and limit.max_integer_assignments<=1 and limit.max_cells<=MAX_BRANCHES,'family_budget_scope')
    core.need(limit.max_formula_nodes<=MAX_TOTAL_NODES and limit.elapsed_ms<=60000 and
              limit.solver_timeout_ms<=10000 and limit.solver_rlimit<=10000000,'reference_runtime_limit')
    return premises,missing,limit


def clone(state):
    return {key:(list(value) if isinstance(value,list) else dict(value)) for key,value in state.items()}


def interval_formula(value,x):
    return solver.domain_formula(value,{'lower':x['lower'],'upper':x['upper'],
        'lower_closed':x['lower_inclusive'],'upper_closed':x['upper_inclusive']})


def compile_family(definition,budget):
    premises,missing,limit=validate(definition,budget)
    method=definition['method'];cap=definition['branch_limit']
    if cap==0:raise BranchLimit('branch_cap')
    variables={name:z3.Real('method.input.'+str(i)) for i,name in enumerate(sorted(method['inputs']))}
    symbols={}
    for key,var in variables.items():
        interval=definition['domains'][key]['interval']
        fixed=interval['lower']==interval['upper']
        symbols[key]=(solver.q(interval['lower']) if fixed else var,not fixed)
    initial={'symbols':symbols,'conditions':[],'decisions':[],
             'calculations':{},'journal':{key:solver.q(0) for key in method['accounts']},'flows':{}}
    def bounded(rows):
        if len(rows)>cap:raise BranchLimit('branch_cap')
        return rows
    def expression(node,state,path):
        op=node['op']
        if op=='ref':
            value,symbolic=state['symbols'][node['id']];return [(state,value,symbolic)]
        if op=='const':return [(state,solver.q(node['value']),False)]
        rows=[]
        for left_state,left,left_symbolic in expression(node['left'],state,path+'/left'):
            for right_state,right,right_symbolic in expression(node['right'],left_state,path+'/right'):
                symbolic=left_symbolic or right_symbolic
                if op=='mul' and left_symbolic and right_symbolic:
                    raise Unsupported('unknown_by_unknown_product:'+path)
                if op=='min' and symbolic:
                    for arm,condition,value in [('left',left<=right,left),('right',right<left,right)]:
                        branch=clone(right_state)
                        branch['conditions'].append((core.canonical(['min',path,arm]).decode(),condition))
                        branch['decisions'].append({'path':path,'arm':arm,
                            'left':left.sexpr(),'right':right.sexpr()})
                        rows.append((branch,value,True))
                else:
                    if op=='add':value=left+right
                    elif op=='sub':value=left-right
                    elif op=='mul':value=left*right
                    else:value=left if solver.fraction(left)<=solver.fraction(right) else right
                    rows.append((right_state,z3.simplify(value),symbolic))
                bounded(rows)
        return rows
    states=[initial]
    for group in ['calculations','postings','flows']:
        for row in method[group]:
            updated=[]
            for state in states:
                for branch,value,symbolic in expression(row['expression'],state,group+'/'+row['id']):
                    branch=clone(branch)
                    if group=='calculations':
                        branch['symbols'][row['id']]=(value,symbolic)
                        branch['calculations'][row['id']]=value
                    elif group=='postings':branch['journal'][row['account']]+=value
                    else:branch['flows'][row['id']]=value
                    updated.append(branch);bounded(updated)
            states=updated
    branches=[];total_nodes=0
    for index,state in enumerate(states):
        total=z3.simplify(sum(state['journal'].values(),solver.q(0)),som=True)
        cash=z3.simplify(sum(state['flows'].values(),solver.q(0))-state['journal'][method['cash_account']],som=True)
        if not z3.is_rational_value(total) or solver.fraction(total)!=0:
            raise Unsupported('unproved_journal_identity')
        if not z3.is_rational_value(cash) or solver.fraction(cash)!=0:
            raise Unsupported('unproved_cash_flow_identity')
        p=solver.Problem('piecewise_method','explicit_authored_method_family',variables=variables)
        for name,var in variables.items():p.add('domain:'+name,interval_formula(var,definition['domains'][name]['interval']))
        for label,condition in state['conditions']:p.add(label,condition)
        for row in definition['measurements']:
            group={'calculation':'calculations','journal':'journal','flow':'flows'}[row['category']]
            p.add('measurement:'+row['id'],interval_formula(state[group][row['target']],row['domain']['interval']))
        outputs={group:{key:z3.simplify(value).sexpr() for key,value in state[group].items()}
                 for group in ['calculations','journal','flows']}
        manifest={'index':index,'decisions':state['decisions'],'outputs':outputs,
                  'constraints':[{'id':key,'formula':value.sexpr()} for key,value in p.constraints]}
        manifest['sha256']=core.digest(manifest)
        total_nodes += sum(solver.nodes(formula) for _,formula in p.constraints)
        total_nodes += sum(solver.nodes(formula) for group in ['calculations','journal','flows']
                           for formula in state[group].values())
        if total_nodes>MAX_TOTAL_NODES:raise BranchLimit('total_formula_node_cap')
        branches.append({'problem':p,'manifest':manifest,'state':state})
    return branches,premises,missing,limit


def replay_witness(definition,budget,index,witness):
    branches,_,missing,_=compile_family(definition,budget)
    core.need(not missing,'unresolved_premise')
    core.need(type(index) is int and 0<=index<len(branches),'branch_index')
    core.need(type(witness) is dict and set(witness)==set(definition['domains']),'complete_input_witness')
    values={}
    for key,value in witness.items():
        q=effects.rational(value)
        core.need(history.in_domain(q,definition['domains'][key]['interval']),'input_domain:'+key)
        values[key]={'status':'known','value':value}
    method=definition['method'];digest=definition['selected_method_digest']
    result=effects.derive({digest:method},digest,values)
    core.need(result['status']=='derived','original_method_replay:'+result.get('reason',result['status']))
    calculations={row['id']:row['binding']['value'] for row in result['diagnostics']['calculations']}
    outputs={'calculation':calculations,'journal':result['journal'],
             'flow':{row['id']:row['amount'] for row in result['flows']}}
    for row in definition['measurements']:
        core.need(history.in_domain(Q(outputs[row['category']][row['target']]),row['domain']['interval']),
                  'output_measurement:'+row['id'])
    chosen={d['path']:d['arm'] for d in branches[index]['manifest']['decisions']}
    visited={};symbols={k:Q(v) for k,v in witness.items()}
    def evaluate(node,path):
        op=node['op']
        if op=='ref':return symbols[node['id']]
        if op=='const':return effects.rational(node['value'])
        a,b=evaluate(node['left'],path+'/left'),evaluate(node['right'],path+'/right')
        if op=='min':
            arm='left' if a<=b else 'right'
            if path in chosen:
                core.need(chosen[path]==arm,'wrong_minimum_arm');visited[path]=arm
            return min(a,b)
        return effects.bounded(a+b if op=='add' else a-b if op=='sub' else a*b)
    replay={'calculations':{},'journal':{k:Q(0) for k in method['accounts']},'flows':{}}
    for group in ['calculations','postings','flows']:
        for row in method[group]:
            value=evaluate(row['expression'],group+'/'+row['id'])
            if group=='calculations':symbols[row['id']]=value;replay['calculations'][row['id']]=effects.fmt(value)
            elif group=='postings':replay['journal'][row['account']]+=value
            else:replay['flows'][row['id']]=effects.fmt(value)
    replay['journal']={k:effects.fmt(v) for k,v in replay['journal'].items()}
    core.need(visited==chosen,'incomplete_branch_replay')
    core.need(replay['calculations']==calculations and replay['journal']==result['journal'] and
              replay['flows']==outputs['flow'],'original_evaluator_mismatch')
    branch=branches[index]
    substitutions=[(branch['problem'].variables[k],solver.q(v)) for k,v in witness.items()]
    for group in ['calculations','journal','flows']:
        for key,expression in branch['state'][group].items():
            actual=solver.fraction(z3.substitute(expression,*substitutions))
            core.need(actual==Q(replay[group][key]),'compiled_output_mismatch:'+group+':'+key)
    return {'inputs':deepcopy(witness),'calculations':calculations,'journal':result['journal'],
            'flows':result['flows'],'branch_decisions':visited,'checked_exactly':True,
            'original_method_status':result['status'],'native_preconditions_checked':False}


def assess(definition,budget):
    started=time.monotonic()
    try:
        premises,missing,limit=validate(definition,budget)
        complete=not missing and not definition['obligations']
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),
              'definition_sha256':core.digest(definition),'budget':deepcopy(budget),
              'premises':premises,'missing_premises':missing,
              'target_obligations':deepcopy(definition['obligations']),
              'formulation_complete':complete,'target_existence':'unknown',
              'candidate_feasibility':'unknown','declared_search':'not_started',
              'economic_scope':'explicitly_limited' if complete else 'unresolved'}
        if missing:return {**base,'status':'unresolved'}
        try:branches,_,_,_=compile_family(definition,budget)
        except BranchLimit as exc:
            return {**base,'status':'unknown','reason':str(exc),'branch_partition_complete':False}
        except Unsupported as exc:
            return {**base,'status':'unsupported','reason':str(exc),'branch_partition_complete':False}
        manifest=[b['manifest'] for b in branches]
        results=[];attempted=0
        for index,branch in enumerate(branches):
            remaining=limit.elapsed_ms-int(1000*(time.monotonic()-started))
            if attempted>=limit.max_cells or remaining<=0 or limit.max_integer_assignments==0:
                results.append({'index':index,'status':'unvisited','reason':'global_cell_time_or_assignment_limit'})
                continue
            attempted+=1
            branch_budget={**budget,'max_cells':1,'elapsed_ms':remaining}
            r=solver.solve(branch['problem'],solver.Budget(**branch_budget))
            cells=r['cells']
            if r['feasibility']=='Feasible':
                cell=next(c for c in cells if c['feasibility']=='sat')
                witness={k:effects.fmt(Q(v)) for k,v in cell['witness'].items()}
                results.append({'index':index,'status':'feasible','witness':witness,
                                'replay':replay_witness(definition,budget,index,witness)})
            elif r['feasibility']=='Infeasible':
                core.need(r['coverage'].get('complete',False) and len(cells)==1 and
                          cells[0]['conflict']['rechecked']=='unsat','unchecked_branch_infeasibility')
                results.append({'index':index,'status':'infeasible','conflict':deepcopy(cells[0]['conflict'])})
            else:
                results.append({'index':index,'status':'unknown','reason':r.get('reason') or r['status']})
        feasible=sum(row['status']=='feasible' for row in results)
        infeasible=sum(row['status']=='infeasible' for row in results)
        decided=feasible+infeasible
        coverage={'total':len(branches),'attempted':attempted,'feasible':feasible,'infeasible':infeasible,
                  'unresolved':len(branches)-decided,'complete':decided==len(branches)}
        answer={**base,'branch_partition_complete':True,'branch_manifest':manifest,'branches':results,
                'coverage':coverage,'solver_version':z3.get_version_string(),
                'declared_search':'complete' if coverage['complete'] else 'partial',
                'wall_seconds':time.monotonic()-started}
        if feasible:
            return {**answer,'status':'conditional_family_witness' if complete else 'candidate_with_unresolved_obligations',
                    'candidate_feasibility':'conditionally_feasible',
                    'target_existence':'conditional_witness' if complete else 'unknown'}
        if coverage['complete']:
            return {**answer,'status':'conditionally_infeasible','candidate_feasibility':'conditionally_infeasible',
                    'target_existence':'conditionally_empty' if complete else 'unknown'}
        return {**answer,'status':'unknown'}
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}


def verify_result(definition,budget,result):
    try:
        current=assess(definition,budget)
        core.need(type(result) is dict and set(result)==set(current),'result_fields')
        for key in current:
            if key not in ['branches','wall_seconds']:core.need(result[key]==current[key],'result_changed:'+key)
        if 'wall_seconds' in result:
            core.need(type(result['wall_seconds']) in [int,float] and
                      0<=result['wall_seconds']<float('inf'),'invalid_timing')
        if 'branches' not in result:return True
        core.need(type(result['branches']) is list and len(result['branches'])==len(current['branches']),'branch_count')
        compiled,_,missing,_=compile_family(definition,budget)
        core.need(not missing,'missing_premises')
        for row,expected in zip(result['branches'],current['branches']):
            core.need(type(row) is dict and set(row)==set(expected),'branch_fields')
            for key in expected:
                if key not in ['witness','replay','conflict']:core.need(row[key]==expected[key],'branch_changed:'+key)
            if row['status']=='feasible':
                core.need(row['replay']==replay_witness(definition,budget,row['index'],row['witness']),'replay_changed')
            if row['status']=='infeasible':
                conflict=row['conflict'];core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                formulas=dict(compiled[row['index']]['problem'].constraints)
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                core.need(budget['solver_timeout_ms']>0 and budget['solver_rlimit']>0,'conflict_budget')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'conflict_not_unsat')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception):return False
