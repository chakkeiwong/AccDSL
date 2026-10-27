"""Selected prerequisite satisfaction over complete monetary families."""
from copy import deepcopy
from fractions import Fraction as Q
import time
import z3
import method_requirements_v3 as requirements
import piecewise_method_family_v1 as parent

core, joint, solver = parent.core, parent.joint, parent.solver
PROFILE='PrerequisiteMethodFamily/1'
BOUNDARY={**parent.BOUNDARY,'scope':'conditional_selected_prerequisite_method_family_only'}


def dependencies(node):
    if node['op']=='ref':return {node['id']}
    if node['op']=='const':return set()
    if node['op']=='not':return dependencies(node['arg'])
    if node['op'] in ['all','any']:
        return set().union(*(dependencies(x) for x in node['args']))
    return dependencies(node['left']) | dependencies(node['right'])


def original_truth(node,manifest,values):
    deps=sorted(dependencies(node))
    mini={'profile':requirements.PROFILE,'method_id':'exact_fixed_predicate','version':'1',
        'inputs':{k:deepcopy(manifest['inputs'][k]) for k in deps},'required_known':[],
        'requirements':[{'id':'predicate','guard':{'op':'const','type':core.BOOL,'value':True},
            'guard_requires':[],'predicate':deepcopy(node),'requires':deps,'admission_refs':[],
            'on_false':'invalid','on_unknown':'unresolved'}],
        'capabilities':[],'residual_prerequisites':deepcopy(manifest['residual_prerequisites'])}
    digest=core.digest(mini)
    result=requirements.assess({digest:mini},digest,{k:values[k] for k in deps},[])
    core.need('findings' in result,'fixed_evaluation_failed:'+result.get('reason',result['status']))
    return result['findings'][0]['body_truth']


def validate(definition,budget):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','family','requirements','selected_requirements_digest',
                           'bindings','available_capabilities','obligations'],'prerequisite_family')
    core.need(definition['profile']==PROFILE,'profile')
    premises,missing,limit=parent.validate(definition['family'],budget)
    manifest=definition['requirements'];requirements.compile_manifest(manifest)
    core.need(definition['selected_requirements_digest']==core.digest(manifest),'requirements_digest')
    core.need(len(manifest['inputs'])<=256 and len(manifest['requirements'])<=256,'prerequisite_limit')
    core.identifiers(definition['available_capabilities'],'available_capabilities')
    bindings=definition['bindings'];method=definition['family']['method']
    core.need(type(bindings) is dict and set(bindings)==set(manifest['inputs']),'complete_requirement_bindings')
    mapped,values={},{}
    for key,item in bindings.items():
        core.need(type(item) is dict and item.get('kind') in ['method_input','external'],'binding_kind')
        typ=manifest['inputs'][key]['type']
        if item['kind']=='method_input':
            core.closed(item,['kind','input','premise','requirement_source_ref','method_source_ref'],'method_binding')
            core.text(item['input'],'method_input');target=item['input']
            core.need(target in method['inputs'],'unknown_method_input')
            core.need(typ==method['inputs'][target]['type'],'mapping_type_mismatch')
            core.need(item['requirement_source_ref']==manifest['inputs'][key]['source_ref'] and
                      item['method_source_ref']==method['inputs'][target]['source_ref'],'mapping_source_mismatch')
            mapped[key]=target;interval=definition['family']['domains'][target]['interval']
            values[key]=({'status':'known','value':interval['lower']} if interval['lower']==interval['upper'] else
                         {'status':'unknown','reason':'conditional_candidate_variable'})
        else:
            core.closed(item,['kind','binding','premise','source_ref'],'external_binding')
            core.need(item['source_ref']==manifest['inputs'][key]['source_ref'],'external_source_mismatch')
            core.validate_values({'inputs':{key:{'type':{'kind':typ['kind']}}}},{key:item['binding']})
            values[key]=deepcopy(item['binding'])
        p=item['premise'];joint.premise(p)
        if p is None:missing.append('binding:'+key)
        elif p['id'] in premises:core.need(premises[p['id']]==p,'conflicting_premise_identity')
        else:premises[p['id']]=deepcopy(p)
    obligations=definition['obligations'];core.need(type(obligations) is list and len(obligations)<=256,'obligation_limit')
    ids=set()
    for row in obligations:
        core.closed(row,['id','meaning','affects'],'obligation');core.text(row['id'],'obligation_id')
        core.need(row['id'] not in ids,'duplicate_obligation');ids.add(row['id'])
        core.text(row['meaning'],'meaning');core.identifiers(row['affects'],'affects',nonempty=True)
    return premises,missing,limit,mapped,values


