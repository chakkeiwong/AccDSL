"""Check the precise identity distinction used by the main-chapter repair."""
from pathlib import Path
from hashlib import sha256
import json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
UNIT=HERE.parent/'common-program-authoring-20261026';sys.path.insert(0,str(UNIT))
import common_text as t
source=(UNIT/'examples/alpha.acc').read_bytes().decode()
resources=json.loads((UNIT/'examples/alpha.resources.json').read_text())
changed=source.replace('account_map ','account_map  ',1);assert changed!=source
original=t.compile_text(source,resources);formatted=t.compile_text(changed,resources)
assert original['status']==formatted['status']=='compiled_structural'
def first(compiled):
 b=compiled['program'];command=b['commands'][0];h=command['registry_sha256'];registry=b['registries'][h]
 entry=registry['entries'][command['method_key']]
 call={'profile':t.methods.PROFILE,'expected_state_sha256':t.digest(b['opening']),'expected_registry_sha256':h,
  'registry':registry,'method_key':command['method_key'],'event':command['event']}
 return entry,t.methods.materialize(b['opening'],call)
before,r1=first(original);after,r2=first(formatted)
assert before['method']==after['method'] and before['method_sha256']==after['method_sha256']
assert before['source_sha256']!=after['source_sha256'] and original['program_sha256']!=formatted['program_sha256']
assert r1==r2
result={'passed':True,'change':'One additional space after first account_map keyword',
 'lowered_method_equal':True,'method_sha256_equal':True,'source_sha256_changed':True,
 'program_sha256_changed':True,'first_materialized_request_equal':True,
 'scope':'Exact checked authored-program profile; no universal formatting theorem',
 'source_files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [UNIT/'common_text.py',UNIT/'examples/alpha.acc',UNIT/'examples/alpha.resources.json']}}
(HERE/'identity-check.json').write_text(json.dumps(result,indent=2)+chr(10));print(json.dumps({k:v for k,v in result.items() if k!='source_files'}))
