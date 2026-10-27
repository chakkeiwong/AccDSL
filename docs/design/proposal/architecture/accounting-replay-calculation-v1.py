"""Offline finite calculations for the replay design examples; no runtime API."""
import copy
import hashlib
import json
from pathlib import Path
import platform
import sys
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'docs/design/proposal/architecture'
FIXTURE = BASE / 'accounting-replay-fixtures-v1.json'
checks = []
def check(name, condition):
    checks.append({'id': name, 'passed': bool(condition)})
    if not condition:
        raise AssertionError(name)
def unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError('duplicate key')
        out[key] = value
    return out
def bad_float(value):
    raise ValueError('float/constant outside fixture profile: ' + value)
def digest(kind, value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                     allow_nan=False).encode('ascii')
    return hashlib.sha256(('accdsl.replay.v1/' + kind).encode() + b'\0' + raw).hexdigest()
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path):
    return str(path.relative_to(ROOT))
def money(value):
    check('two decimal input ' + value, isinstance(value, str) and
          format(Decimal(value), '.2f') == value)
    return Decimal(value)

d = json.loads(FIXTURE.read_text(), object_pairs_hook=unique,
               parse_float=bad_float, parse_constant=bad_float)
records = d['records']
def get(ref, kind=None):
    record = records[ref]
    if kind:
        check('record kind ' + ref, record['kind'] == kind)
    return record['content']
input_hashes = {relative(FIXTURE): sha(FIXTURE), relative(Path(__file__).resolve()): sha(Path(__file__))}
for binding in d['source_bindings'] + d['preserved_legacy_files']:
    path = ROOT / binding['path']
    actual = sha(path)
    check('file binding ' + binding['path'], actual == binding['sha256'])
    input_hashes[binding['path']] = actual
for name in ['accounting-replay-contract-v1.md']:
    input_hashes[relative(BASE / name)] = sha(BASE / name)
source = json.loads((ROOT / d['source_bindings'][0]['path']).read_text())
a01 = next(x for x in source['acquisitions'] if x['id'] == 'A01')
check('A01 source arithmetic', (Decimal(a01['price']), Decimal(a01['fair_value']), Decimal(a01['cost'])) == (Decimal('100'), Decimal('100'), Decimal('2')))
register = json.loads((ROOT / d['source_bindings'][1]['path']).read_text())
s9 = next(x for x in register['sources'] if x['id'] == 'S9')
for binding in [s9['pdf'], s9['text']]:
    check('S9 transitive binding ' + binding['path'], sha(ROOT / binding['path']) == binding['sha256'])
for ref, record in records.items():
    check('content digest ' + ref, digest(record['kind'], record['content']) == ref)
    check('ASCII finite encoding ' + ref, json.dumps(record['content'], ensure_ascii=False).isascii())

# Check dependencies without reading authored case expectations.
for ref, record in records.items():
    c = record['content']
    if record['kind'] == 'request':
        for field, kind in [('key','key'),('opening_state','state'),('context','context'),('branch','branch'),('authority','authority'),('method','method'),('evidence','evidence'),('assumptions','assumptions')]:
            get(c[field], kind)
        key, branch, context, opening = (get(c[x]) for x in ['key','branch','context','opening_state'])
        check('request scoped context ' + ref, all(key[k] == branch[k] == context[k] for k in ['entity_id','book_id']) and key['branch_id'] == branch['branch_id'] and opening['context'] == c['context'] and opening['branch'] == c['branch'])
        check('request time ' + ref, c['time']['economic_date'] >= context['annual_period_start'] and c['time']['source_cutoff'] <= c['time']['review_cutoff'])
        check('event version ' + ref, type(c['event']['version']) is int and c['event']['version'] >= 0)
        for field in ['price','fair_value','fee']:
            money(c['event'][field])
    if record['kind'] == 'state':
        get(c['context'], 'context'); get(c['branch'], 'branch')
        check('state balances ' + ref, sum(money(v) for v in c['balances'].values()) == 0)
        check('state version ' + ref, type(c['version']) is int and c['version'] >= 0)
        if c['parent']:
            parent = get(c['parent'], 'state')
            check('state lineage ' + ref, c['version'] == parent['version'] + 1 and c['branch'] == parent['branch'] and c['context'] == parent['context'])

