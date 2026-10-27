from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import projection as p
import receivable_term_history_v1 as terms
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(path):return json.loads(path.read_text())
def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def ptr(parts):return '/'+ '/'.join(x.replace('~','~0').replace('/','~1') for x in parts)
def equal(a,b):return p.core.canonical(a)==p.core.canonical(b)

def spec_for(state,kind):
    parent=state['memory_definition']['root']['fields']['claims']['values']
    child=parent['fields'][kind]['values']
    fields={'owner':dict(kind='parent_key',type=p.guards.TEXT),
            'identity':dict(kind='child_key',type=p.guards.TEXT),
            'parent_issued':dict(kind='parent_field',pointer='/issued',type=p.guards.DATE)}
    for name,node in child['fields'].items():
        fields[name]=dict(kind='child_field',pointer='/'+name,type=deepcopy(node['type']))
    return dict(profile=p.PROFILE,context=deepcopy(state['book']['context']),parent_pointer='/claims',
                child_pointer='/'+kind,fields=fields,residuals=['Projection of explicit supplied internal maps; no term-history validity'])

def expected_rows(state,kind):
    rows=[];groups=[];lineage=[]
    for owner,parent in state['book']['memory']['claims'].items():
        parent_path='/memory'+ptr(['claims',owner]);first=len(rows)
        for key,child in parent[kind].items():
            path='/memory'+ptr(['claims',owner,kind,key])
            values={'owner':owner,'identity':key,'parent_issued':parent['issued'],**child}
            row={k:{'status':'known','value':v} for k,v in values.items()}
            fields={}
            for field in row:
                if field=='owner':loc=parent_path;typ=p.guards.TEXT;binding='parent_key'
                elif field=='identity':loc=path;typ=p.guards.TEXT;binding='child_key'
                elif field=='parent_issued':loc=parent_path+'/issued';typ=p.guards.DATE;binding='parent_field'
                else:
                    loc=path+'/'+field;typ=state['book']['memory_types'][loc[len('/memory'):]];binding='child_field'
                fields[field]=dict(path=loc,kind=binding,type=typ)
            rows.append(row);lineage.append(dict(parent_key=owner,child_key=key,parent_path=parent_path,child_path=path,fields=fields))
        groups.append(dict(parent_key=owner,parent_path=parent_path,child_map_path=parent_path+'/'+kind,row_start=first,row_count=len(rows)-first))
    return rows,groups,lineage

def configure(state):
    d=p.types.derive(state['memory_definition'],state['book']['memory'],state['book'])
    assert d['status']=='typed',d
    state['book'].update(memory_types=d['memory_types'],memory_schema=d['schema_sha256'])
    state['schemas'][d['schema_sha256']]=d['schema']
    return state

def run(state,spec,coverage=None,call=None):
    coverage=coverage if coverage is not None else p.population(spec,state['book'],'complete','Supplied internal projection fixture')
    args=(spec,state['book'],state['memory_definition'],state['schemas'],coverage)
    return p.project(*args,p.make_call(*args) if call is None else call)

