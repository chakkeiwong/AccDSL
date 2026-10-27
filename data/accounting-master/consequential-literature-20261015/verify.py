from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
base=json.loads((OUT/'baseline.json').read_text());rec=json.loads((OUT/'ledger-reconciliation.json').read_text())
for row in base['files']:
 p=ROOT/row['path']
 if p.suffix!='.json':ck('candidate-preserved/'+p.name,sha(p)==row['sha256'])
for n,count in rec['before'].items():
 old=json.loads((OUT/'six-ledgers-before'/(n+'.json')).read_text());new=json.loads((ROOT/'docs/design/research'/(n+'.json')).read_text())
 ck(n+'/historical-rows',new['records'][:count]==old['records'])
 ck(n+'/historical-date',new['date']==old['date'])
 ck(n+'/new-count',len(new['records'])==rec['after'][n])
for p in rec['dossier_pins']:ck('dossier/'+p['path'],sha(ROOT/p['path'])==p['sha256'])
sources=json.loads((ROOT/'docs/design/research/source-support.json').read_text())['records']
for k in ['nassar2022tableformer','nassar2022tableformersupp','lysak2023otsl','libkin2016certain','libkin2016sql']:
 row=next(x for x in sources if x['id']==k);ck(k+'/bytes',sha(ROOT/row['local_path'])==row['sha256']);ck(k+'/limits',bool(row['claims_forbidden']))
for k in ['mccarthy1982','caiani2016','imielinski1984','tamer2010']:
 row=next(x for x in sources if x['id']==k);ck(k+'/still-blocked',row['classification']=='SOURCE_BLOCKED' and not row['claims_allowed'])
review=(OUT/'claim-review.md').read_text()
for token in ['C01–C03','C04','C05','C06–C08','C09','C10','C11','C12','C13–C14','C15–C16','C17','C18','C19','C20','C21','C22','C23–C25','C26','C27–C28','C29','C30–C31','C32','C33','C34–C38','C39–C44']:
 ck('disposition-present/'+token,token in review)
ck('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
result={'passed':all(x['passed'] for x in checks),'checks':checks,'count':len(checks),'interpretation':'Integrity and disposition presence, not automated source-faithfulness certification'}
(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks)}));assert result['passed']
