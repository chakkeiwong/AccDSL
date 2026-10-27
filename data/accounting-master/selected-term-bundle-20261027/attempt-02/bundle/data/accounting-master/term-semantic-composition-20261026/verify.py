from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import importlib.util,json,subprocess,sys,time
import declaration as d
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];b=d.b;p=d.p;core=d.core
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+chr(10))

def common_corruptions(base):
    rows=[];owner='invoice/a~1'
    def add(label,change,component):
        state=deepcopy(base);change(state,state['book']['memory']['claims'][owner]);b.d.f.f.configure(state)
        rows.append((label,state,component))
    add('claim_total_mismatch',lambda s,c:c.update(remaining='1/1'),'common')
    add('claim_sale_missing',lambda s,c:c.update(sale_event='absent'),'common')
    add('claim_negative_remaining',lambda s,c:c.update(remaining='-1/1'),'common')
    add('claim_issue_future',lambda s,c:c.update(issued='2030-01-01'),'common')
    add('clock_after_period',lambda s,c:s['book']['memory']['collection_clock'].update(cursor='2030-01-01'),'clock')
    add('current_term_missing',lambda s,c:c.update(current_term='absent'),'summaries')
    add('current_due_wrong',lambda s,c:c.update(due='2030-01-01'),'summaries')
    add('assessed_flag_wrong',lambda s,c:c.update(assessed=False),'summaries')
    add('latest_identity_wrong',lambda s,c:c.update(latest_assessment='imported'),'summaries')
    add('latest_date_wrong',lambda s,c:c.update(assessment_date='2030-01-01'),'summaries')
    add('latest_remaining_wrong',lambda s,c:c.update(assessed_remaining='1/1'),'summaries')
    add('latest_overdue_wrong',lambda s,c:c.update(overdue='1/1'),'summaries')
    def empty_bad(s,c):c.update(assessments={},assessed=False,latest_assessment='none',assessed_remaining='1/1',overdue='0/1')
    add('empty_assessment_summary_wrong',empty_bad,'summaries')
    return rows

def direct_components(state,spec,coverage):
    book=state['book'];definition=state['memory_definition'];schemas=state['schemas'];results={}
    results['common']=b.guards.assess(spec['common'],book,definition,schemas)
    values={'cursor':dict(status='known',value=book['memory']['collection_clock']['cursor']),
            'end':dict(status='known',value=book['period']['end_exclusive'])}
    lineage={key:dict(value=values[key]['value'],type=p.guards.DATE,kind='book_field',path=path)
      for key,path in [('cursor','/memory/collection_clock/cursor'),('end','/period/end_exclusive')]}
    manifest=spec['clock']['manifest'];h=core.digest(manifest)
    results['clock']=dict(values=values,lineage=lineage,assessment=b.t.c.guarded.assess({h:manifest},h,values,[]))
    for name in ('terms','assessments','summaries'):
        template=spec[name];iteration=coverage[template['iteration']['child_pointer'][1:]]
        query_cov={key:coverage[item['projection']['child_pointer'][1:]] for key,item in template['template']['queries'].items()}
        results[name]=b.d.f.run(state,template,coverage=iteration,query_coverages=query_cov)
    cov={key:coverage[source['child_pointer'][1:]] for key,source in spec['events']['sources'].items()}
    results['events']=b.d.run_bridge(state,spec['events'],coverages=cov)
    return results

