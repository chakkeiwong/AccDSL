"""Read-only bounded Core 0 conformance; all writes go to a fresh output dir."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import importlib.metadata, json, sys, time

ROOT=Path(__file__).resolve().parents[1]
assert len(sys.argv)==2, 'supply a fresh output directory'
OUT=Path(sys.argv[1]).resolve()
assert OUT.is_relative_to(ROOT), 'output must be inside the relocated bundle'
OUT.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(ROOT/'scripts'))
import core_semantics as core
import build_demo_registry as registry_builder
import jsonschema

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
manifest=json.loads((ROOT/'bundle-manifest.json').read_text())
checks=[];reads=set();start=time.monotonic()
def check(ok,name,**detail):
    checks.append(dict(name=name,passed=bool(ok),**detail))
    assert ok,name
def audit(event,args):
    if event!='open' or not isinstance(args[0],(str,bytes)):return
    p=Path(args[0]).resolve()
    mode=args[1]
    writing=isinstance(mode,str) and any(x in mode for x in 'wax+')
    if writing and not p.is_relative_to(OUT):raise AssertionError('write_outside_fresh_output:'+str(p))
    if p.is_relative_to(ROOT):reads.add(str(p.relative_to(ROOT)));return
    # Runtime libraries are separately recorded; no project/home fallback.
    if p.is_relative_to(Path(sys.base_prefix).resolve()):return
    raise AssertionError('undeclared_external_file:'+str(p))

def integrity(root):
    for item in manifest['files']:
        p=(root/item['path']).resolve()
        if not p.is_relative_to(root.resolve()):return 'outside_root'
        if not p.is_file():return 'missing_dependency'
        if sha(p)!=item['sha256']:return 'corrupt_dependency'
    return 'pass'

try:
    check(Path(core.__file__).resolve().is_relative_to(ROOT),'validator_loaded_from_bundle')
    check(Path(registry_builder.__file__).resolve().is_relative_to(ROOT),'registry_loaded_from_bundle')
    versions={n:importlib.metadata.version(n) for n in manifest['environment']['distributions']}
    check(versions==manifest['environment']['distributions'],'dependency_versions_match',observed=versions)
    sys.addaudithook(audit)
    check(integrity(ROOT)=='pass','all_bundle_hashes')
    read=lambda n:core.strict_json((ROOT/'docs/design'/n).read_text())
    doc=read('fixtures/core-ir-demo.json');registry=read('fixtures/core-demo-registry.json');schema=read('spec/core-ir.schema.json')
    structural=jsonschema.Draft202012Validator(schema)
    jsonschema.Draft202012Validator.check_schema(schema)
    def positive(name,change=lambda d,r:None):
        d,r=deepcopy(doc),deepcopy(registry);change(d,r)
        result=core.validate(d,r,schema,ROOT)
        check(result['status']=='passed' and result['coverage_claims_verified'] is False,name,result=result)
    def negative(name,expected,change):
        d,r=deepcopy(doc),deepcopy(registry);change(d,r)
        structural.validate(d)
        try:core.validate(d,r,schema,ROOT)
        except core.Invalid as e:check(e.code==expected,name,expected=expected,observed=e.code)
        else:raise AssertionError(name+':unexpected_acceptance')
    def node(d,section,name):return next(v for v in d[section] if v['id']==name)
    positive('complete_authored_fixture')
    positive('equivalent_timezone',lambda d,r:node(d,'documents','synthetic-note-document').update(available='2025-12-31T19:00:00-05:00'))
    def reorder(d,r):
        for v in d.values():
            if isinstance(v,list):v.reverse()
        r['records'].reverse()
    positive('record_order_independence',reorder)
    negative('unknown_expression_target','UnknownReference',lambda d,r:node(d,'expressions','alpha.ref').update(target='absent'))
    negative('wrong_money_context','TypeMismatch',lambda d,r:node(d,'expressions','debt.value').update(type='Money<EUR>'))
    negative('future_public_evidence','FutureEvidence',lambda d,r:node(d,'documents','synthetic-note-document').update(available='2026-01-02T00:00:00Z'))
    negative('source_literal_corruption','SourceLiteralMismatch',lambda d,r:node(d,'sourceSpans','synthetic-note-7').update(literal='Debt 101'))
    negative('unbalanced_opening','UnbalancedState',lambda d,r:d['states'][0]['balances'][0].update(signed_amount={'n':'96','d':'1'}))
    negative('omitted_explicit_zero','IncompleteState',lambda d,r:d['states'][0]['balances'].pop())
    negative('stale_export_bytes','StaleArtifact',lambda d,r:next(v for v in r['records'] if v['artifact']).update(sha256='0'*64))
    negative('unsupported_registry_escape','RegistryBinding',lambda d,r:next(v for v in r['records'] if v['artifact']).update(artifact='../outside.json'))
    # A modified candidate root must fail preflight before semantic execution.
    missing=OUT/'missing-root';missing.mkdir()
    check(integrity(missing)=='missing_dependency','missing_dependency_preflight')
    corrupt=OUT/'corrupt-root';corrupt.mkdir()
    first=manifest['files'][0];target=corrupt/first['path'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'corrupt\n')
    check(integrity(corrupt)=='corrupt_dependency','corrupt_dependency_preflight')
    check(integrity(ROOT)=='pass','original_bundle_unchanged')
    dump(OUT/'checks.json',dict(passed=True,checks=checks,project_reads=sorted(reads),wall_seconds=time.monotonic()-start,
        scope='Historical authored-debt admission only; no compiler, accounting or general profile acceptance.'))
    print(json.dumps(dict(passed=True,checks=len(checks),positive_semantic=3,negative_semantic=8,project_reads=len(reads))))
except Exception as e:
    dump(OUT/'failure.json',dict(error=repr(e),checks=checks,project_reads=sorted(reads)))
    raise
