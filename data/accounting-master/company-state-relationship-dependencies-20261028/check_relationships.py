"""Bounded independent controls for the retained native claim path."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import relationships as rel

ROOT = rel.ROOT
HERE = 'data/accounting-master/company-state-relationship-dependencies-20261028'
PLAN = 'docs/plans/company-state-relationship-dependencies-20261028.md'
INPUT = 'data/accounting-master/company-operation-path-20261023/example.json'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    path = json.loads((ROOT / INPUT).read_text())
    source_path = path['initial_year']['source']['path']
    source = (ROOT / source_path).read_bytes()
    saved = deepcopy(path)
    checks, controls = [], {}
    def check(name, actual, expected):
        checks.append(dict(name=name, passed=actual == expected, actual=rel.wire(actual), expected=rel.wire(expected)))
    def inspect(p):
        return rel.inspect(p, source, rel.native.digest(p))
    def op(p, year, kind, index=0):
        d = [p['initial_year'], *p['continuations']][year]
        return [o for o in d['operations'] if o['kind'] == kind][index]
    result = inspect(path)
    native = result['native_result']
    check('native complete', native['status'], 'complete_conditional')
    check('input retained', result['input'], path)
    check('input immutable', path, saved)
    check('63 supplied events retained', len(result['event_nodes']), 63)
    check('63 distinct year qualified event keys', len({e['id'] for e in result['event_nodes']}), 63)
    check('all events executed', {e['status'] for e in result['event_nodes']}, {'executed'})
    check('all 63 prefix memories', len(result['prefixes']), 63)
    check('14 lifetime claims', len(result['claim_nodes']), 14)
    check('12 creation relations', sum(e['kind']=='creates_claim' for e in result['relation_edges']), 12)
    check('60 named allocations', sum(e['kind']=='settles_claim' for e in result['relation_edges']), 60)
    check('14 zero allocations retained', sum(e.get('is_zero',False) for e in result['relation_edges']), 14)
    check('all 72 claim dependencies retained', len(result['claim_guard_dependencies']), 72)
    check('3 years checked', len(result['year_ends']), 3)
    check('uninspected kinds explicit', result['uninspected_executed_kinds'],
          sorted({'facility_draw','facility_interest','facility_repayment','payroll','plant_addition',
                  'depreciation','interest','tax','dividend','close'}))
    for field in ['real_behavior_evidence','historical_admission','actor_information_admission',
                  'legal_identity_admission','generic_preconditions_complete']:
        check('no unsupported '+field, result[field], False)
    check('no executable reduction', result['executable_reduction'], None)
    for c in result['claim_nodes']:
        check('unresolved identities '+c['id'], [c[k] for k in ['counterparty','legal_instrument','authority']], [None]*3)
        check('lifetime arithmetic '+c['id'], Q(c['recognised'])-Q(c['settled']), Q(c['outstanding']))
    # These expected values are computed from the authored amounts, independently
    # of annual carry code or the inspector's journal comparisons.
    expected = [('55/1','40/1'), ('176/5','10/1'), ('204/5','10/1')]
    for yi, y in enumerate(result['year_ends']):
        ledger_totals = {l: sum((Q(c['outstanding']) for c in y['claims'].values() if c['ledger']==l),Q(0))
                         for l in ['receivable','payable']}
        check('independent year totals '+str(yi), rel.wire(ledger_totals),
              dict(receivable=expected[yi][0],payable=expected[yi][1]))
        check('native complete memory '+str(yi), y['claims'], native['years'][yi]['closing_memory']['claims'])
    final = {c['id']:c for c in result['claim_nodes']}
    check('opening AR lifetime', [final['opening-ar'][k] for k in ['recognised','settled','outstanding']], ['35/1','35/1','0/1'])
    check('first sales claim lifetime', [final['sales-ar-a'][k] for k in ['recognised','settled','outstanding']], ['150/1','150/1','0/1'])
    check('last sales claim lifetime', [final['sales-ar-2027-a'][k] for k in ['recognised','settled','outstanding']], ['204/1','918/5','102/5'])
    # Equal financial reports need not imply equal claim state. Reallocate one
    # unit of the final year's first collection between its two new claims.
    alternative = deepcopy(path)
    allocations = op(alternative,2,'collection')['payload']['allocations']
    allocations[-2]['amount']=rel.wire(Q(allocations[-2]['amount'])+1)
    allocations[-1]['amount']=rel.wire(Q(allocations[-1]['amount'])-1)
    alt = inspect(alternative)
    check('alternative completes', alt['native_result']['status'], 'complete_conditional')
    for yi in range(3):
        a, b = native['years'][yi]['run'], alt['native_result']['years'][yi]['run']
        check('equal aggregate balances '+str(yi), a['closing_balances'], b['closing_balances'])
        check('equal aggregate statements '+str(yi), a['statements'], b['statements'])
        check('equal posted journals '+str(yi), a['journals'], b['journals'])
    alt_claims = {c['id']:c for c in alt['claim_nodes']}
    check('different claim A', alt_claims['sales-ar-2027-a']['outstanding'], '97/5')
    check('different claim B', alt_claims['sales-ar-2027-b']['outstanding'], '107/5')
    check('different relation allocations retained', alt['relation_edges'] != result['relation_edges'], True)
    controls['same_totals_different_claims']=alt
    mutations = [
        ('zero wrong ledger', lambda p: op(p,0,'supplier_payment')['payload']['allocations'][0].update(claim_id='opening-ar'), 'invalid', 'wrong_claim_ledger'),
        ('zero absent claim', lambda p: op(p,0,'supplier_payment')['payload']['allocations'][0].update(claim_id='absent'), 'invalid', 'unrecognised_claim'),
        ('duplicate allocation', lambda p: op(p,0,'collection')['payload']['allocations'].append(deepcopy(op(p,0,'collection')['payload']['allocations'][0])), 'invalid', 'duplicate_allocation'),
        ('over settlement', lambda p: op(p,0,'collection')['payload']['allocations'][0].update(amount='36/1'), 'invalid', 'over_settlement'),
        ('future claim', lambda p: op(p,0,'collection')['payload']['allocations'][0].update(claim_id='sales-ar-2026-a'), 'invalid', 'unrecognised_claim'),
        ('negative allocation', lambda p: op(p,0,'collection')['payload']['allocations'][0].update(amount='-1/1'), 'invalid', 'operation_rational'),
        ('unknown control', lambda p: op(p,0,'delivery')['payload'].update(control_transferred='unknown'), 'unresolved', 'operation_inputs'),
        ('false control', lambda p: op(p,0,'delivery')['payload'].update(control_transferred=False), 'unsupported', 'control_not_transferred_method'),
        ('insufficient inventory', lambda p: op(p,0,'delivery')['payload'].update(units='10000/1'), 'economic_failure', 'inventory_shortfall'),
        ('late duplicate claim', lambda p: op(p,2,'purchase')['payload'].update(claim_id='purchase-ap-a'), 'invalid', 'duplicate_claim'),
    ]
    for name, mutate, status, reason in mutations:
        p = deepcopy(path)
        mutate(p)
        r = inspect(p)
        n = r['native_result']
        stopped = n['years'][-1]['run']
        check(name+' partial', n['status'], 'partial')
        check(name+' refusal status', stopped['status'], status)
        check(name+' refusal reason', stopped['reason'], reason)
        check(name+' preserves all events', len(r['event_nodes']), 63)
        check(name+' exactly one refused event', sum(e['status']=='refused' for e in r['event_nodes']), 1)
        check(name+' no false suffix execution', all(e['status']=='unexecuted' for e in r['event_nodes']
              if e['year']>n['stopped_index']), True)
        if name=='late duplicate claim':
            check('earlier two complete native years unchanged', n['years'][:2], native['years'][:2])
            check('partial preserves lifetime claims', r['year_ends'][-1]['claims'], result['year_ends'][1]['claims'])
        controls[name] = r
    try:
        rel.inspect(path,source,'0'*64)
        refused=False
    except ValueError:
        refused=True
    check('external digest mismatch refused', refused, True)
    corrupted = rel.inspect(path,source+b' ',rel.native.digest(path))
    check('corrupted source no graph', corrupted['relation_graph'], None)
    check('corrupted source status', corrupted['native_result']['years'][0]['run']['reason'], 'source_digest')
    controls['corrupted_source']=corrupted
    unsupported=deepcopy(path)
    unsupported['initial_year']['opening_claims'][0]['counterparty']='invented'
    invalid=inspect(unsupported)
    check('native schema rejects fabricated party field', invalid['native_result']['reason'], 'path_schema')
    check('fabricated party field supplies no graph', invalid['relation_graph'], None)
    controls['fabricated_party_field']=invalid
    def safe(x):
        if isinstance(x,set): return sorted(x)
        if isinstance(x,dict): return {k:safe(v) for k,v in x.items()}
        if isinstance(x,(list,tuple)): return [safe(v) for v in x]
        return rel.wire(x)
    failed=[c for c in checks if not c['passed']]
    files={Path(__file__),ROOT/PLAN,ROOT/INPUT,ROOT/source_path,Path(rel.__file__)}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    # composition is dynamically loaded, so include its module and helpers.
    files.update(Path(m.__file__) for m in [rel.native,rel.native.reports,rel.native.annual_path])
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact rational inspection; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Complete retained authored three-year operation path; all 63 operations and 14 claims',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=HERE+'/result.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,
                      events=len(result['event_nodes']),claims=len(result['claim_nodes']),
                      relations=len(result['relation_edges']),controls=len(controls))
    for name,data in [('inspection',result),('controls',controls),('checks',checks),('run-manifest',manifest),('verification',verification)]:
        (out/(name+'.json')).write_text(json.dumps(safe(data),indent=2)+chr(10))
    for f in [Path(__file__),Path(rel.__file__)]:
        (out/f.name).write_bytes(f.read_bytes())
    print(json.dumps(safe(verification)))
    return bool(failed)


if __name__=='__main__':
    raise SystemExit(main())