def main():
    assert not (HERE/'checks.json').exists(),'passing_evidence_frozen'
    started=time.monotonic();checks=[];pairs=[];controls=[];oracle=[]
    def check(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-obligation-completion-20261026/source-lock.json')
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    for path in (HERE.parent/'nested-obligation-completion-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    for module in list(sys.modules.values()):
        file=getattr(module,'__file__',None)
        if not file:continue
        path=Path(file).resolve()
        if path.is_relative_to(ROOT) and path.is_file() and not path.is_relative_to(HERE):
            key=str(path.relative_to(ROOT))
            if key in lock:assert lock[key]==sha(path),key
            lock[key]=sha(path)
    if (HERE/'source-lock.json').exists():assert read(HERE/'source-lock.json')==lock,'dependency_drift'
    else:dump('source-lock.json',lock)
    evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases'];retained=[]
    for chart,case in evidence.items():
        states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
        retained.extend((chart+':'+label,state) for label,state in states)
    m=importlib.util.spec_from_file_location('prior_semantic_controls',HERE.parent/'nested-obligation-completion-20261026/controls.py')
    prior=importlib.util.module_from_spec(m);m.loader.exec_module(prior)
    base=evidence['alpha']['final'];mutations=prior.corruptions(base)+common_corruptions(base)
    for label,state in retained:
        terms.validate(state);oracle.append(dict(case=label,status='valid',state_sha256=core.digest(state)))
    for label,state,component in mutations:
        try:terms.validate(state);status='valid';reason=None
        except Exception as exc:status='invalid';reason=str(exc)
        check(status=='invalid',label+':native_rejects');oracle.append(dict(case=label,status=status,reason=reason,state_sha256=core.digest(state)))
    structural=deepcopy(base);structural['migration']['scope']='Unsupported replacement premise'
    try:terms.validate(structural);raise AssertionError('structural discriminator accepted')
    except core.Invalid as exc:oracle.append(dict(case='structural_scope_discriminator',status='invalid',reason=str(exc),state_sha256=core.digest(structural)))
    dump('native-oracle.json',oracle)
    templates={chart:d.build(case['final']) for chart,case in evidence.items()}
    def compare(label,state,spec,expected_status,component=None):
        before=p.order_digest(state);s_before=p.order_digest(spec);coverage=d.populations(state,spec)
        actual=d.run(state,spec,coverage=coverage);check('components' in actual,label+':all_components:'+actual.get('reason',''))
        expected=direct_components(state,spec,coverage)
        check(core.canonical(actual['components'])==core.canonical(expected),label+':six_full_subresults')
        check(set(actual['components'])==set(b.MEMBERS),label+':all_six_present')
        check(actual['status']==expected_status,label+':overall_status')
        if component:check(actual['component_statuses'][component]=='invalid',label+':target_component_rejects')
        total=sum((Fraction(c['remaining']) for c in state['book']['memory']['claims'].values()),Fraction(0))
        bound=actual['components']['common']['assessment']['bound_values']['total']
        check(bound==dict(status='known',value=f'{total.numerator}/{total.denominator}'),label+':original_claim_sum')
        check(actual['components']['clock']['values']['end']['value']==state['book']['period']['end_exclusive'],label+':exact_fiscal_boundary')
        check(not actual['structural_profile_admitted'] and not actual['method_eligible'] and all(actual[k] is False for k in p.FLAGS),label+':scope_flags')
        check(p.order_digest(state)==before and p.order_digest(spec)==s_before,label+':no_mutation')
        pairs.append(dict(case=label,state_sha256=core.digest(state),actual=actual,expected_components=expected));return actual
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native_financial_callback_in_semantic_bundle')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        for label,state in retained:compare(label,state,templates[label.split(':')[0]],'term_semantic_requirements_satisfied')
        for label,state,component in mutations:
            result=compare(label,state,templates['alpha'],'invalid',component);controls.append(dict(case=label,result=result))
        result=compare('structural_scope_discriminator',structural,templates['alpha'],'term_semantic_requirements_satisfied')
        controls.append(dict(case='structural_scope_discriminator',meaning='Native migration premise outside this semantic profile; no admission granted',result=result))
        structural_controls(base,templates['alpha'],check,controls,compare)
    finally:
        for module,name,value in saved:setattr(module,name,value)
        dump('assertions.json',checks)
    for n,h in lock.items():check(sha(ROOT/n)==h,'protected:'+n)
    dump('declarations.json',templates);dump('cases.json',pairs);dump('controls.json',controls);dump('assertions.json',checks)
    summary=dict(passed=True,retained_states=len(retained),complete_bundle_comparisons=len(pairs),controls=len(controls),
       assertions=len(checks),protected_files=len(lock),native_oracle_cases=len(oracle),
       native_financial_callbacks_disabled_during_candidate=True,full_native_validator_replacement=False)
    dump('checks.json',summary);git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/term-semantic-composition-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,
      data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-term-semantic-composition-20261026.md',
      result_file='data/accounting-master/term-semantic-composition-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('bundle.py','declaration.py','verify.py')},
      artifacts=['declarations.json','cases.json','controls.json','native-oracle.json','checks.json','assertions.json','source-lock.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def structural_controls(base,spec,check,controls,compare):
    def refused(label,s=spec,state=base,status='invalid',reason='',**kwargs):
        result=d.run(state,s,**kwargs);check(result['status']==status and reason in result.get('reason',''),label+':reason:'+result.get('reason',''))
        controls.append(dict(case=label,result=result))
    for key in ('claims','terms','assessments'):
        coverage=d.populations(base,spec);coverage[key]['status']='partial'
        result=d.run(base,spec,coverage=coverage);check(result['status']=='unresolved','partial_'+key)
        controls.append(dict(case='partial_'+key,result=result))
    refused('missing_populations',coverage={},reason='fields:bundle_populations')
    altered=deepcopy(spec);altered['residuals'].append('Changed selected declaration')
    refused('stale_reviewed_bundle',s=altered,selection=core.digest(spec),reason='reviewed_semantic_bundle')
    altered=deepcopy(spec);del altered['clock']
    refused('missing_component',s=altered,reason='fields:semantic_bundle')
    altered=deepcopy(spec);altered['clock']['bindings']['end']['pointer']='/date'
    result=d.run(base,altered);check(result['status']=='invalid','changed_fiscal_bound_rejects_cursor')
    controls.append(dict(case='changed_fiscal_bound',result=result))
    coverage=d.populations(base,spec);call=b.make_call(spec,base['book'],base['memory_definition'],base['schemas'],coverage,core.digest(spec))
    altered=deepcopy(base);claim=altered['book']['memory']['claims']['invoice/a~1'];claim['terms']=dict(reversed(list(claim['terms'].items())))
    refused('stale_book_order',state=altered,coverage=coverage,call=call,reason='stale_semantic_bundle_call')
    compare('reordered_semantic_state',altered,spec,'term_semantic_requirements_satisfied')

if __name__=='__main__':main()
