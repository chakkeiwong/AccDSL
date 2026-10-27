"""Possible/necessary scalar outcomes of complete conditional native sequences."""
from copy import deepcopy
from fractions import Fraction as Q
import time
import sequential_return_state_family_v1 as family
core,solver,z3,native=family.core,family.solver,family.z3,family.native
PROFILE='SequentialOutcomeQuery/1'
BOUNDARY={**family.BOUNDARY,'scope':'typed_scalar_query_on_complete_settlement_sale_family',
          'actual_outcome':'unknown'}
OPS={'eq':lambda a,b:a==b,'lt':lambda a,b:a<b,'le':lambda a,b:a<=b,
     'gt':lambda a,b:a>b,'ge':lambda a,b:a>=b}
REGIONS={'eq':[(True,'eq'),(False,'lt'),(False,'gt')],
         'lt':[(True,'lt'),(False,'ge')], 'le':[(True,'le'),(False,'gt')],
         'gt':[(True,'gt'),(False,'le')], 'ge':[(True,'ge'),(False,'lt')]}

def validate(request,budget):
    core.need(len(core.canonical(request))<=core.MAX_BYTES,'request_size_limit')
    core.closed(request,['profile','family','prefix','type','terms','operator','threshold'],'outcome_query')
    core.need(request['profile']==PROFILE,'profile')
    core.need(type(request['prefix']) is int and request['prefix'] in [1,2],'query_prefix')
    core.need(type(request['operator']) is str and request['operator'] in OPS,'query_operator')
    native.monetary.rational(request['threshold'])
    terms=request['terms'];core.need(type(terms) is list and 0<len(terms)<=256,'query_term_limit')
    ids=set()
    for term in terms:
        core.closed(term,['account','coefficient'],'query_term');core.text(term['account'],'query_account')
        core.need(term['account'] not in ids,'duplicate_query_account');ids.add(term['account'])
        native.monetary.rational(term['coefficient'])
    # Validate the query against original event-dated monetary types.
    info=family.prepare(request['family'],budget)
    method=(info['first_joined']['family']['method'] if request['prefix']==1 else info['sale_definition'])
    for term in terms:
        core.need(term['account'] in method['accounts'],'undeclared_query_account')
        core.need(request['type']==method['accounts'][term['account']],'query_context_type_mismatch')
    return info

def expression(request,branch):
    balances=branch['sale']['prefix'+str(request['prefix'])]
    return sum((solver.q(t['coefficient'])*balances[t['account']] for t in request['terms']),solver.q(0))

def regions(request,branch):
    value=expression(request,branch);threshold=solver.q(request['threshold'])
    return [(i,truth,op,OPS[op](value,threshold)) for i,(truth,op) in enumerate(REGIONS[request['operator']])]

def replay_witness(request,budget,branch_index,region_index,witness):
    validate(request,budget)
    core.need(type(region_index) is int and 0<=region_index<len(REGIONS[request['operator']]),'query_region')
    replay=family.replay_witness(request['family'],budget,branch_index,witness)
    state=replay['first']['after'] if request['prefix']==1 else replay['after']
    value=sum((Q(t['coefficient'])*Q(state['balances'][t['account']]) for t in request['terms']),Q(0))
    truth,op=REGIONS[request['operator']][region_index]
    core.need(OPS[op](value,Q(request['threshold'])),'query_region_not_satisfied')
    core.need(OPS[request['operator']](value,Q(request['threshold']))==truth,'query_truth_mismatch')
    return {'value':native.monetary.fmt(value),'predicate_holds':truth,
            'original_complete_replay':replay,'committed':False}

def classify(rows):
    yes=any(r['predicate_holds'] and r['status']=='feasible' for r in rows)
    no=any(not r['predicate_holds'] and r['status']=='feasible' for r in rows)
    matching=[r for r in rows if r['predicate_holds']]
    complement=[r for r in rows if not r['predicate_holds']]
    empty_yes=bool(matching) and all(r['status']=='infeasible' for r in matching)
    empty_no=bool(complement) and all(r['status']=='infeasible' for r in complement)
    conclusion=('contingent' if yes and no else 'necessary' if yes and empty_no
                else 'impossible' if no and empty_yes else 'empty_family' if empty_yes and empty_no else 'unknown')
    return {'conclusion':conclusion,'satisfying_witness':yes,'counterexample_witness':no,
            'predicate_region_empty':empty_yes,'complement_region_empty':empty_no,
            'possible':'yes' if yes else 'no' if empty_yes else 'unknown',
            'necessary':'not_applicable_empty_family' if empty_yes and empty_no else 'no' if no else 'yes' if yes and empty_no else 'unknown'}

