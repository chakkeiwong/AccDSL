"""Preserve first fixture bytes and normalize two mathematically equal inputs."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'authored-cases-v2.json').exists()
data=json.loads((OUT/'authored-cases.json').read_text());changed=[]
for c in data['cases']:
    if c['id'] in ('matching-lower-current','matching-higher-current'):
        p=c['request']['data']['periods'][1];old=p['asset_profit_income'];assert old=='1584/121'
        p['asset_profit_income']=str(Q(old));assert p['asset_profit_income']=='144/11'
        changed.append(dict(case=c['id'],old=old,new=p['asset_profit_income'],equal=Q(old)==Q(p['asset_profit_income'])))
(OUT/'authored-cases-v2.json').write_text(json.dumps(data,indent=2)+'\n')
lock=json.loads((OUT/'input-lock.json').read_text())
for item in lock['files']:
    if item['path'].endswith('/authored-cases.json'):
        item.update(path=str((OUT/'authored-cases-v2.json').relative_to(ROOT)),sha256=hashlib.sha256((OUT/'authored-cases-v2.json').read_bytes()).hexdigest())
lock['predecessor']=dict(path=str((OUT/'input-lock.json').relative_to(ROOT)),sha256=hashlib.sha256((OUT/'input-lock.json').read_bytes()).hexdigest())
(OUT/'input-lock-v2.json').write_text(json.dumps(lock,indent=2)+'\n')
(OUT/'fixture-repair.json').write_text(json.dumps(dict(reason='Canonical reduced rational input required; no mathematical target change.',changes=changed),indent=2)+'\n')
print(json.dumps(dict(canonical_input_repairs=len(changed))))
