#!/usr/bin/env python3
"""Bounded document diagnostic for the proposed accounting fixtures."""
import hashlib, json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
FIX = ROOT / 'docs/design/proposal/architecture/accounting-fixtures-v1.json'
STD = ROOT / 'docs/design/proposal/methods/standards-fixtures-v1.json'
checks=[]
def ok(name, value):
    checks.append({'id':name,'passed':bool(value)})
    return bool(value)
f=json.loads(FIX.read_text()); s=json.loads(STD.read_text())
ok('schema', f.get('schema_version')=='accdsl.accounting.fixtures.v1')
ok('nonempty_cases', len(f.get('cases',[]))==5)
ok('source_hash', hashlib.sha256(STD.read_bytes()).hexdigest()==f['source_bindings'][0]['sha256_required'])
by={x['id']:x for x in f['cases']}
for cid in ('AC01_A01_eligible_fvtpl','AC02_A02_eligible_amortised_cost'):
    x=by[cid]; e=x['expected']; j=e['journal']
    deb=sum(Decimal(a[1]) for a in j); cred=sum(Decimal(a[2]) for a in j)
    ok(cid+'_balanced', deb==cred)
    delta={}
    for a,d,c in j: delta[a]=delta.get(a,Decimal('0'))+Decimal(d)-Decimal(c)
    ok(cid+'_delta', delta=={k:Decimal(v) for k,v in e['state_delta'].items()})
u=by['AC03_A03_missing_valuation_evidence']['expected']
ok('unresolved_no_write', u['assessment_status']=='unresolved' and u['failure_code']=='TREATMENT_UNRESOLVED' and u['journal']==[] and u['state_delta'] is None and not u['commit'] and u['mathematical_status']=='unresolved' and u['computation_status']=='not_computed')
r=by['AC04_replay_same_identity']['expected']; ok('replay_no_posting', r['receipt_status']=='replayed' and not r['commit'] and not r['additional_posting'])
st=by['AC05_stale_opening_state']['expected']; ok('stale_no_write', st['failure_code']=='STALE_OPENING_STATE' and not st['commit'] and not st['additional_posting'])
out={'schema_version':'accdsl.accounting.contract.check.v1','fixture':str(FIX.relative_to(ROOT)),'checks':checks,'passed':all(x['passed'] for x in checks),'scope':'Document diagnostic only; no runtime or accounting-validity claim'}
print(json.dumps(out,indent=2))
raise SystemExit(0 if out['passed'] else 1)
