"""Create complete documentary fixtures and pin retained source choices, once."""
from pathlib import Path
import json,hashlib,copy,tomllib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
assert not (OUT/'source-selection.json').exists()
UP=ROOT/'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream'
dossier=ROOT/'data/accounting-master/taxonomy-reuse-20261007/adapter-dossier.json'
d=json.loads(dossier.read_text());pins={}
def pin(p,expected=None):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 h=sha(p);assert expected is None or h==expected,str(p);pins[str(p.relative_to(ROOT))]=h
pin(dossier)
for row in d['source_anchors'].values():pin(row['path'],row['sha256'])
for row in d['proposed_input']['uri_map'].values():pin(row['path'],row['sha256'])
pin(d['source_dependency_snapshot']['graph'],d['source_dependency_snapshot']['sha256'])
for rel in ['data/accounting-master/tableformer-loader-20261010/result.md','data/accounting-master/easyocr-weight-rights-20261011/result.md','docs/design/proposal/methods/preparation-20261005-v1/03-adapters/adapter-cases-v1.json']:
 pin(rel)
for name in ['arelle','docling','docling-core','pdfplumber']:pin(UP/(name+'-commit.json'))
for name in ['arelle','docling','docling-core']:pin(UP/name/'pyproject.toml')
pin(UP/'pdfplumber/README.md')
py=tomllib.loads((UP/'arelle/pyproject.toml').read_text())
assert py['project']['dependencies']==d['proposed_environment']['base_requirements']
selection={'schema':'DocumentarySourceSelection/1','status':'documentary_source_selection','date':'2026-10-15','selected_native':{'name':'Arelle','commit':d['code_commit'],'role':'optional first native-XBRL adapter','options':d['proposed_runtime_options'],'base_constraints':py['project']['dependencies'],'build_constraints':py['build-system']['requires'],'extras':[]},'pdf_baseline':{'name':'pdfplumber','commit':json.loads((UP/'pdfplumber-commit.json').read_text())['sha'],'role':'machine-generated PDF geometry comparator'},'not_selected':['Docling full model path','TableFormer weights/runtime','EasyOCR weights/runtime','standard/all optional extras','GPU runtime'],'taxonomy_graph':d['source_dependency_snapshot'],'uri_map':d['proposed_input']['uri_map'],'environment_lock':None,'runtime_admission':'held','unresolved':['Actual target platform and Python build','Exact transitive package versions/hashes and notices','Runtime API/output compatibility','Historical FASB and component XBRL terms applicability','Model checkpoint identities/terms for non-selected model paths'],'terms_dispositions':d['distribution_dispositions'],'source_pins':[{'path':p,'sha256':h} for p,h in sorted(pins.items())]}
write(OUT/'source-selection.json',selection)
body='synthetic source: raw=1,234; transform=comma_grouping; scale=-3; concept=Revenue; context=c1; unit=USD; nil=false; precision=2\n'
resource={'uri':'fixture:source','body':body,'sha256':digest(body)}
context={'id':'c1','entity':'synthetic-entity','perimeter':'separate','period_kind':'duration','start':'2024-01-01','end_exclusive':'2025-01-01','dimensions':[]}
fact={'occurrence':'occ-1','source_uri':'fixture:source','source_span':[0,len(body)],'concept':'Revenue','raw':'1,234','transform':'comma_grouping','scale':-3,'precision':2,'context_id':'c1','unit_id':'USD','nil':False}
base={'schema':'DocumentaryAdapterExchange/1','case_id':'A01','evidence_class':'authored_expected_not_runtime','request':{'id':'request-A01','selection_sha256':sha(OUT/'source-selection.json'),'resources':[resource],'required_uris':['fixture:source'],'contexts':[context],'units':[{'id':'USD','measure':'iso4217:USD'}],'transforms':['comma_grouping'],'facts':[fact],'control':{'cancel_after':None,'prior_request_digest':None,'prior_receipt':None}},'expected':{'status':'proposed','records':[{'occurrence':'occ-1','context_id':'c1','unit_id':'USD','raw':'1,234','value':'1.234','nil':False,'review':'proposed'}],'unresolved':[],'diagnostics':[],'accounting_committed':False,'package_complete':False}}
cases=[base]
def case(i):
 x=copy.deepcopy(base);x['case_id']=i;x['request']['id']='request-'+i;cases.append(x);return x