def compile_selection(definition,budget):
    premises,missing,limit,mapped,values=validate(definition,budget)
    manifest=definition['requirements'];method_family=definition['family']
    findings=[];selected=[];states=[]
    caps=sorted(set(manifest['capabilities'])-set(definition['available_capabilities']))
    if caps:states.append('unsupported')
    for key in manifest['required_known']:
        if key not in mapped and values[key]['status']=='unknown':
            states.append('unresolved');findings.append({'kind':'required_known','input':key,'consequence':'unresolved'})
    for req in manifest['requirements']:
        guard_refs=dependencies(req['guard'])
        if any(k in mapped and values[k]['status']=='unknown' for k in guard_refs):
            states.append('unsupported');findings.append({'id':req['id'],'activation':'unsupported_symbolic_guard',
                                                        'consequence':'unsupported'});continue
        truth=original_truth(req['guard'],manifest,values)
        if truth!='true':
            consequence='not_applicable' if truth=='false' else 'unresolved'
            if truth=='unknown':states.append('unresolved')
            findings.append({'id':req['id'],'activation':'inactive' if truth=='false' else 'unknown',
                             'consequence':consequence});continue
        def select(node,path):
            refs=dependencies(node)
            if not (refs & set(mapped)):
                fixed=original_truth(node,manifest,values)
                consequence='satisfied' if fixed=='true' else (req['on_false'] if fixed=='false' else 'unresolved')
                if consequence!='satisfied':states.append(consequence)
                findings.append({'id':req['id'],'path':path,'activation':'active','truth':fixed,
                                 'consequence':consequence,'dependencies':sorted(refs)})
            elif node['op']=='all':
                for index,child in enumerate(node['args']):select(child,path+'/'+str(index))
            elif node['op'] in ['eq','le','lt']:
                unknown=[k for k in refs if k not in mapped and values[k]['status']=='unknown']
                if unknown:
                    states.append('unresolved');findings.append({'id':req['id'],'path':path,'activation':'active',
                        'consequence':'unresolved','unknown_inputs':sorted(unknown)})
                else:selected.append((req['id'],path,node))
            else:
                states.append('unsupported');findings.append({'id':req['id'],'path':path,'activation':'active',
                    'consequence':'unsupported','reason':'symbolic_predicate_form'})
        select(req['predicate'],req['id'])
    stop=next((x for x in ['invalid','unsupported','unresolved'] if x in states),None)
    meta={'fixed_findings':findings,'missing_capabilities':caps,
          'mapped_inputs':deepcopy(mapped),'external_values':{k:v for k,v in values.items() if k not in mapped},
          'selected_predicates':[{'requirement':key,'path':path,'expression':deepcopy(node)} for key,path,node in selected],
          'binding_sha256':core.digest(definition['bindings'])}
    if stop or missing:return [],premises,missing,limit,meta,stop or 'unresolved'
    branches,_,_,_=parent.compile_family(method_family,budget)
    total_nodes=0
    for branch in branches:
        p=branch['problem']
        def numeric(node):
            op=node['op']
            if op=='ref':
                key=node['id']
                core.need(manifest['inputs'][key]['type']['kind']=='rational','numeric_predicate_required')
                if key in mapped:
                    target=mapped[key];interval=method_family['domains'][target]['interval']
                    if interval['lower']==interval['upper']:return solver.q(interval['lower']),False
                    return p.variables[target],True
                return solver.q(values[key]['value']),False
            if op=='const':
                core.need(node['type']['kind']=='rational','numeric_constant_required')
                return solver.q(node['value']),False
            if op not in ['add','sub','mul']:raise parent.Unsupported('numeric_predicate_operator:'+op)
            a,ax=numeric(node['left']);b,bx=numeric(node['right'])
            if op=='mul' and ax and bx:raise parent.Unsupported('unknown_product_in_prerequisite')
            return z3.simplify(a+b if op=='add' else a-b if op=='sub' else a*b),ax or bx
        for reqid,path,node in selected:
            a,_=numeric(node['left']);b,_=numeric(node['right'])
            formula=a==b if node['op']=='eq' else (a<=b if node['op']=='le' else a<b)
            p.add(core.canonical(['prerequisite',reqid,path]).decode(),formula)
        old=branch['manifest']
        manifest_out={**{k:deepcopy(v) for k,v in old.items() if k!='sha256'},'parent_sha256':old['sha256'],
            'constraints':[{'id':key,'formula':value.sexpr()} for key,value in p.constraints]}
        manifest_out['sha256']=core.digest(manifest_out);branch['manifest']=manifest_out
        total_nodes+=sum(solver.nodes(x) for _,x in p.constraints)
        if total_nodes>parent.MAX_TOTAL_NODES:raise parent.BranchLimit('prerequisite_formula_cap')
    return branches,premises,missing,limit,meta,None


