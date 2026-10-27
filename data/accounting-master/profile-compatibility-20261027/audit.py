"""One-shot anchored interface/edge inventory; no historical writer invocation."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast, json, subprocess, sys, time
from selection import INTERFACES, EDGES

H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def read(p):return json.loads(p.read_text())
assert len(sys.argv)==2
O=H/sys.argv[1];O.mkdir(exist_ok=False);start=time.monotonic()
locks={};checks=[];interfaces=[]
def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
def pin(p):
    p=Path(p);name=str(p.relative_to(R));digest=sha(p)
    if name in locks:check(locks[name]==digest,'consistent_identity:'+name)
    locks[name]=digest
    return dict(path=name,sha256=digest)
for spec in INTERFACES:
    p=B/spec['path'];text=p.read_text();tree=ast.parse(text)
    profile=[n.value.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROFILE' for t in n.targets) and isinstance(n.value,ast.Constant)]
    check(profile==[spec['profile']],spec['id']+':exact_profile')
    functions=[]
    for name in spec['functions']:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        functions.append(dict(name=name,signature=ast.unparse(node.args),line=node.lineno,end_line=node.end_lineno,
            source_sha256=sha256('\n'.join(text.splitlines()[node.lineno-1:node.end_lineno]).encode()).hexdigest()))
    result=dict(spec,source=pin(p),functions=functions)
    result['evidence_identity']=pin(B/spec['evidence'])
    check(read(B/spec['evidence'])['passed'],spec['id']+':retained_evidence_pass')
    folder=(B/spec['evidence']).parent;lock=folder/'source-lock.json'
    if not lock.exists():lock=(B/spec['path']).parent/'source-lock.json'
    if lock.exists():
        pin(lock)
        for path,digest in read(lock).items():
            check((R/path).is_file() and sha(R/path)==digest,spec['id']+':dependency:'+path)
    verify=(B/spec['path']).parent/'verify.py'
    if verify.exists():result['evidence_harness']=pin(verify)
    interfaces.append(result)
edge_rows=[]
for source,target,kind,meaning,anchor in EDGES:
    edge_rows.append(dict(source=source,target=target,disposition=kind,meaning=meaning,anchor=pin(B/anchor),
       independently_implemented=False))
# Verify the claimed structural distinction from the actual dispatcher.
selected=(B/'invariant-unicode-repair-20261026/company_text_unicode.py').read_text()
check("(recipe if kind=='scalar' else expansion).lower" in selected,'selected_recipe_dispatch')
check("eligibility.lower,'eligibility'" in selected,'selected_flat_eligibility_dispatch')
check('SelectedTermCommand/2' not in selected and 'execute_sources' not in selected,'no_term_executor_branch_in_selected_wrapper')
term=(B/'term-event-source-20261026/event_text.py').read_text()
check("full.execute(contract,rules,state,request,coverage,selection,call)" in term,'term_complete_execution_owner')
check("{'assessment','amendment','collection','carry'}" in term,'term_exact_rule_population')
check("native_callbacks_disabled=True" in (B/'term-event-source-20261026/verify.py').read_text(),'term_native_disabled_evidence')
check("source.split('\\n')" in (B/'invariant-unicode-repair-20261026/invariant_text_unicode.py').read_text()
      or "source.splitlines" not in (B/'invariant-unicode-repair-20261026/invariant_text_unicode.py').read_text(),'corrected_invariant_physical_line_reader')
for p in [H/'selection.py',H/'audit.py',R/'docs/plans/accounting-profile-compatibility-20261027.md']:pin(p)
dump(O/'interfaces.json',dict(scope='Seven inspected source entry points; all other profiles remain outside this inventory.',interfaces=interfaces,edges=edge_rows))
dump(O/'source-lock.json',locks)
lines=['# Selected source and transition compatibility','',
 'Candidate 5.51 remains governing. This reference identifies seven inspected interfaces and six composition edges. It is a scoped implementation reference, not a replacement for the complete language specification.','',
 'Source syntax, structural compilation, state admission, proposed transition and actual accounting/source admission are different stages. Error representation also differs: several frontends raise located exceptions while the old company compiler returns invalid records. Consumers must use the named interface contract.','']
for row in interfaces:
    lines+=['## '+row['profile'],'',row['input'],'','Result: '+row['output'],'','Failure: '+row['failure'],'','Semantic owner: '+row['owner'],'','Limits: '+row['limits'],'']
    for f in row['functions']:lines+=['- '+f['name']+'('+f['signature']+') — '+row['source']['path']+':'+str(f['line'])]
    lines+=['','Retained evidence: '+row['evidence_identity']['path']+'.','']
lines+=['## Composition edges','']
for edge in edge_rows:lines+=['- '+edge['source']+' → '+edge['target']+' ('+edge['disposition']+'): '+edge['meaning']]
lines+=['','## Remaining complete interface','',
 'The term-event source runner already lowers and executes complete assessment, amendment, collection and carry commands. Its historical harness supplies their ordered program, current state, independent selection, population and calls. The selected-company source path does not directly admit that nested term rule family. A generic relabel or event injection would lose structural/semantic coverage and carry constraints.','',
 'The smallest complete next deliverable is an explicit selected-term program envelope over this existing executor: exact source/resource identities, ordered requests and independently bound opening/coverage/selection; full successful prefix and first-refusal result; declared carry/report boundary. It must not regenerate selections or silently accept changed source. Reuse the two retained complete traces as comparators and include refusal, replay, resource and boundary controls. This defines one missing composition interface, not a new accounting method or a general whole-company compiler.','',
 'The modern transitive dependency bundle remains open. Before promoting a packaged interface, relocate its pure consumers and pin all imported modules and protected source resources. No archival verifier should be rerun.']
(H/'compatibility.md').write_text('\n'.join(lines)+'\n')
check(all(sha(R/p)==d for p,d in locks.items()),'all_sources_unchanged')
dump(O/'checks.json',dict(passed=True,checks=checks,interfaces=7,edges=6,requirements_closed=0,scope='Static consumer/call-chain and preserved-evidence verification; no new dynamic financial execution.'))
git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
dump(O/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/profile-compatibility-20261027/audit.py '+sys.argv[1],environment=sys.version,git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic source audit',wall_seconds=time.monotonic()-start,data_version=sha(O/'source-lock.json'),timestamp_utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/accounting-profile-compatibility-20261027.md',result_file=str((H/'result.md').relative_to(R))))
print(json.dumps(dict(passed=True,interfaces=7,edges=6,checks=len(checks),source_files=len(locks))))
