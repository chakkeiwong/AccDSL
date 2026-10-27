"""Isolated selected-term execution against exact full-result commitments."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json, sys, time
ROOT=Path(__file__).resolve().parents[1]
assert len(sys.argv)==2
OUT=(ROOT/sys.argv[1]).resolve();assert OUT.is_relative_to(ROOT)
OUT.mkdir(parents=True,exist_ok=False)
reads=set();checks=[];start=time.monotonic()
def audit(event,args):
    if event!='open' or not isinstance(args[0],(str,bytes)):return
    path=Path(args[0]).resolve();mode=args[1]
    if isinstance(mode,str) and any(c in mode for c in 'wax+') and not path.is_relative_to(OUT):
        raise AssertionError('write_outside_output:'+str(path))
    if path.is_relative_to(ROOT):reads.add(str(path.relative_to(ROOT)));return
    if path.is_relative_to(Path(sys.base_prefix).resolve()):return
    raise AssertionError('undeclared_external_read:'+str(path))
sys.addaudithook(audit)
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
manifest=read(ROOT/'bundle-manifest.json')
def integrity(root):
    for item in manifest['files']:
        p=(root/item['path']).resolve()
        if not p.is_relative_to(root.resolve()):return 'outside_root'
        if not p.is_file():return 'missing'
        if sha(p)!=item['sha256']:return 'corrupt'
    return 'pass'
saved=[]
try:
    check(integrity(ROOT)=='pass','bundle_integrity')
    sys.path.insert(0,str(ROOT/'data/accounting-master/selected-term-program-20261027'))
    import program as p
    import receivable_term_history_v1 as native
    for mod,names in [(native,('validate','step','carry','migrate','state_request','event_types','literal','protected','claim_type','term_type','assessment_type')),
      (native.life,('validate','control','claim_type','event_types','make_request','run','protected')),(native.life.operating,('build','conditions'))]:
        for name in names:saved.append((mod,name,getattr(mod,name)))
    def disabled(*a,**kw):raise AssertionError('native_callback_in_relocated_program')
    for mod,name,_ in saved:setattr(mod,name,disabled)
    for chart in ['alpha','beta']:
        obj=read(ROOT/'inputs'/f'{chart}-program.json');s=read(ROOT/'inputs'/f'{chart}-selection.json');oracle=read(ROOT/'inputs'/f'{chart}-oracle.json')
        before=p.core.digest(obj);actual=p.execute(obj,s['selection'],s['expected_sha256'])
        check(actual['status']=='complete_provisional' and actual['successful_commands']==10,chart+':complete')
        check(p.core.digest(actual)==oracle['canonical_sha256'],chart+':full_canonical_result')
        check(p.source.full.p.order_digest(actual)==oracle['order_sha256'],chart+':full_order_result')
        check(p.core.canonical(actual['after'])==p.core.canonical(oracle['final_state']),chart+':complete_final_state')
        check(p.core.digest(obj)==before,chart+':input_unchanged')
        dump(OUT/f'{chart}-result-commitment.json',dict(canonical_sha256=p.core.digest(actual),order_sha256=p.source.full.p.order_digest(actual),successful_commands=actual['successful_commands']))
        del actual
    obj=read(ROOT/'inputs/alpha-program.json');s=read(ROOT/'inputs/alpha-selection.json')
    bad=deepcopy(obj);bad['rule_sources']['carry']+='\n'
    result=p.execute(bad,s['selection'],s['expected_sha256'])
    check(result['status']=='invalid_program' and result['reason']=='selected_program_sha256','unselected_source_refused')
    bad=deepcopy(obj);bad['commands'][0]['request']['event']['inputs']['approved']['value']=dict(status='unknown',reason='No supplied approval')
    selection=dict(profile=p.SELECTION,**p.identities(bad),term_selection=s['selection']['term_selection'])
    result=p.execute(bad,selection,p.core.digest(selection))
    check(result['status']=='refused' and result['failed_result']['execution']['status']=='unresolved','unknown_approval_retained')
    check(p.core.canonical(result['after'])==p.core.canonical(obj['opening']),'refused_opening_unchanged')
    missing=OUT/'missing-root';missing.mkdir();check(integrity(missing)=='missing','missing_dependency')
    corrupt=OUT/'corrupt-root';corrupt.mkdir();first=manifest['files'][0];q=corrupt/first['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b'corrupt\n')
    check(integrity(corrupt)=='corrupt','corrupt_dependency')
    loaded={str(Path(m.__file__).resolve().relative_to(ROOT)) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT) and Path(m.__file__).is_file()}
    declared={v['path'] for v in manifest['files']}
    check(loaded<=declared,'all_loaded_project_modules_declared')
    check(integrity(ROOT)=='pass','bundle_unchanged')
    dump(OUT/'checks.json',dict(passed=True,checks=checks,project_reads=sorted(reads),loaded_project_modules=sorted(loaded),native_callbacks_disabled=True,wall_seconds=time.monotonic()-start,full_release_bundle=False))
    print(json.dumps(dict(passed=True,checks=len(checks),loaded_project_modules=len(loaded),complete_commands=20)))
except Exception as e:
    dump(OUT/'failure.json',dict(error=repr(e),checks=checks,project_reads=sorted(reads)));raise
finally:
    for mod,name,value in saved:setattr(mod,name,value)