def replay_witness(definition,budget,index,witness):
    branches,_,missing,_,_,stop=compile_selection(definition,budget)
    core.need(not missing and stop is None,'prerequisite_unresolved')
    core.need(type(index) is int and 0<=index<len(branches),'branch_index')
    monetary=parent.replay_witness(definition['family'],budget,index,witness)
    manifest=definition['requirements'];values={}
    for key,item in definition['bindings'].items():
        values[key]=({'status':'known','value':witness[item['input']]} if item['kind']=='method_input'
                     else deepcopy(item['binding']))
    digest=definition['selected_requirements_digest']
    result=requirements.assess({digest:manifest},digest,values,definition['available_capabilities'])
    core.need(result['status'] in ['requirements_satisfied','no_active_requirements'],'original_prerequisite_replay:'+result['status'])
    substitutions=[(branches[index]['problem'].variables[k],solver.q(v)) for k,v in witness.items()]
    for _,formula in branches[index]['problem'].constraints:
        core.need(z3.is_true(z3.simplify(z3.substitute(formula,*substitutions))),'compiled_constraint_replay')
    return {'monetary':monetary,'prerequisites':result,'candidate_bindings':values,
            'both_original_evaluators_checked':True,'actual_fact_status':'not_admitted',
            'native_preconditions_complete':False}


def assess(definition,budget):
    started=time.monotonic()
    try:
        premises,missing,limit,mapped,values=validate(definition,budget)
        obligations=deepcopy(definition['family']['obligations'])+deepcopy(definition['obligations'])
        complete=not missing and not obligations
        base={'profile':PROFILE,**BOUNDARY,'definition':deepcopy(definition),
              'definition_sha256':core.digest(definition),'budget':deepcopy(budget),
              'premises':premises,'missing_premises':missing,
              'target_obligations':obligations,
              'formulation_complete':complete,'target_existence':'unknown',
              'candidate_feasibility':'unknown','declared_search':'not_started',
              'economic_scope':'explicitly_limited' if complete else 'unresolved'}
        try:
            branches,_,_,_,meta,stop=compile_selection(definition,budget)
            base['prerequisite_compilation']=meta
            if stop:return {**base,'status':stop,'reason':'selected_prerequisites'}
        except parent.BranchLimit as exc:
            return {**base,'status':'unknown','reason':str(exc),'branch_partition_complete':False}
        except parent.Unsupported as exc:
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
                witness={k:parent.effects.fmt(Q(v)) for k,v in cell['witness'].items()}
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
