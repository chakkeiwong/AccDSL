from pathlib import Path
import json,tomllib
ROOT=Path(__file__).resolve().parents[3]
UP=ROOT/'docs/design/proposal/methods/preparation-20261005-v1/03-adapters/sources/upstream'
for name in ['arelle','docling','docling-core']:
 p=UP/name/'pyproject.toml';d=tomllib.loads(p.read_text());j=json.loads((UP/(name+'-commit.json')).read_text());project=d.get('project',{});poetry=d.get('tool',{}).get('poetry',{})
 print(json.dumps({'name':name,'commit':j.get('sha',j.get('commit')),'project':{k:project.get(k) for k in ['name','version','requires-python','dependencies','optional-dependencies']},'poetry_dependencies':poetry.get('dependencies')},ensure_ascii=False))
for rel in ['data/accounting-master/taxonomy-reuse-20261007/adapter-dossier.json','data/accounting-master/tableformer-loader-20261010/run-manifest.json']:
 d=json.loads((ROOT/rel).read_text());print(json.dumps({'path':rel,'keys':list(d),'summary':{k:v for k,v in d.items() if k in ['status','code_commit','scope','selected','candidate','runtime','lock']}}))
