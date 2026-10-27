"""Evidence-only composition using unchanged source, overlap and time engines."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import retained_statement_network_v1 as network
import population_overlap_v1 as overlap
temporal=network.temporal;core=temporal.core
PREFIX='conditional_region:'

def compose(source_request,groups,budget):
    parent=network.assess(source_request,budget)
    core.need(parent['status']!='invalid','invalid_source')
    core.need(type(groups) is dict and bool(groups),'nonempty_groups')
    definition=deepcopy(parent['definition']);before=deepcopy(definition)
    extra_missing=[];details={}
    for name,group in groups.items():
        core.text(name,'group_id')
        core.closed(group,['observations','regions','valuation_premise','projection_premises'], 'overlap_group')
        source_ids=group['observations'];core.need(type(source_ids) is dict,'observation_bindings')
        core.need(set(group['projection_premises'])==set(source_ids),'projection_keys')
        core.need(len(set(source_ids.values()))==len(source_ids),'distinct_source_populations')
        core.need(all(k in before['observations'] for k in source_ids.values()),'unknown_source_observation')
        original={n:before['observations'][k] for n,k in source_ids.items()}
        first=next(iter(original.values()))['type'];when=first['time'];value_type=first['value_type']
        core.need(when['kind']=='instant','instant_populations_required')
        populations={}
        for n,item in original.items():
            core.need(item['type']['value_type']==value_type,'source_context_mismatch')
            core.need(item['type']['time']==when,'source_instant_mismatch')
            source_context=parent['source_mapping'][source_ids[n]]['original_context']
            # This bounded composer handles the existing cash captions only.
            # Unsupported dimensional mappings cannot be dropped as a fallback.
            core.need(not any(k in source_context for k in ['dimensions','axis','member']),
                      'dimensional_source_projection_not_supported')
            populations[n]={'measurement':{**deepcopy(item),'type':deepcopy(value_type)},
                'predicate':item['type']['quantity'],'source_dimensions':{},
                'projection_premise':deepcopy(group['projection_premises'][n])}
        body={'profile':overlap.PROFILE,'value_type':deepcopy(value_type),'populations':populations,
              'regions':deepcopy(group['regions']),'valuation_premise':deepcopy(group['valuation_premise'])}
        numeric,metadata=overlap.lower(body);overlap.joint.validate(numeric,budget)
        extra_missing += [name+':'+m for m in metadata['missing']]
        rename={'population:'+n:oid for n,oid in source_ids.items()}
        for region in metadata['region_order']:
            old='region:'+region;new=PREFIX+core.digest([name,region])
            core.need(new not in definition['observations'],'region_identity_collision')
            rename[old]=new
            item=deepcopy(numeric['observations'][old])
            item['type']={'value_type':deepcopy(value_type),'time':deepcopy(when),
                          'quantity':'conditional_aggregate_region:'+core.digest([name,region])}
            definition['observations'][new]=item
        for equation in numeric['equations']:
            rid=PREFIX+core.digest([name,equation['id']])
            core.need(all(r['id']!=rid for r in definition['relations']),'relation_identity_collision')
            definition['relations'].append({'id':rid,'kind':'same_time',
                'terms':[{**t,'observation':rename[t['observation']]} for t in equation['terms']],
                'rhs':equation['rhs'],'identity_premise':deepcopy(equation['identity_premise'])})
        details[name]={'request':body,'metadata':metadata,'rename':rename,'time':deepcopy(when),
            'source_ids':deepcopy(source_ids),'retained_source_mappings':{
                n:deepcopy(parent['source_mapping'][oid]) for n,oid in source_ids.items()}}
    assert all(definition['observations'][k]==v for k,v in before['observations'].items())
    assert definition['relations'][:len(before['relations'])]==before['relations']
    temporal.lower(definition,budget)
    return parent,definition,details,extra_missing

def assess(source_request,groups,budget):
    try:
        parent,definition,details,missing=compose(source_request,groups,budget)
        assessment=None if missing else temporal.assess(definition,budget)
        return {'profile':'RetainedPopulationCompositionEvidence/1',**overlap.BOUNDARY,
            'scope':'evidence_only_retained_temporal_composition','source_result':parent,
            'definition':definition,'groups':details,'missing':missing,
            'status':'unresolved' if missing else assessment['status'],
            'assessment':assessment,'original_observation_count':len(parent['definition']['observations']),
            'original_relation_count':len(parent['definition']['relations'])}
    except (ValueError,TypeError,KeyError,AttributeError,OSError) as exc:
        return {'profile':'RetainedPopulationCompositionEvidence/1',**overlap.BOUNDARY,
                'status':'invalid','reason':str(exc)[:300]}

def verify(source_request,groups,budget,result):
    try:
        if result.get('status')=='invalid':return result==assess(source_request,groups,budget)
        parent,definition,details,missing=compose(source_request,groups,budget)
        core.need(network.verify_result(source_request,budget,result['source_result']),'source_replay')
        current=assess(source_request,groups,budget)
        for k,v in current.items():
            if k not in ['source_result','assessment']:core.need(result[k]==v,'result_changed:'+k)
        core.need(set(result)==set(current),'result_fields')
        if missing:return result['assessment'] is None
        saved=result['assessment'];fresh=current['assessment']
        core.need(set(saved)==set(fresh),'assessment_fields')
        for k,v in fresh.items():
            if k!='joint_assessment':core.need(saved[k]==v,'assessment_changed:'+k)
        a,b=saved['joint_assessment'],fresh['joint_assessment']
        core.need(set(a)==set(b),'joint_fields')
        for k,v in b.items():
            if k not in ['witness','conflicts','solver_wall_seconds']:core.need(a[k]==v,'joint_changed:'+k)
        if 'witness' in a:temporal.check_witness(definition,budget,a['witness'])
        if 'conflicts' in a:network.source._check_conflicts(saved['numeric_definition'],budget,a['conflicts'])
        if 'solver_wall_seconds' in a:
            t=a['solver_wall_seconds'];core.need(type(t) in [int,float] and 0<=t<float('inf'),'timing')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,OSError):return False
