"""Finite exact envelopes of typed outcomes over a complete native sequence."""
from copy import deepcopy
from fractions import Fraction as Q
import time
import sequential_outcome_query_v1 as query
family,core,solver,z3,native=query.family,query.core,query.solver,query.z3,query.native
PROFILE='SequentialOutcomeRange/1'
BOUNDARY={**query.BOUNDARY,'scope':'finite_typed_envelope_of_complete_settlement_sale_family'}

def predicate_request(request):
    core.need(len(core.canonical(request))<=core.MAX_BYTES,'request_size_limit')
    core.closed(request,['profile','family','prefix','type','terms'],'outcome_range')
    core.need(request['profile']==PROFILE,'profile')
    return {**deepcopy(request),'profile':query.PROFILE,'operator':'eq','threshold':'0/1'}

def validate(request,budget):
    definition=predicate_request(request)
    query.validate(definition,budget)
    return definition

def replay_value(request,budget,index,witness):
    validate(request,budget)
    replay=family.replay_witness(request['family'],budget,index,witness)
    state=replay['first']['after'] if request['prefix']==1 else replay['after']
    value=sum((Q(t['coefficient'])*Q(state['balances'][t['account']]) for t in request['terms']),Q(0))
    return {'value':native.monetary.fmt(value),'original_complete_replay':replay,'committed':False}

def proof_checks(branch,expression,side,value,budget,started):
    """Certify a closure endpoint, no better original value and attainment."""
    original=[x for _,x in branch['problem'].constraints]
    closure=[solver.close(z3.simplify(x)) for x in original]
    bound=solver.q(value)
    def check(formulas):
        remaining=budget['elapsed_ms']-int(1000*(time.monotonic()-started))
        if remaining<=0 or budget['solver_timeout_ms']==0 or budget['solver_rlimit']==0:return 'unknown'
        engine=z3.Solver();engine.set(timeout=min(remaining,budget['solver_timeout_ms']),rlimit=budget['solver_rlimit'])
        engine.add(*formulas);return str(engine.check())
    better=expression<bound if side=='lower' else expression>bound
    return {'closure_endpoint':check(closure+[expression==bound]),
            'no_better':check(original+[better]),'attainment':check(original+[expression==bound])}

def aggregate(rows):
    feasible=[r for r in rows if r['status']=='feasible']
    complete=bool(rows) and all(r['status']=='infeasible' or
               r['status']=='feasible' and all(e['certified'] for e in r['bounds'].values()) for r in rows)
    if not complete:return {'status':'unknown','nonempty':bool(feasible),'globally_certified':False,'bounds':None}
    if not feasible:return {'status':'empty_family','nonempty':False,'globally_certified':False,'bounds':None}
    bounds={}
    for side in ['lower','upper']:
        extreme=(min if side=='lower' else max)(Q(r['bounds'][side]['value']) for r in feasible)
        extremizers=[r for r in feasible if Q(r['bounds'][side]['value'])==extreme]
        bounds[side]={'value':native.monetary.fmt(extreme),'attained':any(r['bounds'][side]['attained'] for r in extremizers),
                      'supporting_branches':[r['index'] for r in extremizers],
                      'attaining_branches':[r['index'] for r in extremizers if r['bounds'][side]['attained']]}
    return {'status':'finite_envelope','nonempty':True,'globally_certified':True,'bounds':bounds}

