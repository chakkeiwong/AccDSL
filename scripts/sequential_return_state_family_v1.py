"""Complete restricted settlement-sale family, retaining intermediate alternatives."""
from copy import deepcopy
from hashlib import sha256
from fractions import Fraction as Q
import time,z3
import conditional_return_state_family_v2 as parent
core,joint,solver,native=parent.core,parent.joint,parent.solver,parent.native
piecewise=parent.parent.parent
PROFILE='SequentialReturnStateFamily/1'
BOUNDARY={**parent.BOUNDARY,'scope':'fixed_opening_settlement_then_whole_lot_sale_only'}
SALE_KEY=core.canonical(['sale','proceeds']).decode()


def interval(item,where,premises,missing):
    core.closed(item,['interval','premise','source_ref'],'quantity_domain');core.text(item['source_ref'],'source_ref')
    p=item['premise'];joint.premise(p)
    if p is None:missing.append(where)
    elif p['id'] in premises:core.need(premises[p['id']]==p,'conflicting_premise_identity')
    else:premises[p['id']]=deepcopy(p)
    x=item['interval'];core.closed(x,['lower','upper','lower_inclusive','upper_inclusive'],'interval')
    lo,hi=native.monetary.rational(x['lower']),native.monetary.rational(x['upper'])
    core.need(type(x['lower_inclusive']) is bool and type(x['upper_inclusive']) is bool,'endpoint_inclusion')
    core.need(lo<hi or lo==hi and x['lower_inclusive'] and x['upper_inclusive'],'nonempty_interval')


