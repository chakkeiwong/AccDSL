from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
paths=[
 'data/accounting-master/taxonomy-reuse-20261007/adapter-dossier.json',
 'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/source-register.json',
 'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/adapter-cases-v1.json',
 'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream/pdfplumber-commit.json',
]
for rel in paths:
 d=json.loads((ROOT/rel).read_text())
 if 'adapter-dossier' in rel:
  keys=['source_dependency_snapshot','proposed_runtime_options','proposed_environment','proposed_input','distribution_dispositions','acceptance']
  out={k:d[k] for k in keys};out['exchange_summary']=[{'keys':list(x),'identity':{k:v for k,v in x.items() if k in ['id','name','case','status','result_status']}} for x in d['exchanges']] if isinstance(d['exchanges'],list) else d['exchanges']
 elif 'commit' in rel:out={'sha':d.get('sha'),'url':d.get('url')}
 else:out={'keys':list(d) if isinstance(d,dict) else 'list','record_count':len(d.get('records',d.get('cases',[]))) if isinstance(d,dict) else len(d),'example':d.get('records',d.get('cases',[]))[:1] if isinstance(d,dict) else d[:1]}
 print(json.dumps({'path':rel,'result':out},ensure_ascii=False))