def main():
    started=time.monotonic();checks=[];cases=[];controls=[]
    def ensure(ok,label):checks.append(dict(check=label,passed=bool(ok)));assert ok,label
    lock=read(HERE.parent/'nested-term-invariant-audit-20261026/source-lock.json')
    for path in (HERE.parent/'nested-term-invariant-audit-20261026').iterdir():
        if path.is_file():lock[str(path.relative_to(ROOT))]=sha(path)
    dump('source-lock.json',lock)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    saved=[]
    for module,names in [(native,('validate','control','claim_type','event_types','make_request','run','protected')),
                         (terms,('validate','step','carry','migrate')),(operating,('build',))]:
        for name in names:saved.append((module,name,getattr(module,name)))
    def disabled(*a,**kw):raise AssertionError('native financial callback during projection')
    try:
        for module,name,_ in saved:setattr(module,name,disabled)
        evidence=read(HERE.parent/'receivable-term-history-20261025/evidence.json')['cases']
        for chart,case in evidence.items():
            states=[('migration',case['migration']['state'])]+[(f'event-{i}',r['result']['after']) for i,r in enumerate(case['steps'])]+[('carry',case['carry']['after'])]
            for label,state in states:
                before=p.order_digest(state)
                for kind in ('terms','assessments'):
                    spec=spec_for(state,kind);actual=run(state,spec)
                    ensure(actual['status']=='projected',chart+':'+label+':'+kind+':projected:'+actual.get('reason',''))
                    rows,groups,lineage=expected_rows(state,kind)
                    ensure(equal(actual['rows'],rows),chart+':'+label+':'+kind+':all_rows')
                    ensure(actual['groups']==groups and equal(actual['lineage'],lineage),chart+':'+label+':'+kind+':groups_lineage')
                    cases.append(dict(chart=chart,state=label,kind=kind,spec=spec,result=actual,expected_rows=rows,expected_groups=groups,expected_lineage=lineage))
                ensure(p.order_digest(state)==before,chart+':'+label+':unchanged')
        controls_for(evidence['alpha']['final'],ensure,controls)
    finally:
        for module,name,value in saved:setattr(module,name,value)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    dump('cases.json',cases);dump('controls.json',controls);dump('assertions.json',checks)
    summary=dict(passed=True,retained_states=22,full_projections=len(cases),controls=len(controls),assertions=len(checks),
        protected_files=len(lock),native_financial_callbacks_disabled=True,new_financial_validator=False,actual_population_completeness=False)
    dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
      command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/nested-map-projection-20261026/verify.py',
      environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-started,
      data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-nested-map-projection-20261026.md',
      result_file='data/accounting-master/nested-map-projection-20261026/result.md',
      implementation_sha256={n:sha(HERE/n) for n in ('projection.py','verify.py')},
      artifacts=['cases.json','controls.json','checks.json','assertions.json','source-lock.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

def controls_for(base,ensure,controls):
    spec=spec_for(base,'terms');coverage=p.population(spec,base['book'],'complete','Explicit test coverage')
    call=p.make_call(spec,base['book'],base['memory_definition'],base['schemas'],coverage)
    def refused(label,reason,state=base,definition=spec,pop=None,selected=None,status='invalid'):
        actual=run(state,definition,pop,selected)
        ensure(actual['status']==status and reason in actual.get('reason',''),label+':reason:'+actual.get('reason',''))
        ensure('rows' not in actual and 'groups' not in actual,label+':no_partial_result')
        controls.append(dict(case=label,result=actual))
    for status in ('partial','unknown'):
        pop=deepcopy(coverage);pop['status']=status
        refused('population_'+status,'complete_supplied_population_required',pop=pop,status='unresolved')
    for field,value,reason in [('book_sha256','0'*64,'population_book'),('child_pointer','/assessments','population_scope'),
                              ('status','inferred','population_status'),('provenance','','population_provenance')]:
        pop=deepcopy(coverage);pop[field]=value
        refused('population_'+field,reason,pop=pop)
    changed=deepcopy(base);changed['book']['date']='2028-02-01'
    refused('stale_book','stale_projection_call',state=changed,pop=coverage,selected=call)
    changed=deepcopy(base);claim=changed['book']['memory']['claims']['invoice/a~1'];claim['terms']=dict(reversed(list(claim['terms'].items())))
    ensure(p.core.digest(changed)==p.core.digest(base),'map_reorder_canonical_identity_same')
    refused('stale_book_order','stale_projection_call',state=changed,pop=coverage,selected=call)
    actual=run(changed,spec);ensure(actual['status']=='projected' and [x['child_key'] for x in actual['lineage']]==list(claim['terms']),'reordered_rows_retained')
    controls.append(dict(case='reordered_rows_retained',result=actual))
    changed_spec=deepcopy(spec);changed_spec['context']={}
    refused('wrong_context','projection_context',definition=changed_spec)
    changed_spec=deepcopy(spec);changed_spec['child_pointer']='/absent'
    refused('missing_child_path','record_path',definition=changed_spec)
    changed_spec=deepcopy(spec);changed_spec['fields']['due']['type']=p.guards.TEXT
    refused('wrong_declared_type','declared_field_type',definition=changed_spec)
    empty=deepcopy(base);empty['book']['memory']['claims']={};configure(empty)
    actual=run(empty,spec);ensure(actual['status']=='projected' and actual['rows']==actual['groups']==actual['lineage']==[],'empty_parent_map')
    controls.append(dict(case='empty_parent_map',result=actual))
    refused('wrong_type_empty_parent','declared_field_type',state=empty,definition=changed_spec)
    childempty=deepcopy(base);childempty['book']['memory']['claims']['invoice/a~1']['terms']={};configure(childempty)
    actual=run(childempty,spec);ensure(actual['status']=='projected' and actual['rows']==[] and len(actual['groups'])==1 and actual['groups'][0]['row_count']==0,'empty_child_group_retained')
    controls.append(dict(case='empty_child_group_retained',result=actual))
    changed_spec=deepcopy(spec);changed_spec['fields']['due']['pointer']='/absent'
    refused('bad_field_empty_child','record_path',state=childempty,definition=changed_spec)
    changed=deepcopy(base);claims=changed['book']['memory']['claims']
    claims['汉字/é~\u2028']=deepcopy(next(iter(claims.values())))
    configure(changed);actual=run(changed,spec)
    ensure(actual['status']=='projected' and len(actual['groups'])==2,'duplicate_local_ids_distinct_groups')
    ensure(len({(x['parent_key'],x['child_key']) for x in actual['lineage']})==len(actual['rows']),'raw_key_pairs_unique')
    for item in actual['lineage']:
        found,value=p.base.binding.located(changed['book']['memory'],item['child_path'][len('/memory'):])
        ensure(found and value==changed['book']['memory']['claims'][item['parent_key']]['terms'][item['child_key']],'unicode_escaped_path')
    controls.append(dict(case='duplicate_ids_unicode_ownership',result=actual))
    boundary(base,ensure,controls,refused)

def boundary(base,ensure,controls,refused):
    state=deepcopy(base);node={'node':'scalar','type':p.guards.TEXT}
    definition={'node':'map','max_items':3,'values':{'node':'record','fields':{
        'children':{'node':'map','max_items':128,'values':{'node':'record','fields':{'value':node}}}}}}
    state['memory_definition']['root']['fields']['projection_groups']=definition
    state['book']['memory']['projection_groups']={owner:{'children':{str(i):{'value':'v'} for i in range(128)}} for owner in ('a','b')}
    configure(state)
    spec=dict(profile=p.PROFILE,context=state['book']['context'],parent_pointer='/projection_groups',child_pointer='/children',
      fields={'value':dict(kind='child_field',pointer='/value',type=p.guards.TEXT)},residuals=['Synthetic structural limit fixture'])
    actual=run(state,spec)
    ensure(actual['status']=='projected' and len(actual['rows'])==256,'exact_row_limit:'+actual.get('reason',''))
    controls.append(dict(case='exact_row_limit',result=actual))
    state['book']['memory']['projection_groups']['c']={'children':{'0':{'value':'v'}}};configure(state)
    refused('row_overflow','row_limit',state=state,definition=spec)

if __name__=='__main__':main()
