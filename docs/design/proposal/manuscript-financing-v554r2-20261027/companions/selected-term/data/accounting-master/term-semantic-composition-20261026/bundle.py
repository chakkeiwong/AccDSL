"""Reviewed semantic bundle; native structural/migration admission is separate."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'nested-obligation-completion-20261026'))
import declarations as d
t=d.t;p=d.p;core=d.core;guards=p.guards
PROFILE='TermStateSemanticBundle/1';CALL='TermStateSemanticBundleCall/1'
MEMBERS=('common','clock','terms','assessments','summaries','events')

def validate(spec,definition):
    p.base.memory.bounded(spec)
    core.closed(spec,['profile','context',*MEMBERS,'residuals'],'semantic_bundle')
    core.need(spec['profile']==PROFILE,'semantic_bundle_profile')
    guards.validate(spec['common'])
    for name in ('terms','assessments','summaries'):t.validate(spec[name],definition)
    d.bridge.validate(spec['events'],definition)
    for name in ('common','terms','assessments','summaries','events'):
        core.need(spec[name]['context']==spec['context'],'semantic_member_context')
    clock=spec['clock'];core.closed(clock,['manifest','bindings'],'clock_binding')
    t.c.guarded.compile_manifest(clock['manifest'])
    core.need(type(clock['bindings']) is dict and set(clock['bindings'])==set(clock['manifest']['inputs']),'exact_clock_bindings')
    for name,b in clock['bindings'].items():
        core.need(b.get('kind')=='book_field','clock_book_binding')
        typ=t.capture_type(b,'groups',None,None,definition)
        declaration=clock['manifest']['inputs'][name]
        core.need(typ==declaration['type'] and declaration['role']=='state','clock_binding_type')
    core.identifiers(spec['residuals'],'bundle_residuals',True)

def make_call(spec,book,definition,schemas,coverage,selection):
    result=dict(profile=CALL,book_order_sha256=p.order_digest(book),spec_order_sha256=p.order_digest(spec),reviewed_selection=selection)
    for n,v in [('spec',spec),('book',book),('definition',definition),('schemas',schemas),('coverage',coverage)]:result[n+'_sha256']=core.digest(v)
    return result

def nested_coverage(source,coverage):
    core.need(source['parent_pointer']=='/claims' and source['child_pointer'] in ('/terms','/assessments'),'semantic_population_scope')
    return coverage[source['child_pointer'][1:]]

def clock_assess(spec,book,definition,schemas):
    guards.program.typed.typed_book(book,definition,schemas)
    values={};lineage={}
    for name,b in spec['bindings'].items():
        source=t.captured(b,None,None,book);values[name]=dict(status='known',value=source['value']);lineage[name]=source
    manifest=spec['manifest'];h=core.digest(manifest)
    return dict(values=values,lineage=lineage,assessment=t.c.guarded.assess({h:manifest},h,values,[]))

def assess(spec,book,definition,schemas,coverage,selection,call):
    result=dict(profile=PROFILE,**p.FLAGS,method_eligible=False,structural_profile_admitted=False);stage='call'
    try:
        core.need(call==make_call(spec,book,definition,schemas,coverage,selection),'stale_semantic_bundle_call')
        result.update({k:v for k,v in call.items() if k!='profile'})
        core.need(selection==core.digest(spec),'reviewed_semantic_bundle')
        stage='declaration';validate(spec,definition);core.need(spec['context']==book['context'],'bundle_book_context')
        stage='population';core.closed(coverage,['claims','terms','assessments'],'bundle_populations')
        claims=coverage['claims'];core.closed(claims,['profile','status','map_pointer','book_sha256','provenance'],'claim_population')
        core.need(claims['profile']=='SuppliedClaimPopulation/1' and claims['map_pointer']=='/claims','claim_population_scope')
        core.need(claims['book_sha256']==core.digest(book),'claim_population_book')
        core.need(claims['status'] in ('complete','partial','unknown'),'claim_population_status');core.text(claims['provenance'],'claim_population_provenance')
        if claims['status']!='complete':return dict(result,status='unresolved',reason='complete_supplied_claims_required',failed_stage=stage)
        stage='components';components={}
        components['common']=guards.assess(spec['common'],book,definition,schemas)
        components['clock']=clock_assess(spec['clock'],book,definition,schemas)
        for name in ('terms','assessments','summaries'):
            template=spec[name];iteration=nested_coverage(template['iteration'],coverage)
            query_cov={key:nested_coverage(item['projection'],coverage) for key,item in template['template']['queries'].items()}
            h=core.digest(template);args=(template,book,definition,schemas,iteration,query_cov,h)
            components[name]=t.evaluate(*args,t.make_call(*args))
        source_cov={name:nested_coverage(source,coverage) for name,source in spec['events']['sources'].items()}
        h=core.digest(spec['events']);args=(spec['events'],book,definition,schemas,source_cov,h)
        components['events']=d.bridge.assess(*args,d.bridge.make_call(*args))
        statuses={name:(r['assessment']['status'] if name=='clock' else r['status']) for name,r in components.items()}
        expected={'common':('collection_total_requirements_satisfied',),'clock':('requirements_satisfied',),
          'terms':('requirements_satisfied','no_active_requirements'),
          'assessments':('requirements_satisfied','no_active_requirements'),
          'summaries':('requirements_satisfied','no_active_requirements'),'events':('collection_requirements_satisfied',)}
        outcomes=[s if s in ('invalid','unsupported','unresolved') or s in expected[n] else 'invalid' for n,s in statuses.items()]
        status=next((s for s in ('invalid','unsupported','unresolved') if s in outcomes),'term_semantic_requirements_satisfied')
        return dict(result,status=status,failed_stage=None,components=components,component_statuses=statuses,
          derived_selection_basis='Each component derives from the independently reviewed bundle; no independent per-instance review',
          scope='Typed supplied state and declared semantic constraints only; exact native structural/migration profile unadmitted',residuals=deepcopy(spec['residuals']))
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,OverflowError) as exc:
        return dict(result,status='invalid',reason=str(exc)[:300],failed_stage=stage)
