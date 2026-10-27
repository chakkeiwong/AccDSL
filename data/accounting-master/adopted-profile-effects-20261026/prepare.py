"""Capture exact providers and small, inspectable reader/evaluator deltas."""
from pathlib import Path
from hashlib import sha256
import ast
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MASTER=HERE.parent
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(name,v):(HERE/name).write_text(json.dumps(v,indent=2)+'\n')
assert not (HERE/'source-lock.json').exists()
files={}
def protect(path):files[str(path.relative_to(ROOT))]=sha(path)
for folder in ['insurance-identity-adoption-20261026','exact-bank-profile-adoption-20261026','exact-native-timing-20261026','exact-information-time-20261026','profile-publication-effects-20261026','profile-composition-boundary-20261026']:
 for path in (MASTER/folder).glob('*'):
  if path.is_file() and path.suffix in {'.py','.json','.md'}:protect(path)
for path in (MASTER/'exact-bank-profile-adoption-20261026/examples').glob('*.json'):protect(path)
for folder in ['profile-composition-boundary-20261026','insurance-identity-adoption-20261026','exact-bank-profile-adoption-20261026']:
 data=json.loads((MASTER/folder/'source-lock.json').read_text())
 for path,h in data.get('files',data).items():
  if isinstance(h,str) and len(h)==64:
   assert sha(ROOT/path)==h;files[path]=h
protect(ROOT/'docs/design/proposal/manuscript-insurance-identity-20261026/accounting-product-proposal.pdf')
dump('source-lock.json',files)
original=MASTER/'profile-publication-effects-20261026/descriptor.py'
source=original.read_text();changed=source.replace('class Descriptor:', 'class SchemaBoundDescriptor:',1)
delta=[]
for kind in ['Submission','TransportObservation','OperationRequest','OperationResult','Receipt','ReportReceipt','PublicationReceipt']:
 old="self.prefix + '"+kind.lower()+".v1'";new="self.schema_id('"+kind+"')"
 count=changed.count(old)
 if count:changed=changed.replace(old,new);delta.append(dict(old=old,new=new,count=count))
old="self.prefix + expected_kind.lower() + '.v1'";new='self.schema_id(expected_kind)'
assert changed.count(old)==1;changed=changed.replace(old,new);delta.append(dict(old=old,new=new,count=1))
(HERE/'schema_descriptor.py').write_text(changed)
comp=MASTER/'profile-composition-boundary-20261026/composition.py'
text=comp.read_text();tree=ast.parse(text);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='assess')
function='\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])
old="            elif edge['relation']=='state' and da['disposition']=='partial':"
new="            elif da.get('execution_binding',{}).get('identity_policy_ref')!=db.get('execution_binding',{}).get('identity_policy_ref'):\n                status,reason='unsupported','execution_policy_adapter_missing'\n"+old
assert function.count(old)==1
function=function.replace(old,new)
(HERE/'composition_assess.py').write_text('"""Original evaluator plus explicit execution-policy mismatch finding."""\nfrom copy import deepcopy\nfrom composition import validate,canonical,path_value,requested_heads,Invalid,PROFILE\nfrom hashlib import sha256\n\n'+function+'\n')
dump('reader-delta.json',dict(descriptor_source=str(original.relative_to(ROOT)),descriptor_sha256=sha(original),schema_replacements=delta,adapted_descriptor_sha256=sha(HERE/'schema_descriptor.py'),composition_source=str(comp.relative_to(ROOT)),composition_sha256=sha(comp),composition_inserted_before=old,composition_replacement=new,adapted_composition_sha256=sha(HERE/'composition_assess.py')))
print(json.dumps(dict(protected_files=len(files),schema_expressions=sum(x['count'] for x in delta),composition_insertions=1)))
