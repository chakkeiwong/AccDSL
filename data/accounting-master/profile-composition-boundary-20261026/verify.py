from copy import deepcopy
from hashlib import sha256
import json, os, platform, subprocess, sys, time
import composition as m

HERE=m.HERE;ROOT=m.ROOT
def check(value,reason):
    if not value:raise AssertionError(reason)
def plan(name,stages,edges):return {'profile':m.PROFILE,'name':name,'stages':stages,'dependencies':edges}
def stage(identity,h,exchange):return {'id':identity,'packet_sha256':h,'exchange_id':exchange}
def edge(a,b,relation='sequence',left=None,right=None):
    return {'from':a,'to':b,'relation':relation,'produced_path':left or [],'consumed_path':right or []}
def main():
    start=time.monotonic();check(os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU hiding required')
    library=m.Library();hashes={e['name']:h for h,e in library.entries.items()};results=[];cases=[]
    for name in ('insurance','group'):
        h=hashes[name];reader=library.readers[h];xs=[x for x in library.packets[h]['exchanges'] if x['role']=='publication' and reader.body(x['response_ref']).get('disposition')=='completed']
        for a in xs:
            for b in xs:
                if a==b or a['world_after']!=b['world_before']:continue
                rq=reader.body(b['request_ref'])
                path=['heads','accounts'] if name=='insurance' else ['group_heads',rq['expected_head']['owner_key'],'state_ref']
                p=plan(name+':'+a['id'],[stage('first',h,a['id']),stage('report',h,b['id'])],[edge('first','report'),edge('first','report','state',path,path)])
                cases.append((p,'documentary_consistent'))
    check(len(cases)==66,'native pair inventory changed')
    ih=hashes['insurance'];ah=hashes['insurance-assessment'];bh=hashes['bank-assessment']
    incompatible=plan('foreign_account_head',[stage('component',ih,'gmm-half-service'),stage('assessment',ah,'route.full')],[edge('component','assessment','state',['heads','accounts'],['accounting_heads','Synthetic/Legal'])])
    cases.append((incompatible,'unsupported'))
    cases.append((plan('independent_queries',[stage('bank',bh,'capital.final'),stage('insurance',ah,'route.full')],[]),'documentary_consistent'))
    cases.append((plan('changed_world',[stage('a',ih,'gmm-half-service'),stage('b',ih,'group-membership.report')],[edge('a','b')]),'invalid'))
    cases.append((plan('missing_receipt_consumption',[stage('a',ih,'gmm-half-service'),stage('b',ih,'gmm-half-service.report')],[edge('a','b','receipt')]),'invalid'))
    cases.append((plan('duplicate_publication',[stage('a',ih,'gmm-half-service'),stage('b',ih,'gmm-half-service')],[]),'invalid'))
    cases.append((plan('partial_financial_handoff',[stage('a',ih,'group-unknown'),stage('b',ih,'gmm-half-service.report')],[edge('a','b','state',['heads','accounts'],['heads','accounts'])]),'unresolved'))
    cases.append((plan('unknown_acknowledgement',[stage('a',ah,'route.full.lost-after'),stage('b',ah,'route.full.retry-after')],[edge('a','b')]),'unresolved'))
    cases.append((plan('known_retry',[stage('a',ah,'route.full'),stage('b',ah,'route.full.replay')],[edge('a','b')]),'documentary_consistent'))
    cases.append((plan('refused_stage',[stage('a',ah,'route.full.conflict'),stage('b',ah,'route.full.replay')],[edge('a','b')]),'invalid'))
    cases.append((plan('wrong_head_path',[stage('a',ih,'gmm-half-service'),stage('b',ih,'gmm-half-service.report')],[edge('a','b','state',['heads','issued'],['heads','accounts'])]),'invalid'))
    cases.append((plan('non_state_path',[stage('a',ih,'gmm-half-service'),stage('b',ih,'gmm-half-service.report')],[edge('a','b','state',['heads','missing'],['heads','accounts'])]),'invalid'))
    out=HERE/'examples';out.mkdir(exist_ok=True)
    for i,(p,expected) in enumerate(cases):
        before=m.canonical(p);source=m.render(p);lowered,spans=m.parse(source)
        check(lowered==p and m.render(lowered)==source,'roundtrip')
        typed=m.assess(p,library);compiled=m.compile_text(source,library)
        check(compiled['assessment']==typed,'typed_text_findings_differ')
        check(typed['status']==expected,p['name']+':'+typed['status'])
        check(m.canonical(p)==before,'plan mutated')
        check(not any(typed[k] for k in ['execution_admission','source_admission','accounting_admission','concurrent_execution_admission']),'admission')
        check(len(spans['stages'])==len(p['stages']) and len(spans['dependencies'])==len(p['dependencies']),'source maps')
        check(m.parse(source.replace(chr(10),chr(13)+chr(10)))[0]==p,'CRLF mismatch')
        for s in p['stages']:
            r,x,d=library.select(s);actual=typed['stages'][s['id']]
            check(actual['descriptor']==d and actual['view_ref']==r.body(x['request_ref'])['view_ref'],'native evidence lost')
        stem=f'{i+1:03d}';(out/(stem+'.accdsl')).write_text(source)
        (out/(stem+'.json')).write_text(json.dumps({'plan':p,'source_map':spans,'assessment':typed},indent=2)+chr(10))
        results.append({'name':p['name'],'expected':expected,'actual':typed['status'],'findings':[f['reason'] for f in typed['findings']]})
    foreign=m.assess(incompatible,library)['findings'][0]['evidence']
    check(foreign['produced_ref']['schema']=='accdsl.insurance-components.ownerstate.v1' and foreign['consumed_ref']['schema']=='accdsl.insurance-assessment.accountinghead.v1','actual incompatible schemas lost')
    malformed=[];base=deepcopy(cases[0][0])
    mutations=[('duplicate_stage',lambda p:p['stages'].append(deepcopy(p['stages'][0]))),
      ('missing_dependency_stage',lambda p:p['dependencies'][0].update(to='missing')),
      ('cycle_or_order',lambda p:p['dependencies'][0].update(to='first',**{'from':'report'})),
      ('duplicate_edge',lambda p:p['dependencies'].append(deepcopy(p['dependencies'][0]))),
      ('unresolved_packet',lambda p:p['stages'][0].update(packet_sha256='0'*64)),
      ('unresolved_exchange',lambda p:p['stages'][0].update(exchange_id='not_retained')),
      ('unsupported_adapter',lambda p:p['dependencies'][0].update(relation='automatic_currency_conversion')),
      ('unknown_field',lambda p:p.update(callback='execute_arbitrary_code'))]
    for name,change in mutations:
        p=deepcopy(base);change(p)
        try:m.assess(p,library)
        except m.Invalid as exc:malformed.append({'case':name,'refusal':str(exc)})
        else:raise AssertionError(name+' accepted')
    source=m.render(base)
    for name,source_bad in [('invalid_utf8',bytes([255])),('bom',chr(65279)+source),
            ('trailing',source+'stage "x" "y" "z";'),('bare_cr',source+chr(13)),
            ('unicode_line_separator',source+chr(8232)),('incomplete',source.replace('end_composition;',''))]:
        try:m.parse(source_bad)
        except m.Invalid as exc:malformed.append({'case':name,'refusal':str(exc)})
        else:raise AssertionError(name+' accepted')
    multi=deepcopy(incompatible);multi['stages'].append(stage('unknown',ah,'route.full.lost-after'))
    multi['stages'].append(stage('duplicate',ih,'gmm-half-service'))
    assessed=m.assess(multi,library)
    check(assessed['status']=='invalid' and {f['status'] for f in assessed['findings']}=={'invalid','unsupported','unresolved'},'findings precedence lost')
    chain=plan('transitive_unknown',[stage('a',ah,'route.full.lost-after'),stage('b',ah,'route.full.retry-after'),stage('c',ah,'route.full.replay')],[edge('a','b'),edge('b','c')])
    availability=m.assess(chain,library)['dependency_availability']
    check(all(availability[k]['status']=='unresolved' for k in ['a','b','c']),'unknown dependency did not propagate')
    check('predecessor_unavailable:b' in availability['c']['reasons'],'transitive cause lost')
    # No retained receiving request currently consumes a receipt: do not claim
    # positive receipt-handoff conformance from negative-only evidence.
    receipt_consumers=0
    for h,reader in library.readers.items():
        for x in library.packets[h]['exchanges']:
            if reader.body(x['response_ref']).get('disposition') in {'completed','partial'}:
                receipt_consumers+=any('Receipt' in reader.registry[d]['kind'] for d in reader.closure([x['request_ref']]))
    check(receipt_consumers==0,'receipt positive coverage must be reviewed')
    for path,h in library.lock['files'].items():check(sha256((ROOT/path).read_bytes()).hexdigest()==h,'source changed')
    report={'status':'passed_bounded_documentary_composition','matched_cases':len(results),'native_sequences':66,
        'malformed_cases':malformed,'cases':results,'combined_findings_preserved':True,'source_files_preserved':len(library.lock['files']),
        'actual_cross_profile_adapter':'unsupported','transitive_unknown_preserved':True,
        'positive_receipt_handoffs':receipt_consumers,'execution_admission':False,'readiness':'not_ready'}
    (HERE/'checks.json').write_text(json.dumps(report,indent=2)+chr(10))
    files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='run-manifest.json']
    manifest={'git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/profile-composition-boundary-20261026/verify.py',
        'environment':{'python':platform.python_version(),'executable':sys.executable,'libraries':'standard library and pinned local syntax/descriptor helpers'},
        'cpu_gpu':'CPU only; GPU intentionally hidden; no GPU libraries imported','random_seeds':'N/A: deterministic',
        'wall_seconds':round(time.monotonic()-start,3),'data_version':'source-lock.json','plan':library.lock['plan'],
        'result':'data/accounting-master/profile-composition-boundary-20261026/result.md',
        'artifacts':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}}
    (HERE/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','malformed_cases']}|{'malformed_cases':len(malformed)}))

if __name__=='__main__':main()
