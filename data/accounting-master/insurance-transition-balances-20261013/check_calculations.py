"""Check the scoped source anchors and exact authored transition arithmetic."""
import hashlib
import json
from pathlib import Path

UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

baseline = json.loads((UNIT / 'baseline.json').read_text())
checks = {'source_hash': sha(ROOT / baseline['source']) == baseline['source_sha256']}
pages = json.loads((UNIT / 'source-pages.json').read_text())
for p in pages['pages']:
    checks[f"extract:{p['pdf_page']}"] = sha(ROOT / p['text']) == p['sha256']
anchors = [
    (12, '38', 'represents the unearned profit'),
    (12, '40', 'the liability for remaining coverage comprising'),
    (12, '40', 'the liability for incurred claims'),
    (14, '47', 'being equal to the fulfilment cash flows'),
    (14, '47', 'contractual service margin of the group being zero'),
    (14, '49', 'a loss component of the liability for remaining coverage'),
    (14, '50', 'the liability for remaining coverage, excluding the loss component'),
    (57, 'C4(c)', 'recognise any resulting net difference in equity'),
    (57, 'C5', 'instead of applying paragraph C4(a)'),
    (61, 'C20', 'as the difference between the fair value of a group of insurance contracts'),
    (61, 'C20', 'and the fulfilment cash flows measured at that date'),
    (61, 'C20A', 'the loss-recovery component of the asset for remaining coverage'),
]
for page, paragraph, fragment in anchors:
    text = ' '.join((UNIT / f'source-pages/page-{page}.txt').read_text().split())
    checks[f'anchor:{page}:{paragraph}:{fragment[:20]}'] = fragment in text

# Authored inputs and expected outcomes are fixed by the recorded derivation.
inputs = {'A': {'fcf': 90, 'fair_value': 110, 'old_liability': 105},
          'B': {'fcf': 120, 'fair_value': 100, 'old_liability': 115}}
expected = {'A': (20, 0, 110), 'B': (0, 20, 120)}
groups = {}
for name, x in inputs.items():
    f, v = x['fcf'], x['fair_value']
    c, k = max(v-f, 0), max(f-v, 0)
    l = f+c
    groups[name] = {**x, 'csm': c, 'loss_component_within_liability': k,
                    'new_liability': l, 'equity_change': x['old_liability']-l}
    checks[f'{name}:expected_components'] = (c,k,l) == expected[name]
    checks[f'{name}:signed_difference'] = c-k == v-f and c*k == 0
    checks[f'{name}:liability_decomposition'] = l == f+c == max(f,v)
    checks[f'{name}:equity_change'] = x['old_liability']-l == -5

journals = {
    'A': {'debit': {'old_liability':105, 'opening_equity':5},
          'credit': {'fcf_liability':90, 'csm_liability':20}},
    'B': {'debit': {'old_liability':115, 'opening_equity':5},
          'credit': {'fcf_liability':120}},
}
for name, j in journals.items():
    checks[f'{name}:balanced_entry'] = sum(j['debit'].values()) == sum(j['credit'].values())
    checks[f'{name}:entry_matches_components'] = sum(j['credit'].values()) == groups[name]['new_liability']
checks['B:no_loss_component_credit'] = 'loss_component' not in journals['B']['credit']
old = sum(g['old_liability'] for g in groups.values())
new = sum(g['new_liability'] for g in groups.values())
assets = 500
checks['balance_sheet'] = (old, new, assets-old, assets-new) == (220,230,280,270)
checks['equity_bridge'] = (assets-new)-(assets-old) == sum(g['equity_change'] for g in groups.values()) == -10
f_total = sum(g['fcf'] for g in groups.values())
v_total = sum(g['fair_value'] for g in groups.values())
pooled_liability = f_total + max(v_total-f_total,0)
checks['pooling_counterexample'] = f_total == v_total == pooled_liability == 210 and new-pooled_liability == 20
checks['fair_value_only_rejected'] = groups['B']['fair_value'] == 100 != groups['B']['new_liability']
checks['loss_double_count_rejected'] = groups['B']['fcf']+groups['B']['loss_component_within_liability'] == 140 != groups['B']['new_liability']
for f,v in [(100,99),(100,100),(100,101)]:
    c,k=max(v-f,0),max(f-v,0)
    checks[f'boundary:{f}:{v}'] = c-k==v-f and c*k==0 and f+c==max(f,v)
checks['boundary_expected'] = max(100-100,0) == 0
result = {'scope':'Exact authored conditional example, not runtime execution or an issuer valuation',
          'source_sha256':baseline['source_sha256'], 'source_anchors':anchors,
          'groups':groups, 'journals':journals,
          'balance_sheet':{'assets':assets,'old_liability':old,'new_liability':new,'old_equity':assets-old,'new_equity':assets-new},
          'rejected_pooling':{'pooled_liability':pooled_liability,'liability_understatement':new-pooled_liability},
          'checks':checks,'passed':sum(checks.values()),'failed':[k for k,v in checks.items() if not v]}
(UNIT / 'source-calculation-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed','balance_sheet']}))
raise SystemExit(bool(result['failed']))