x=case('A02');x['request']['facts'][0]['nil']=True;x['expected']['records'][0].update(value=None,nil=True)
x=case('A03');c=copy.deepcopy(context);c['id']='c2';c['start']='2023-01-01';c['end_exclusive']='2024-01-01';x['request']['contexts'].append(c);f=copy.deepcopy(fact);f.update(occurrence='occ-2',context_id='c2');x['request']['facts'].append(f);r=copy.deepcopy(x['expected']['records'][0]);r.update(occurrence='occ-2',context_id='c2');x['expected']['records'].append(r)
for i,change,diagnostic in [('A04','missing_resource','unresolved_dependency'),('A05','hash_mismatch','resource_hash_mismatch'),('A06','unknown_transform','unsupported_transform'),('A07','missing_context','missing_context'),('A08','typed_dimension','missing_typed_dimension')]:
 x=case(i)
 if change=='missing_resource':x['request']['resources']=[]
 if change=='hash_mismatch':x['request']['resources'][0]['body']+='changed'
 if change=='unknown_transform':x['request']['facts'][0]['transform']='unadmitted'
 if change=='missing_context':x['request']['contexts']=[]
 if change=='typed_dimension':x['request']['contexts'][0]['dimensions']=[{'axis':'Axis','kind':'typed','value':None}]
 x['expected'].update(status='unresolved',records=[],unresolved=['occ-1'],diagnostics=[diagnostic])
x=case('A09');x['request']['facts'].append(dict(fact,occurrence='occ-2'));x['request']['control']['cancel_after']=1;x['expected'].update(status='partial',unresolved=['occ-2'],diagnostics=['cancelled'])
def request_digest(req):
 d=copy.deepcopy(req);d.pop('control');return digest(json.dumps(d,sort_keys=True,separators=(',',':')))
x=case('A10');x['request']['control']['prior_request_digest']=request_digest(x['request']);x['request']['control']['prior_receipt']='proposal-A10';x['expected']['diagnostics']=['idempotent_replay']
x=case('A11');x['request']['control']['prior_request_digest']='0'*64;x['request']['control']['prior_receipt']='proposal-A11';x['expected'].update(status='conflict',records=[],unresolved=['occ-1'],diagnostics=['request_identity_conflict'])
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'DocumentaryAdapterExchange/1','type':'object','additionalProperties':False,'required':['schema','case_id','evidence_class','request','expected'],'properties':{'schema':{'const':'DocumentaryAdapterExchange/1'},'case_id':{'type':'string'},'evidence_class':{'const':'authored_expected_not_runtime'},'request':{'type':'object','additionalProperties':False,'required':list(base['request']),'properties':{k:{'type':('array' if isinstance(v,list) else 'object' if isinstance(v,dict) else 'string')} for k,v in base['request'].items()}},'expected':{'type':'object','additionalProperties':False,'required':list(base['expected']),'properties':{'status':{'enum':['proposed','unresolved','partial','conflict']},'records':{'type':'array'},'unresolved':{'type':'array','items':{'type':'string'}},'diagnostics':{'type':'array','items':{'type':'string'}},'accounting_committed':{'const':False},'package_complete':{'const':False}}}}}
# Exact field sets for nested records are enforced independently by the verifier.
write(OUT/'exchange-envelope.schema.json',schema);write(OUT/'exchanges.json',cases)
write(OUT/'baseline.json',{'candidate':'docs/design/proposal/manuscript-future-validation-20261015','pdf_sha256':sha(ROOT/'docs/design/proposal/manuscript-future-validation-20261015/accounting-product-proposal.pdf'),'index_sha256':hashlib.sha256(subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)).hexdigest()})
print(json.dumps({'source_pins':len(pins),'base_requirements':len(py['project']['dependencies']),'exchanges':len(cases),'runtime_admission':'held'}))