def prepare(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','first_family','sale_event','proceeds_domain','premise','observations','obligations'],'sequential_family')
    core.need(definition['profile']==PROFILE,'profile')
    first=definition['first_family'];joined,info=parent.prepare(first,budget)
    core.need(first['event']['kind']=='settle','first_settlement_required')
    sale=definition['sale_event'];native.structure.validate(sale,native.event_schema())
    core.need(sale['kind']=='sell' and sale['method']=='inventory.sell','selected_sale_required')
    opening=first['state'];event=first['event']
    core.need(sale['id']!=event['id'] and sale['id'] not in opening['seen'],'duplicate_sequence_event')
    core.need(sale['lot_id']==event['lot_id'],'sale_must_use_created_lot')
    core.need(event['date']<=sale['date']<opening['period']['end_exclusive'],'sale_sequence_chronology')
    if sale['performance_complete']=='unknown' or sale['fraction']=='unknown':
        raise parent.Halt('unresolved','sale_required_fact_unknown')
    if sale['performance_complete'] is not True:raise parent.Halt('unsupported','sale_performance')
    if native.monetary.rational(sale['fraction'])!=1:raise parent.Halt('unsupported','whole_lot_only')
    joint.premise(definition['premise'])
    provided=definition['proceeds_domain'];source=parent.source_ref(core.digest(sale),'/proceeds')
    if sale['proceeds']=='unknown':
        if provided is None:raise parent.Halt('unresolved','sale_proceeds_unknown')
        core.need(type(provided) is dict and provided.get('source_ref')==source,'sale_domain_source_mismatch')
        proceeds=deepcopy(provided)
    else:
        core.need(provided is None,'domain_cannot_replace_known_sale_fact')
        value=sale['proceeds'];proceeds={'interval':{'lower':value,'upper':value,'lower_inclusive':True,'upper_inclusive':True},
            'premise':deepcopy(definition['premise']),'source_ref':source}
    builder,_=native.checked_builders()
    context={'entity':opening['context']['entity'],'book_role':'legal','at':sale['date']}
    method=builder.program('sell',context,native.structure.native.ACCOUNTS)
    method['inputs']['proceeds']['source_ref']=source
    method['inputs']['cost']['source_ref']='conditional:'+core.digest(first)+'#/settlement/carrying'
    native.monetary.compile_definition(method)
    observations=definition['observations'];core.need(type(observations) is list and len(observations)<=256,'observation_limit')
    ids=set()
    for row in observations:
        core.closed(row,['id','prefix','account','type','domain'],'prefix_observation');core.text(row['id'],'observation_id')
        core.need(row['id'] not in ids,'duplicate_observation');ids.add(row['id'])
        core.need(type(row['prefix']) is int and row['prefix'] in [1,2],'observation_prefix')
        core.need(row['account'] in method['accounts'],'observation_account')
        expected=joined['family']['method']['accounts'][row['account']] if row['prefix']==1 else method['accounts'][row['account']]
        core.need(row['type']==expected,'prefix_observation_type_mismatch')
    obligations=definition['obligations'];core.need(type(obligations) is list and len(obligations)<=256,'obligation_limit')
    ids=set()
    for row in obligations:
        core.closed(row,['id','meaning','affects'],'obligation');core.text(row['id'],'obligation_id')
        core.need(row['id'] not in ids,'duplicate_obligation');ids.add(row['id'])
        core.text(row['meaning'],'meaning');core.identifiers(row['affects'],'affects',nonempty=True)
    return {'first_joined':joined,'first_preparation':info,'sale_definition':method,'proceeds_domain':proceeds,
        'cost_lineage':{'first_family_sha256':core.digest(first),'calculation':'carrying','lot_id':event['lot_id'],
                        'from_date':event['date'],'to_date':sale['date'],'premise':deepcopy(definition['premise'])}}


def compile_selection(definition,budget):
    meta=prepare(definition,budget);first=definition['first_family']
    branches,premises,missing,limit,first_meta,stop=parent.compile_selection(first,budget)
    meta['first_compilation']=first_meta
    p=definition['premise'];joint.premise(p)
    if p is None:missing.append('sequence_premise')
    elif p['id'] in premises:core.need(premises[p['id']]==p,'conflicting_premise_identity')
    else:premises[p['id']]=deepcopy(p)
    interval(meta['proceeds_domain'],'sale_proceeds',premises,missing)
    for row in definition['observations']:interval(row['domain'],'observation:'+row['id'],premises,missing)
    if stop or missing:return [],premises,missing,limit,meta,stop or 'unresolved'
    method=meta['sale_definition'];total_nodes=0
    for branch in branches:
        problem=branch['problem'];problem.variables=dict(problem.variables)
        core.need(SALE_KEY not in problem.variables,'variable_collision')
        proceeds=z3.Real('sequence.sale.proceeds');problem.variables[SALE_KEY]=proceeds
        symbols={'proceeds':proceeds,'cost':branch['state']['calculations']['carrying']}
        def expression(node):
            op=node['op']
            if op=='ref':return symbols[node['id']]
            if op=='const':return solver.q(node['value'])
            if op not in ['add','sub']:raise piecewise.Unsupported('sale_expression_operator:'+op)
            a,b=expression(node['left']),expression(node['right']);return a+b if op=='add' else a-b
        journal={k:solver.q(0) for k in method['accounts']};flows={}
        for row in method['calculations']:symbols[row['id']]=expression(row['expression'])
        for row in method['postings']:journal[row['account']]+=expression(row['expression'])
        for row in method['flows']:flows[row['id']]=expression(row['expression'])
        core.need(z3.is_true(z3.simplify(sum(journal.values(),solver.q(0))==0)),'unproved_sale_balance')
        core.need(z3.is_true(z3.simplify(sum(flows.values(),solver.q(0))==journal['cash'])),'unproved_sale_cash_flow')
        problem.add('sale:proceeds_domain',piecewise.interval_formula(proceeds,meta['proceeds_domain']['interval']))
        problem.add('sale:proceeds_nonnegative',proceeds>=0)
        prefix1={k:solver.q(first['state']['balances'][k])+branch['state']['journal'][k] for k in journal}
        prefix2={k:prefix1[k]+journal[k] for k in journal}
        problem.add('sale:closing_cash_nonnegative',prefix2['cash']>=0)
        for row in definition['observations']:
            value=(prefix1 if row['prefix']==1 else prefix2)[row['account']]
            problem.add('observation:'+row['id'],piecewise.interval_formula(value,row['domain']['interval']))
        old=branch['manifest'];manifest={**{k:deepcopy(v) for k,v in old.items() if k!='sha256'},
            'first_native_parent_sha256':old['sha256'],'sale_definition_sha256':core.digest(method),
            'sale_journal':{k:z3.simplify(v).sexpr() for k,v in journal.items()},
            'sale_flows':{k:z3.simplify(v).sexpr() for k,v in flows.items()},
            'constraints':[{'id':key,'formula':value.sexpr()} for key,value in problem.constraints]}
        manifest['sha256']=core.digest(manifest);branch['manifest']=manifest
        branch['sale']={'journal':journal,'flows':flows,'prefix1':prefix1,'prefix2':prefix2}
        total_nodes+=sum(solver.nodes(x) for _,x in problem.constraints)
    if total_nodes>piecewise.MAX_TOTAL_NODES:raise piecewise.BranchLimit('sequence_formula_cap')
    return branches,premises,missing,limit,meta,None


def replay_witness(definition,budget,index,witness):
    branches,_,missing,_,meta,stop=compile_selection(definition,budget)
    core.need(not missing and stop is None,'unresolved_sequence')
    core.need(type(index) is int and 0<=index<len(branches),'branch_index')
    problem=branches[index]['problem'];core.need(type(witness) is dict and set(witness)==set(problem.variables),'complete_sequence_witness')
    first_witness={k:v for k,v in witness.items() if k!=SALE_KEY}
    first=parent.replay_witness(definition['first_family'],budget,index,first_witness)
    sale=deepcopy(definition['sale_event'])
    if sale['proceeds']=='unknown':sale['proceeds']=witness[SALE_KEY]
    else:core.need(sale['proceeds']==witness[SALE_KEY],'sale_known_proceeds_changed')
    before=first['after'];s,e=core.canonical(before),core.canonical(sale)
    proposed=native.propose(s,sha256(s).hexdigest(),e,sha256(e).hexdigest())
    core.need(proposed['status']=='proposed','original_sale_proposal:'+proposed['status']+':'+proposed.get('reason',''))
    after,journal,flows=native.structure.native.transition(before,sale);p=proposed['proposal']
    core.need((p['after'],p['journal'],p['flows'])==(after,journal,flows),'original_sale_transition_mismatch')
    method=meta['sale_definition'];digest=core.digest(method)
    cost=before['lots'][sale['lot_id']]['carrying'];values={'cost':{'status':'known','value':cost},'proceeds':{'status':'known','value':sale['proceeds']}}
    amounts=native.monetary.derive({digest:method},digest,values)
    core.need(amounts['status']=='derived' and amounts['journal']==journal,'original_sale_definition_mismatch')
    substitutions=[(problem.variables[k],solver.q(v)) for k,v in witness.items()]
    for _,formula in problem.constraints:core.need(z3.is_true(z3.simplify(z3.substitute(formula,*substitutions))),'compiled_sequence_constraint')
    for key,formula in branches[index]['sale']['journal'].items():
        core.need(solver.fraction(z3.simplify(z3.substitute(formula,*substitutions)))==Q(journal[key]),'compiled_sale_journal_mismatch')
    for prefix,state in [('prefix1',before),('prefix2',after)]:
        for key,formula in branches[index]['sale'][prefix].items():
            core.need(solver.fraction(z3.simplify(z3.substitute(formula,*substitutions)))==Q(state['balances'][key]),'compiled_prefix_balance_mismatch')
    measured={}
    for row in definition['observations']:
        value=(before if row['prefix']==1 else after)['balances'][row['account']]
        x=row['domain']['interval'];q=Q(value);lo,hi=Q(x['lower']),Q(x['upper'])
        core.need((q>=lo if x['lower_inclusive'] else q>lo) and (q<=hi if x['upper_inclusive'] else q<hi),'observation_replay')
        measured[row['id']]=value
    return {'first':first,'sale_event':sale,'sale_cost':cost,'sale_proposal':p,'after':after,
            'sale_journal':journal,'sale_flows':flows,'observation_values':measured,
            'both_event_transitions_checked':True,'complete_prefix_states_checked':True,
            'actual_fact_status':'not_admitted','committed':False}


def assess(definition,budget):
    started=time.monotonic()
    try:
        preparation=prepare(definition,budget)
        premises,missing,limit,mapped,values=parent.parent.validate(preparation['first_joined'],budget)
        obligations=deepcopy(definition['first_family']['obligations'])+deepcopy(definition['obligations'])
        complete=not missing and not obligations
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),
              'definition_sha256':core.digest(definition),'budget':deepcopy(budget),
              'premises':premises,'missing_premises':missing,'sequence_preparation':preparation,
              'target_obligations':obligations,
              'formulation_complete':complete,'target_existence':'unknown',
              'candidate_feasibility':'unknown','declared_search':'not_started',
              'economic_scope':'explicitly_limited' if complete else 'unresolved'}
        try:
            branches,premises,missing,limit,meta,stop=compile_selection(definition,budget)
            complete=not missing and not obligations
            base.update(premises=premises,missing_premises=missing,formulation_complete=complete,
                        economic_scope='explicitly_limited' if complete else 'unresolved')
            base['sequence_compilation']=meta
            if stop:return {**base,'status':stop,'reason':'selected_prerequisites'}
        except piecewise.BranchLimit as exc:
            return {**base,'status':'unknown','reason':str(exc),'branch_partition_complete':False}
        except piecewise.Unsupported as exc:
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
                witness={k:native.monetary.fmt(Q(v)) for k,v in cell['witness'].items()}
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
            return {**answer,'status':'conditional_sequence_family_witness' if complete else 'candidate_sequence_with_unresolved_obligations',
                    'candidate_feasibility':'conditionally_feasible',
                    'target_existence':'conditional_witness' if complete else 'unknown'}
        if coverage['complete']:
            return {**answer,'status':'conditionally_infeasible','candidate_feasibility':'conditionally_infeasible',
                    'target_existence':'conditionally_empty' if complete else 'unknown'}
        return {**answer,'status':'unknown'}
    except (parent.Halt,native.structure.native.Rejected) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':exc.status,'reason':str(exc)[:300]}
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
        compiled,_,missing,_,_,stop=compile_selection(definition,budget)
        core.need(not missing and stop is None,'missing_premises')
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
