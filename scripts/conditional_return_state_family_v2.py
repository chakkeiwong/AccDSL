"""Conditional numeric event families from one complete retained native state."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from fractions import Fraction as Q
import json,time,z3
import prerequisite_method_family_v1 as parent
import typed_return_transition_v1 as native
core,joint,solver=parent.core,parent.joint,parent.solver
PROFILE='ConditionalReturnStateFamily/1'
BOUNDARY={**parent.BOUNDARY,'scope':'one_fixed_native_opening_conditional_event_only',
          'committed':False,'method_eligible':False}
AUDIT=Path(__file__).resolve().parents[1]/'data/accounting-master/method-family-prerequisites-audit-20261024/audit.json'
AUDIT_SHA='3bfbd1dcbc7c28d7fae18538d2a9d8d702a569af0ba80886e55eb48f68b760ef'
ALLOWED={'settle':{'actual_units':'n','unit_handling':'h','unit_deterioration':'d','inventory_nrv':'nrv'},
         'sell':{'proceeds':'proceeds'}}


class Halt(ValueError):
    def __init__(self,status,reason):self.status=status;super().__init__(reason)


def source_ref(raw_hash,pointer):return 'sha256:'+raw_hash+'#'+pointer


def prepare(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','state','event','event_domains','premise','obligations','branch_limit'],'native_family')
    core.need(definition['profile']==PROFILE,'profile')
    state,event=definition['state'],definition['event']
    native.structure.validate(state,native.structure.schema())
    core.need(type(event) is dict and event.get('kind') in ALLOWED,'selected_event_kind')
    native.structure.validate(event,native.event_schema())
    if state['context']['currency']!='USD' or state['context']['book_role']!='legal':
        raise Halt('unsupported','selected_USD_legal_profile_only')
    native.structure.native.invariant(state)
    core.need(event['id'] not in state['seen'],'duplicate_event')
    kind=event['kind']
    if kind=='settle':core.need(event['lot_id'] not in state['lots'],'duplicate_lot')
    else:
        core.need(event['lot_id'] in state['lots'],'unknown_lot')
        core.need(not state['lots'][event['lot_id']]['disposed'],'lot_already_disposed')
    joint.premise(definition['premise'])
    domains=definition['event_domains'];core.need(type(domains) is dict and set(domains)<=set(ALLOWED[kind]),'event_domain_allowlist')
    for field in domains:core.need(event[field]=='unknown','domain_cannot_replace_known_fact')
    state_hash,event_hash=core.digest(state),core.digest(event)
    for field,item in domains.items():
        core.need(type(item) is dict and item.get('source_ref')==source_ref(event_hash,'/'+field),'event_domain_source_mismatch')
    monetary_builder,_=native.checked_builders()
    context={'entity':state['context']['entity'],'book_role':'legal','at':event['date']}
    method=monetary_builder.program(kind,context,native.structure.native.ACCOUNTS)
    if kind=='settle':
        paths={'n':('event','/actual_units'),'p':('before','/component/unit_refund'),
            'c':('before','/component/unit_cost'),'d':('event','/unit_deterioration'),
            'h':('event','/unit_handling'),'nrv':('event','/inventory_nrv'),
            'refund_before':('before','/component/refund'),'recovery_before':('before','/component/recovery')}
    else:
        token=event['lot_id'].replace('~','~0').replace('/','~1')
        paths={'proceeds':('event','/proceeds'),'cost':('before','/lots/'+token+'/carrying')}
    method_domains={};unresolved=[]
    for key,(origin,pointer) in paths.items():
        raw_hash=state_hash if origin=='before' else event_hash
        reference=source_ref(raw_hash,pointer);method['inputs'][key]['source_ref']=reference
        value=native.read_path(state if origin=='before' else event,pointer)
        field=pointer[1:]
        if origin=='event' and field in domains:method_domains[key]=deepcopy(domains[field])
        elif value=='unknown':unresolved.append(origin+pointer)
        else:method_domains[key]={'interval':{'lower':value,'upper':value,'lower_inclusive':True,'upper_inclusive':True},
                                 'premise':deepcopy(definition['premise']),'source_ref':reference}
    if unresolved:raise Halt('unresolved','required_numeric_inputs:'+','.join(unresolved))
    original,lineage=native.prerequisite_manifest(state,event,state_hash,event_hash)
    core.need('input_declarations' in original,'original_requirement_definition_unavailable')
    core.need(sha256(AUDIT.read_bytes()).hexdigest()==AUDIT_SHA,'prerequisite_template_changed')
    template=next(row for row in json.loads(AUDIT.read_text())['selected'] if row['kind']==kind)
    manifest=deepcopy(template['capture']['manifest'])
    # Original generator supplies exact typed declarations/source references.
    # Replace type context in constants as well, then verify the whole original digest.
    def contextualize(node):
        if isinstance(node,dict):
            if node.get('kind')=='rational' and 'context' in node:node['context']=deepcopy(context)
            for value in node.values():contextualize(value)
        elif isinstance(node,list):
            for value in node:contextualize(value)
    contextualize(manifest);manifest['inputs']=deepcopy(original['input_declarations'])
    core.need(core.digest(manifest)==original['selected_digest'],'original_prerequisite_template_mismatch')
    bindings={}
    for key,declaration in manifest['inputs'].items():
        if key in method['inputs']:
            bindings[key]={'kind':'method_input','input':key,'premise':deepcopy(definition['premise']),
                'requirement_source_ref':declaration['source_ref'],'method_source_ref':method['inputs'][key]['source_ref']}
        else:
            line=lineage[key];value=native.read_path(state if line['source']=='before' else event,line['pointer'])
            bound=({'status':'unknown','reason':'explicit_native_unknown:'+line['source']+line['pointer']}
                   if value=='unknown' else {'status':'known','value':value})
            bindings[key]={'kind':'external','binding':bound,'premise':deepcopy(definition['premise']),
                           'source_ref':declaration['source_ref']}
    joined={'profile':parent.PROFILE,'family':{'profile':parent.parent.PROFILE,'method':method,
        'selected_method_digest':core.digest(method),'domains':method_domains,'measurements':[],
        'obligations':[],'branch_limit':definition['branch_limit']},'requirements':manifest,
        'selected_requirements_digest':core.digest(manifest),'bindings':bindings,
        'available_capabilities':[],'obligations':deepcopy(definition['obligations'])}
    parent.validate(joined,budget)
    return joined,{'state_sha256':state_hash,'event_skeleton_sha256':event_hash,
                   'method_input_paths':{key:list(value) for key,value in paths.items()},'original_prerequisite_digest':original['selected_digest'],
                   'variable_event_fields':{field:ALLOWED[kind][field] for field in domains},
                   'opening_native_invariant_checked':True}


def compile_selection(definition,budget):
    joined,meta=prepare(definition,budget)
    branches,premises,missing,limit,selected,stop=parent.compile_selection(joined,budget)
    meta.update(joined_definition=joined,prerequisite_compilation=selected)
    for branch in branches:
        p=branch['problem'];cash=solver.q(definition['state']['balances']['cash'])+branch['state']['journal']['cash']
        p.add('native:closing_cash_nonnegative',cash>=solver.q(0))
        old=branch['manifest'];manifest={**{k:deepcopy(v) for k,v in old.items() if k!='sha256'},
            'prerequisite_parent_sha256':old['sha256'],'native_opening_sha256':meta['state_sha256'],
            'constraints':[{'id':key,'formula':value.sexpr()} for key,value in p.constraints]}
        manifest['sha256']=core.digest(manifest);branch['manifest']=manifest
    if sum(solver.nodes(x) for b in branches for _,x in b['problem'].constraints)>parent.parent.MAX_TOTAL_NODES:
        raise parent.parent.BranchLimit('native_formula_cap')
    return branches,premises,missing,limit,meta,stop


def replay_witness(definition,budget,index,witness):
    branches,_,missing,_,meta,stop=compile_selection(definition,budget)
    core.need(not missing and stop is None,'unresolved_native_family')
    selected=parent.replay_witness(meta['joined_definition'],budget,index,witness)
    candidate=deepcopy(definition['event'])
    for field,key in meta['variable_event_fields'].items():candidate[field]=witness[key]
    state=definition['state'];raw_s,raw_e=core.canonical(state),core.canonical(candidate)
    proposal=native.propose(raw_s,sha256(raw_s).hexdigest(),raw_e,sha256(raw_e).hexdigest())
    core.need(proposal['status']=='proposed','original_native_proposal:'+proposal['status']+':'+proposal.get('reason',''))
    after,journal,flows=native.structure.native.transition(state,candidate)
    p=proposal['proposal'];core.need((p['after'],p['journal'],p['flows'])==(after,journal,flows),'original_native_transition_mismatch')
    core.need(selected['monetary']['journal']==journal,'family_native_journal_mismatch')
    expected_flows=[{'entity':state['context']['entity'],'activity':f['activity'],'origin':f['origin'],
        'amount':f['amount'],'date':candidate['date'],'event_id':candidate['id']} for f in selected['monetary']['flows']]
    core.need(expected_flows==flows,'family_native_flow_mismatch')
    substitutions=[(branches[index]['problem'].variables[k],solver.q(v)) for k,v in witness.items()]
    for _,formula in branches[index]['problem'].constraints:
        core.need(z3.is_true(z3.simplify(z3.substitute(formula,*substitutions))),'compiled_native_constraint')
    return {'selected_family':selected,'candidate_event':candidate,'native_proposal':p,
        'after':after,'journal':journal,'flows':flows,'both_original_transitions_checked':True,
        'complete_native_state_checked':True,'actual_fact_status':'not_admitted','committed':False}


def assess(definition,budget):
    started=time.monotonic()
    try:
        joined,preparation=prepare(definition,budget)
        premises,missing,limit,mapped,values=parent.validate(joined,budget)
        obligations=deepcopy(definition['obligations'])
        complete=not missing and not obligations
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),
              'definition_sha256':core.digest(definition),'budget':deepcopy(budget),
              'premises':premises,'missing_premises':missing,'native_preparation':preparation,
              'target_obligations':obligations,
              'formulation_complete':complete,'target_existence':'unknown',
              'candidate_feasibility':'unknown','declared_search':'not_started',
              'economic_scope':'explicitly_limited' if complete else 'unresolved'}
        try:
            branches,_,_,_,meta,stop=compile_selection(definition,budget)
            base['native_compilation']=meta
            if stop:return {**base,'status':stop,'reason':'selected_prerequisites'}
        except parent.parent.BranchLimit as exc:
            return {**base,'status':'unknown','reason':str(exc),'branch_partition_complete':False}
        except parent.parent.Unsupported as exc:
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
                witness={k:parent.parent.effects.fmt(Q(v)) for k,v in cell['witness'].items()}
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
            return {**answer,'status':'conditional_state_family_witness' if complete else 'candidate_state_with_unresolved_obligations',
                    'candidate_feasibility':'conditionally_feasible',
                    'target_existence':'conditional_witness' if complete else 'unknown'}
        if coverage['complete']:
            return {**answer,'status':'conditionally_infeasible','candidate_feasibility':'conditionally_infeasible',
                    'target_existence':'conditionally_empty' if complete else 'unknown'}
        return {**answer,'status':'unknown'}
    except (Halt,native.structure.native.Rejected) as exc:
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