def assess(request,budget):
    started=time.monotonic()
    try:
        validate(request,budget)
        base={'profile':PROFILE,**BOUNDARY,'request':deepcopy(request),'request_sha256':core.digest(request),
              'family_sha256':core.digest(request['family']),'budget':deepcopy(budget)}
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
        if missing or stop:return {**base,'status':stop or 'unresolved','reason':'parent_formulation_incomplete'}
        rows=[];attempted=0
        for bi,branch in enumerate(branches):
            for ri,truth,op,predicate in regions(request,branch):
                row={'branch':bi,'region':ri,'predicate_holds':truth,'operator':op,'formula':predicate.sexpr()}
                remaining=limit.elapsed_ms-int(1000*(time.monotonic()-started))
                if attempted>=limit.max_cells or remaining<=0 or limit.max_integer_assignments==0:
                    rows.append({**row,'status':'unvisited','reason':'global_cell_time_or_assignment_limit'});continue
                attempted+=1
                bounds={**budget,'max_cells':1,'elapsed_ms':remaining}
                solved=solver.solve(branch['problem'],solver.Budget(**bounds),extra=(predicate,))
                cells=solved['cells']
                core.need(solved['coverage']['total'] in [None,1],'unexpected_query_partition')
                if solved['feasibility']=='Feasible':
                    cell=next(c for c in cells if c['feasibility']=='sat')
                    witness={k:native.monetary.fmt(Q(v)) for k,v in cell['witness'].items()}
                    rows.append({**row,'status':'feasible','witness':witness,
                                 'replay':replay_witness(request,budget,bi,ri,witness)})
                elif solved['feasibility']=='Infeasible':
                    core.need(solved['coverage']['complete'] and len(cells)==1 and cells[0]['conflict']['rechecked']=='unsat','unchecked_query_infeasibility')
                    rows.append({**row,'status':'infeasible','conflict':deepcopy(cells[0]['conflict'])})
                else:rows.append({**row,'status':'unknown','reason':solved.get('reason') or solved['status']})
        decision=classify(rows);decided=sum(r['status'] in ['feasible','infeasible'] for r in rows)
        return {**base,'status':'conditional_outcome_query' if not obligations else 'candidate_outcome_query',
                'branch_partition_complete':True,'branch_manifest':[b['manifest'] for b in branches],
                'decision':decision,'regions':rows,'coverage':{'total':len(rows),'attempted':attempted,
                'decided':decided,'unresolved':len(rows)-decided,'complete':decided==len(rows)},
                'solver_version':z3.get_version_string(),'wall_seconds':time.monotonic()-started}
    except (family.parent.Halt,native.structure.native.Rejected) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':exc.status,'reason':str(exc)[:300]}
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}

def verify_result(request,budget,result):
    try:
        current=assess(request,budget)
        core.need(type(result) is dict and set(result)==set(current),'result_fields')
        for key in current:
            if key not in ['regions','wall_seconds']:core.need(result[key]==current[key],'result_changed:'+key)
        if 'wall_seconds' in result:
            core.need(type(result['wall_seconds']) in [int,float] and 0<=result['wall_seconds']<float('inf'),'invalid_timing')
        if 'regions' not in result:return True
        core.need(type(result['regions']) is list and len(result['regions'])==len(current['regions']),'region_count')
        branches,_,missing,_,_,stop=family.compile_selection(request['family'],budget)
        core.need(not missing and stop is None,'parent_incomplete')
        for row,expected in zip(result['regions'],current['regions']):
            core.need(type(row) is dict and set(row)==set(expected),'region_fields')
            for key in expected:
                if key not in ['witness','replay','conflict']:core.need(row[key]==expected[key],'region_changed:'+key)
            if row['status']=='feasible':
                core.need(row['replay']==replay_witness(request,budget,row['branch'],row['region'],row['witness']),'query_replay_changed')
            elif row['status']=='infeasible':
                conflict=row['conflict'];core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                formulas=dict(branches[row['branch']]['problem'].constraints)
                formulas['query:extra:0']=regions(request,branches[row['branch']])[row['region']][3]
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                core.need(budget['solver_timeout_ms']>0 and budget['solver_rlimit']>0,'conflict_budget')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'query_conflict_not_unsat')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError,z3.Z3Exception):return False