def assess(request,budget):
    started=time.monotonic()
    try:
        definition=validate(request,budget)
        base={'profile':PROFILE,**BOUNDARY,'request':deepcopy(request),'request_sha256':core.digest(request),
              'family_sha256':core.digest(request['family']),'budget':deepcopy(budget),
              'range_meaning':'outer_envelope_not_interior_attainability'}
        try:
            branches,premises,missing,limit,meta,stop=family.compile_selection(request['family'],budget)
        except family.piecewise.BranchLimit as exc:
            return {**base,'status':'unknown','reason':str(exc),'branch_partition_complete':False}
        except family.piecewise.Unsupported as exc:
            return {**base,'status':'unsupported','reason':str(exc),'branch_partition_complete':False}
        obligations=deepcopy(request['family']['first_family']['obligations'])+deepcopy(request['family']['obligations'])
        base.update(premises=premises,missing_premises=missing,target_obligations=obligations,
                    formulation_complete=not missing and not obligations,
                    answer_target='declared_conditional_family' if not obligations else 'candidate_family_with_unresolved_obligations')
        if stop or missing:return {**base,'status':stop or 'unresolved','reason':'parent_formulation_incomplete'}
        rows=[];attempted=0
        for index,branch in enumerate(branches):
            remaining=limit.elapsed_ms-int(1000*(time.monotonic()-started))
            if attempted>=limit.max_cells or remaining<=0 or limit.max_integer_assignments==0:
                rows.append({'index':index,'status':'unvisited','reason':'global_cell_time_or_assignment_limit'});continue
            attempted+=1
            expression=query.expression(definition,branch)
            result=solver.solve(branch['problem'],solver.Budget(**{**budget,'max_cells':1,'elapsed_ms':remaining}),objective=expression)
            cells=result['cells'];core.need(result['coverage']['total'] in [None,1],'unexpected_range_partition')
            if result['feasibility']=='Infeasible':
                core.need(result['coverage']['complete'] and len(cells)==1 and cells[0]['conflict']['rechecked']=='unsat','unchecked_branch_infeasibility')
                rows.append({'index':index,'status':'infeasible','conflict':deepcopy(cells[0]['conflict'])});continue
            if result['feasibility']!='Feasible':
                rows.append({'index':index,'status':'unknown','reason':result.get('reason') or result['status']});continue
            cell=next(c for c in cells if c['feasibility']=='sat')
            witness={k:native.monetary.fmt(Q(v)) for k,v in cell['witness'].items()}
            row={'index':index,'status':'feasible','witness':witness,'replay':replay_value(request,budget,index,witness),'bounds':{}}
            for side,endpoint in cell['bounds'].items():
                core.need(endpoint['status']!='Unbounded','unbounded_in_finite_fragment')
                if not endpoint['certified']:
                    row['bounds'][side]={'status':'unknown','certified':False,'reason':'solver_endpoint_not_certified'};continue
                core.need(endpoint['status']=='Finite','finite_endpoint_required')
                value=native.monetary.fmt(Q(endpoint['value']))
                proofs=proof_checks(branch,expression,side,value,budget,started)
                if 'unknown' in proofs.values():
                    row['bounds'][side]={'status':'unknown','certified':False,'reason':'endpoint_recheck_resource_unknown','proof':proofs};continue
                core.need(proofs['closure_endpoint']=='sat' and proofs['no_better']=='unsat','invalid_endpoint_proof')
                attained=proofs['attainment']=='sat'
                core.need(attained==endpoint['attained'],'endpoint_attainment_mismatch')
                checked={'status':'finite','certified':True,'value':value,'attained':attained,'proof':proofs,
                         'witness':None,'replay':None}
                if attained:
                    w={k:native.monetary.fmt(Q(v)) for k,v in endpoint['witness'].items()}
                    replay=replay_value(request,budget,index,w)
                    core.need(replay['value']==value,'endpoint_original_value_mismatch')
                    checked.update(witness=w,replay=replay)
                row['bounds'][side]=checked
            rows.append(row)
        decided=sum(r['status']=='infeasible' or r['status']=='feasible' and all(e['certified'] for e in r['bounds'].values()) for r in rows)
        return {**base,'status':'conditional_outcome_range' if not obligations else 'candidate_outcome_range',
                'branch_partition_complete':True,'branch_manifest':[b['manifest'] for b in branches],
                'branches':rows,'range':aggregate(rows),'coverage':{'total':len(rows),'attempted':attempted,
                'decided':decided,'unresolved':len(rows)-decided,'complete':decided==len(rows)},
                'solver_version':z3.get_version_string(),'wall_seconds':time.monotonic()-started}
    except (family.parent.Halt,native.structure.native.Rejected) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':exc.status,'reason':str(exc)[:300]}
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception,solver.UnsupportedFragment) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}

def verify_result(request,budget,result):
    try:
        current=assess(request,budget)
        core.need(type(result) is dict and set(result)==set(current),'result_fields')
        for key in current:
            if key not in ['branches','wall_seconds']:core.need(result[key]==current[key],'result_changed:'+key)
        if 'wall_seconds' in result:core.need(type(result['wall_seconds']) in [int,float] and 0<=result['wall_seconds']<float('inf'),'invalid_timing')
        if 'branches' not in result:return True
        branches,_,missing,_,_,stop=family.compile_selection(request['family'],budget)
        core.need(not missing and stop is None,'incomplete_parent')
        core.need(type(result['branches']) is list and len(result['branches'])==len(current['branches']),'branch_count')
        for row,expected in zip(result['branches'],current['branches']):
            core.need(type(row) is dict and set(row)==set(expected),'branch_fields')
            for key in expected:
                if key not in ['witness','replay','bounds','conflict']:core.need(row[key]==expected[key],'branch_changed:'+key)
            if row['status']=='feasible':
                core.need(row['replay']==replay_value(request,budget,row['index'],row['witness']),'feasible_replay_changed')
                core.need(type(row['bounds']) is dict and set(row['bounds'])=={'lower','upper'},'endpoint_fields')
                for side,endpoint in row['bounds'].items():
                    target=expected['bounds'][side]
                    core.need(type(endpoint) is dict and set(endpoint)==set(target),'endpoint_fields')
                    for key in target:
                        if key not in ['witness','replay']:core.need(endpoint[key]==target[key],'endpoint_changed:'+key)
                    if not endpoint['certified']:continue
                    if endpoint['attained']:
                        replay=replay_value(request,budget,row['index'],endpoint['witness'])
                        core.need(endpoint['replay']==replay and replay['value']==endpoint['value'],'endpoint_replay_changed')
                    else:core.need(endpoint['witness'] is None and endpoint['replay'] is None,'unattained_witness')
            elif row['status']=='infeasible':
                conflict=row['conflict'];core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                formulas=dict(branches[row['index']]['problem'].constraints)
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                core.need(budget['solver_timeout_ms']>0 and budget['solver_rlimit']>0,'conflict_budget')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'conflict_not_unsat')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception):return False