arithmetic = []
for ref, record in records.items():
    if record['kind'] != 'receipt':
        continue
    r = record['content']; q = get(r['request'], 'request'); e = q['event']
    opening = get(r['opening_state'], 'state'); closing = get(r['closing_state'], 'state')
    assessment = get(r['assessment'], 'assessment'); journal = get(r['journal'], 'journal'); delta = get(r['delta'], 'delta')
    check('receipt identity ' + ref, r['key'] == q['key'] and r['request_fingerprint'] == r['request'] and r['status'] == 'committed' and r['commit'] is True and r['opening_state'] == q['opening_state'])
    check('receipt dependencies ' + ref, all(x['request'] == r['request'] for x in [assessment,journal,delta]) and journal['assessment'] == r['assessment'] and all(assessment[x] == q[x] for x in ['authority','method','evidence','assumptions']) and assessment['status'] == 'eligible')
    check('receipt contexts ' + ref, all(x['context'] == q['context'] and x['branch'] == q['branch'] for x in [opening,closing,journal,delta]) and closing['parent'] == r['opening_state'])
    p, f = Decimal(e['price']), Decimal(e['fee'])
    direct = {'asset': Decimal(e['fair_value']), 'cash': -p-f, 'expense': f, 'equity': Decimal(0)}
    aggregate = {a: Decimal(0) for a in opening['balances']}
    for line in journal['lines']:
        aggregate[line['account']] += money(line['debit']) - money(line['credit'])
    check('independent event/journal/delta ' + ref, direct == aggregate == {a:money(v) for a,v in delta['amounts'].items()} and sum(aggregate.values()) == 0)
    check('independent event/closing ' + ref, all(money(closing['balances'][a]) == money(v)+direct[a] for a,v in opening['balances'].items()))
    arithmetic.append({'receipt':ref,'delta':{a:str(v) for a,v in direct.items()},'closing_balances':closing['balances']})

outcomes = []
for case in d['cases']:
    qref = case['request']; q = get(qref, 'request'); key = get(q['key'], 'key')
    before = get(case['before_world'], 'world'); after = copy.deepcopy(before)
    for b, s in before['states'].items():
        check('world branch state ' + b, get(get(s,'state')['branch'],'branch')['branch_id'] == b)
    for k, rref in before['committed_receipts'].items():
        check('world receipt index ' + k, get(rref,'receipt')['key'] == k)
    current = before['states'][key['branch_id']]
    prior = before['committed_receipts'].get(q['key'])
    receipt = None; existing = None; code = None
    if prior:
        if get(prior)['request_fingerprint'] == qref:
            status = 'replayed'; receipt = prior
        else:
            status = 'rejected'; code = 'EVENT_ID_CONFLICT'; existing = prior
    elif current != q['opening_state']:
        status = 'rejected'; code = 'STALE_OPENING_STATE'
    else:
        candidates = [h for h,r in records.items() if r['kind'] == 'receipt' and r['content']['request_fingerprint'] == qref]
        check('unique specified commit receipt ' + case['id'], len(candidates) == 1)
        receipt = candidates[0]; status = 'committed'
        after['states'][key['branch_id']] = get(receipt)['closing_state']
        after['committed_receipts'][q['key']] = receipt
    new = status == 'committed'; r = get(receipt) if receipt else {}
    response = {'status':status,'failure_code':code,'request':qref,'receipt':receipt,'existing_receipt':existing,'observed_state':current,'additional_commit':new,'journal':r.get('journal') if new else None,'delta':r.get('delta') if new else None,'domain_writes':['identity','journal','state','receipt'] if new else [],'submitted_facts':q['event']}
    # Only now compare authored expected output.
    check('derived response ' + case['id'], response == case['expected']['response'])
    check('derived full world ' + case['id'], after == get(case['expected']['after_world'],'world'))
    freshness_first = 'STALE_OPENING_STATE' if current != q['opening_state'] else (code or status)
    outcomes.append({'case':case['id'],'lookup_first':code or status,'freshness_first':freshness_first,'response':response,'after_world_digest':digest('world',after)})
check('retry order discriminates', next(x for x in outcomes if x['case']=='AR02_exact_retry')['freshness_first']=='STALE_OPENING_STATE')
check('source journal matches control', [[l['account'],str(Decimal(l['debit']).normalize()),str(Decimal(l['credit']).normalize())] for l in get(get(d['cases'][0]['expected']['response']['receipt'])['journal'])['lines']] == [[a,str(Decimal(b).normalize()),str(Decimal(c).normalize())] for a,b,c in a01['journal']])
output = Path(sys.argv[1])
report = {'schema_version':'accdsl.accounting.replay.verification.v1','passed':True,'check_count':len(checks),'checks':checks,'derived_outcomes':outcomes,'independent_arithmetic':arithmetic,'input_hashes':input_hashes,'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/accounting-replay-calculation-v1.py '+relative(output.resolve()),'environment':{'python':platform.python_version(),'packages':'standard library only','devices':'No numerical framework or device access; CPU string/Decimal calculation'},'scope':'Finite fixture derivation only; eligibility stipulated; no runtime, accounting validity or prose completeness claim'}
with output.open('x') as f:
    json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'outcomes':[{k:x[k] for k in ['case','lookup_first','freshness_first']} for x in outcomes]}))
